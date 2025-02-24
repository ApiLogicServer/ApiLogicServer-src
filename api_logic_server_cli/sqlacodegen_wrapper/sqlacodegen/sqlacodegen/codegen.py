"""Contains the code generation logic and helper functions."""
from __future__ import unicode_literals, division, print_function, absolute_import

import inspect
import re
import sys, logging
from collections import defaultdict
from importlib import import_module
from inspect import FullArgSpec  # val-311
from keyword import iskeyword

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import (
    Enum, ForeignKeyConstraint, PrimaryKeyConstraint, CheckConstraint, UniqueConstraint, Table,
    Column, Float)
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.types import Boolean, String
from sqlalchemy.util import OrderedDict
import yaml
import datetime

# The generic ARRAY type was introduced in SQLAlchemy 1.1
from api_logic_server_cli.create_from_model.model_creation_services import ModelCreationServices
from api_logic_server_cli.create_from_model.meta_model import Resource, ResourceRelationship, ResourceAttribute

log = logging.getLogger(__name__)

sqlalchemy_2_hack = True
""" exploring migration failures (True) """

sqlalchemy_2_db = True
""" prints / debug stops """


"""
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(message)s')  # lead tag - '%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.propagate = True
"""

try:
    from sqlalchemy import ARRAY
except ImportError:
    from sqlalchemy.dialects.postgresql import ARRAY

# SQLAlchemy 1.3.11+
try:
    from sqlalchemy import Computed
except ImportError:
    Computed = None

# Conditionally import Geoalchemy2 to enable reflection support
try:
    import geoalchemy2  # noqa: F401
except ImportError:
    pass

_re_boolean_check_constraint = re.compile(r"(?:(?:.*?)\.)?(.*?) IN \(0, 1\)")
_re_column_name = re.compile(r'(?:(["`]?)(?:.*)\1\.)?(["`]?)(.*)\2')
_re_enum_check_constraint = re.compile(r"(?:(?:.*?)\.)?(.*?) IN \((.+)\)")
_re_enum_item = re.compile(r"'(.*?)(?<!\\)'")
_re_invalid_identifier = re.compile(r'[^a-zA-Z0-9_]' if sys.version_info[0] < 3 else r'(?u)\W')


class _DummyInflectEngine(object):
    @staticmethod
    def singular_noun(noun):
        return noun


# In SQLAlchemy 0.x, constraint.columns is sometimes a list, on 1.x onwards, always a
# ColumnCollection
def _get_column_names(constraint):
    if isinstance(constraint.columns, list):
        return constraint.columns
    return list(constraint.columns.keys())


def _get_constraint_sort_key(constraint):
    if isinstance(constraint, CheckConstraint):
        return 'C{0}'.format(constraint.sqltext)
    return constraint.__class__.__name__[0] + repr(_get_column_names(constraint))


class ImportCollector(OrderedDict):
    """ called for each col to collect all the imports """

    def add_import(self, obj):
        type_ = type(obj) if not isinstance(obj, type) else obj
        """ eg., column.type, or sqlalchemy.sql.schema.Column """

        pkgname = type_.__module__
        """ eg, sqlalchemy.sql.schema, then set to sqlalchemy """

        # The column types have already been adapted towards generic types if possible, so if this
        # is still a vendor specific type (e.g., MySQL INTEGER) be sure to use that rather than the
        # generic sqlalchemy type as it might have different constructor parameters.
        if pkgname.startswith('sqlalchemy.dialects.'):
            dialect_pkgname = '.'.join(pkgname.split('.')[0:3])
            dialect_pkg = import_module(dialect_pkgname)

            if type_.__name__ in dialect_pkg.__all__:
                pkgname = dialect_pkgname
        else:
            if sqlalchemy_2_hack:
                pkgname = "sqlalchemy"
                if type_.__name__.startswith("Null"):
                    pkgname = 'sqlalchemy.sql.sqltypes'
                if type_.__name__.startswith("Null"):  # troublemakes: Double, NullType
                    if sqlalchemy_2_db == True:
                        debug_stop = f'Debug Stop: ImportCollector - target type_name: {type_.__name__}'
            else:  # FIXME HORRID HACK commented out: sqlalchemy.__all__ not in SQLAlchemy2
                """
                in SQLAlchemy 1.4, sqlalchemy.__all__ contained: 
                    ['ARRAY', 'BIGINT', 'BINARY', 'BLANK_SCHEMA', 'BLOB', 'BOOLEAN', 
                    'BigInteger', 'Boolean', 'CHAR', 'CLOB', 'CheckConstraint', 
                    'Column', 'ColumnDefault', 'Computed', 'Constraint', 
                    'DATE', 'DATETIME', 'DDL', 'DECIMAL', 'Date', 'DateTime', 
                    'DefaultClause', 'Enum', 'FLOAT', 'FetchedValue', 'Float', 
                    'ForeignKey', 'ForeignKeyConstraint', 'INT', 'INTEGER', 
                    'Identity', 'Index', 'Integer', 'Interval'...]
                type_.__module__ is sqlalchemy.sql.sqltypes
                """
                pkgname = 'sqlalchemy' if type_.__name__ in sqlalchemy.__all__ else type_.__module__
        type_name = type_.__name__
        if type_name == "CHAR":  
            # render_column_type() uses String for CHAR (e.g., oracle hr.countries)
            self.add_literal_import("sqlalchemy", 'String')   # note: not pkgname
            debug_stop = "target type"
        self.add_literal_import(pkgname, type_name)  # (sqlalchemy, Column | Integer | String...)

    def add_literal_import(self, pkgname, name):
        names = self.setdefault(pkgname, set())
        names.add(name)


class Model(object):

    def __init__(self, table):
        super(Model, self).__init__()
        self.table = table
        self.schema = table.schema
        global code_generator

        bind = code_generator.model_creation_services.session.bind

        # Adapt column types to the most reasonable generic types (ie. VARCHAR -> String)
        for column in table.columns:
            try:
                if table.name == "OrderDetail" and column.name == "Discount":
                    debug_stop = f'Model.__init__ target column -- Float in GA/RC2, Double in Gen'
                column.type = self._get_adapted_type(column.type, bind)  # SQLAlchemy2 (was column.table.bind)
            except Exception as e:
                # remains unchanged, eg. NullType()
                if "sqlite_sequence" not in format(column):
                    print(f"#Failed to get col type for {format(column)} - {column.type}")

    def __str__(self):
        return f'Model for table: {self.table} (in schema: {self.schema})'


    def _get_adapted_type(self, coltype, bind):
        """

        Uses dialect to compute SQLAlchemy type (e.g, String, not VARCHAR, for sqlite)

        Args:
            coltype (_type_): database type
            bind (_type_): e.g, code_generator.model_creation_services.session.bind

        Returns:
            _type_: SQLAlchemy type
        """
        compiled_type = coltype.compile(bind.dialect)  # OrderDetai.Discount: FLOAT (not DOUBLE); coltype is DOUBLE
        if compiled_type == "DOUBLE":
            if sqlalchemy_2_db == True:
                debug_stop = "Debug stop - _get_adapted_type, target compiled_type"
        for supercls in coltype.__class__.__mro__:
            if not supercls.__name__.startswith('_') and hasattr(supercls, '__visit_name__'):
                # Hack to fix adaptation of the Enum class which is broken since SQLAlchemy 1.2
                kw = {}
                if supercls is Enum:
                    kw['name'] = coltype.name

                try:
                    new_coltype = coltype.adapt(supercls)
                except TypeError:
                    # If the adaptation fails, don't try again
                    break

                for key, value in kw.items():
                    setattr(new_coltype, key, value)

                if isinstance(coltype, ARRAY):
                    new_coltype.item_type = self._get_adapted_type(new_coltype.item_type, bind)

                try:
                    # If the adapted column type does not render the same as the original, don't
                    # substitute it
                    if new_coltype.compile(bind.dialect) != compiled_type:
                        # Make an exception to the rule for Float and arrays of Float, since at
                        # least on PostgreSQL, Float can accurately represent both REAL and
                        # DOUBLE_PRECISION
                        if not isinstance(new_coltype, Float) and \
                           not (isinstance(new_coltype, ARRAY) and
                                isinstance(new_coltype.item_type, Float)):
                            break
                except sqlalchemy.exc.CompileError:
                    # If the adapted column type can't be compiled, don't substitute it
                    break

                # Stop on the first valid non-uppercase column type class
                coltype = new_coltype
                if supercls.__name__ != supercls.__name__.upper():
                    break
        if coltype == "NullType":  # troublemakers: Double(), NullType
            if sqlalchemy_2_db == True:
                debug_stop = "Debug stop - _get_adapted_type, target returned coltype"
        return coltype

    def add_imports(self, collector):
        if self.table.columns:
            collector.add_import(Column)

        for column in self.table.columns:
            if self.table.name == "productlines" and column.name == "image":
                if sqlalchemy_2_db:
                    debug_stop = f'add_imports - target column stop - {column.type}'
            if self.table.name == "countries" and column.name == "country_id":
                if sqlalchemy_2_db:
                    debug_stop = f'add_imports - target column stop - {column.type}'
            collector.add_import(column.type)
            if column.server_default:
                if Computed and isinstance(column.server_default, Computed):
                    collector.add_literal_import('sqlalchemy', 'Computed')
                else:
                    collector.add_literal_import('sqlalchemy', 'text')

            if isinstance(column.type, ARRAY):
                collector.add_import(column.type.item_type.__class__)

        for constraint in sorted(self.table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, ForeignKeyConstraint):
                if len(constraint.columns) > 1:
                    collector.add_literal_import('sqlalchemy', 'ForeignKeyConstraint')
                else:
                    collector.add_literal_import('sqlalchemy', 'ForeignKey')
            elif isinstance(constraint, UniqueConstraint):
                if len(constraint.columns) > 1:
                    collector.add_literal_import('sqlalchemy', 'UniqueConstraint')
            elif not isinstance(constraint, PrimaryKeyConstraint):
                collector.add_import(constraint)

        for index in self.table.indexes:
            if len(index.columns) > 1:
                collector.add_import(index)

    @staticmethod
    def _convert_to_valid_identifier(name):
        assert name, 'Identifier cannot be empty'
        if name[0].isdigit() or iskeyword(name):
            name = '_' + name
        elif name == 'metadata':
            name = 'metadata_'
        name = name.replace("$", "_S_")   # ApiLogicServer valid name fixes for superclass version (why override?)
        name = name.replace(" ", "_")
        name = name.replace("+", "_")
        name = name.replace("-", "_")

        result = _re_invalid_identifier.sub('_', name)
        return result


class ModelTable(Model):
    def __init__(self, table):
        super(ModelTable, self).__init__(table)
        self.name = self._convert_to_valid_identifier(table.name)

    def add_imports(self, collector):
        super(ModelTable, self).add_imports(collector)
        try:
            collector.add_import(Table)
        except Exception as exc:
            print("Failed to add imports {}".format(collector))


class ModelClass(Model):
    parent_name = 'Base'

    def __init__(self, table, association_tables, inflect_engine, detect_joined):
        super(ModelClass, self).__init__(table)
        self.name = self._tablename_to_classname(table.name, inflect_engine)
        self.children = []
        self.attributes = OrderedDict()
        self.foreign_key_relationships = list()
        self.rendered_model = ""                # ApiLogicServer
        self.rendered_child_relationships = ""
        """ child relns for this model (eg, OrderList accessor for Customer) """
        self.rendered_parent_relationships = ""
        """ parent relns for this model (eg, Customer accessor for Order) """
        self.rendered_model_relationships = ""  # appended at end ( render() )
        """ child relns for this model - appended during render() REMOVE ME """

        # Assign attribute names for columns
        for column in table.columns:
            self._add_attribute(column.name, column)

        # Add many-to-one relationships (to parent)
        pk_column_names = set(col.name for col in table.primary_key.columns)
        parent_accessors = {}
        """ dict of parent_table, current count (0, 1, 2...   >1 ==> multi-reln) """
        if self.name in ["Flight", "QtrTotal", "StressBinaryDouble", "STRESSAllChar"]:
            # table name is 'stress_binary_double', should match Oracle STRESS_BINARY_DOUBLE
            # table name is 'STRESS_AllChars', matches Oracle STRESS_AllChars
            debug_stop = "nice breakpoint for class names"
        for constraint in sorted(table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, ForeignKeyConstraint):  # drive from the child side
                target_cls = self._tablename_to_classname(constraint.elements[0].column.table.name,
                                                          inflect_engine)
                this_included = code_generator.is_table_included(self.table.name)
                target_included = code_generator.is_table_included(constraint.elements[0].column.table.name)
                if (detect_joined and self.parent_name == 'Base' and set(_get_column_names(constraint)) == pk_column_names):
                    self.parent_name = target_cls  # evidently not called for ApiLogicServer
                    log.debug(f"Foreign Key is Primary Key: {self.name}")
                    self.parent_name = 'Base'  # ApiLogicServer - not sub-table, process anyway
                multi_reln_count = 0
                if target_cls in parent_accessors:
                    multi_reln_count = parent_accessors[target_cls] + 1
                    parent_accessors.update({target_cls: multi_reln_count})
                else:
                    parent_accessors[target_cls] = multi_reln_count
                if self.name == 'QtrTotal' and target_cls == 'YrTotal':
                    debug_stop = "interesting breakpoint"
                if self.name == 'Flight' and target_cls == 'Airport':
                    debug_stop = "interesting breakpoint"
                relationship_ = ManyToOneRelationship(self.name, target_cls, constraint,
                                                    inflect_engine, multi_reln_count)
                if this_included and target_included:
                    self._add_attribute(relationship_.preferred_name, relationship_)
                else:
                    log.debug(f"Parent Relationship excluded: {relationship_.preferred_name}")  # never occurs?

        # Add many-to-many relationships
        for association_table in association_tables:
            fk_constraints = [c for c in association_table.constraints
                              if isinstance(c, ForeignKeyConstraint)]
            fk_constraints.sort(key=_get_constraint_sort_key)
            target_cls = self._tablename_to_classname(
                fk_constraints[1].elements[0].column.table.name, inflect_engine)
            relationship_ = ManyToManyRelationship(self.name, target_cls, association_table)
            self._add_attribute(relationship_.preferred_name, relationship_)

    @classmethod
    def _tablename_to_classname(cls, tablename, inflect_engine):
        """
        camel-case and singlularize, with provisions for reserved word (Date) and collisions (Dates & _Dates)
        """
        tablename = cls._convert_to_valid_identifier(tablename)
        if tablename in ["Dates", "dates", "Column", "column"]:  # ApiLogicServer
            tablename = tablename + "Cls"
        camel_case_name = ''.join(part[:1].upper() + part[1:] for part in tablename.split('_'))
        if camel_case_name in ["Dates"]:
            camel_case_name = camel_case_name + "_Classs"
        result = inflect_engine.singular_noun(camel_case_name) or camel_case_name
        if use_inflection := True:  # better support for Address (not Addres)
            import inflection  # inflect.engine().singular_noun() -> Addres
            result = inflection.singularize(camel_case_name)
            if tablename in ["address"]:  # ApiLogicServer
                debug_stop = "nice breakpoint"
            pass

        if tablename in ["classes"]:  # ApiLogicServer
            debug_stop = "nice breakpoint"
        if result == "Class":   # ApiLogicServer
            result = "Class"    # FIXME - workaround for class name... why not "Classs"?
        if result == "CategoryTableNameTest":  # ApiLogicServer
            result = "Category"
        return result

    @staticmethod
    def _convert_to_valid_identifier(name: str) -> str:  # TODO review
        """ 
        fix name for special chars ($ +-), and iskeyword()

        Args:
            name (str): actual attr name

        Returns:
            str: name fixed for special chars ($ +-), and iskeyword()
        """
        assert name, "Identifier cannot be empty"
        if name[0].isdigit() or iskeyword(name):
            name = "_" + name
        elif name == "metadata":
            name = "metadata_"
        name = name.replace("$", "_S_")   # ApiLogicServer valid name fixes, ModelClass version
        name = name.replace(" ", "_")
        name = name.replace("+", "_")
        name = name.replace("-", "_")

        result = _re_invalid_identifier.sub("_", name)
        return result

    def _add_attribute(self, attrname, value):
        """ add table column AND reln accessors to attributes

        disambiguate relationship accessor names (append tablename with 1, 2...)

        attributes are from sqlalchemy, contain things like server_default for pg autonums 
        """
        attrname = tempname = self._convert_to_valid_identifier(attrname)
        if self.name in ["Employee", "CharacterClass"] and attrname in ["employee_id", "_class"]:
            debug_stop = "nice breakpoint"
        counter = 1
        while tempname in self.attributes:
            tempname = attrname + str(counter)
            counter += 1

        self.attributes[tempname] = value
        return tempname

    def add_imports(self, collector):
        super(ModelClass, self).add_imports(collector)

        if any(isinstance(value, Relationship) for value in self.attributes.values()):
            collector.add_literal_import('sqlalchemy.orm', 'relationship')

        for child in self.children:
            child.add_imports(collector)


class Relationship(object):
    def __init__(self, source_cls, target_cls):
        super(Relationship, self).__init__()
        self.source_cls = source_cls
        """ for API Logic Server, the child class """

        self.target_cls = target_cls
        """ for API Logic Server, the parent class """
        self.kwargs = OrderedDict()


class ManyToOneRelationship(Relationship):

    def __init__(self, child_cls: str, parent_cls: str, constraint, inflect_engine, multi_reln_count):
        """
        compute many to 1 class, assigning accessor names; tricky 
        
        * for multi_relns between same 2 tables
        * tables with reserved names (e/g., DND Class table)
        
        Note: 
        * child_cls is the child    (self.source_cls)
        * parent_cls is the parent  (self.target_cls)
        """
        super(ManyToOneRelationship, self).__init__(child_cls, parent_cls)

        if child_cls in ['Flight', 'Employee', 'TabGroup', 'CharacterClass'] and \
            parent_cls in ['Airport', 'Department', 'Entity', 'Class']:
            debug_stop = "interesting breakpoint"  #  Launch config 8...   -- Create servers/airport from MODEL
        column_names = _get_column_names(constraint)
        colname = column_names[0]
        tablename = constraint.elements[0].column.table.name
        self.foreign_key_constraint = constraint

        parent_accessor_from_fk = False
        if len(column_names) > 1 :      # multi-column - use tablename
            self.preferred_name = inflect_engine.singular_noun(tablename) or tablename
        else:                           # single column - use column name but without '_id'
            if ( colname.endswith('_id') or colname.endswith('_Id') ):  # eg arrival_airport_id
                self.preferred_name = colname[:-3]
                parent_accessor_from_fk = True
                pass  # TODO - alert: can "lowercase" parent accessor (see classic models employee )
            elif ( colname.endswith('id') or colname.endswith('Id') ):  # eg WorksForDepartmentId
                self.preferred_name = colname[:-2]
                parent_accessor_from_fk = True
            else:
                self.preferred_name = inflect_engine.singular_noun(tablename) or tablename
            # TODO - consider using the target class name as the preferred name (lower case fk -> a_child.parent)

        
        # Add uselist=False to One-to-One relationships
        if any(isinstance(c, (PrimaryKeyConstraint, UniqueConstraint)) and
               set(col.name for col in c.columns) == set(column_names)
               for c in constraint.table.constraints):
            self.kwargs['uselist'] = 'False'

        # Handle self referential relationships
        if child_cls == parent_cls:
            # self.preferred_name = 'parent' if not colname.endswith('_id') else colname[:-3]
            if colname.endswith("id") or colname.endswith("Id"):
                self.preferred_name = colname[:-2]
            else:
                self.preferred_name = "parent"  # hmm, why not just table name
                self.preferred_name = self.target_cls  # FIXME why was "parent", (for Order)
            pk_col_names = [col.name for col in constraint.table.primary_key]
            self.kwargs['remote_side'] = '[{0}]'.format(', '.join(pk_col_names))
        
        self.parent_accessor_name = self.preferred_name
        """ parent accessor (typically parent (parent_cls)) """
        # assert self.target_cls == self.preferred_name, "preferred name <> parent"

        # avoid collision if fkname = parent table name
        if child_cls == 'Order':
            log.debug("Special case: avoid collision if fkname = parent table name")
            debug_stop = "interesting breakpoint"
        if child_cls == 'Order' and parent_cls == 'Customer':   # test database: tests/test_databases/sqlite-databases/nw-fk-getter-collision.sqlite
            log.debug("Special case: avoid collision if fkname = parent table name")
            debug_stop = "interesting breakpoint"
        for each_col in constraint.table.columns:
            if each_col.name == self.parent_accessor_name:
                self.parent_accessor_name = self.parent_accessor_name + '1'

        self.child_accessor_name = self.source_cls + "List"
        """ child accessor (typically child (target_class) + "List") """

        do_use_fk_for_name = False  # name from fk column name, even if not multi-reln (disabled for compatibility)
        if False and parent_accessor_from_fk:
            pass  # parent_accessor_name is already unique (eg, Employee.WorksForDepartment)
            self.child_accessor_name += str(multi_reln_count)
            if self.parent_accessor_name.endswith(self.target_cls):
                self.child_accessor_name  = \
                    self.parent_accessor_name[0:len(self.target_cls)-2] + self.source_cls + "List"
                pass  # (eg, Department.WorksForEmployeeList)

        if multi_reln_count > 0:  # disambiguate multi_reln between same 2 tables (tricky!)
            # key cases are nw (Dept/Employee) and ai/airport (Flight/Airport) and app_model_editor (Entity/TabGroup)
            if parent_accessor_from_fk:
                pass  # parent_accessor_name is already unique (eg, Employee.WorksForDepartment)
                self.child_accessor_name += str(multi_reln_count)
                reln_prefix = self.parent_accessor_name  # eg, airport_4 - origin
                parent_accessor_name_lower = self.parent_accessor_name.lower()
                target_cls_lower = self.target_cls.lower()  # bugfix - airport vs Airport
                if parent_accessor_name_lower.endswith(target_cls_lower):
                    # eg, departure_airport and airport     --> child_accessor_name = departureFlightList
                    # eg, origin and airport [4]   FAILS    --> child_accessor_name = FlightList1
                    # eg, worksfordepartment and department --> child_accessor_name = WorksForEmployeeList
                    reln_prefix = self.parent_accessor_name[0: \
                                            len(parent_accessor_name_lower) - len(self.target_cls)]
                    if reln_prefix.endswith("_"):
                        reln_prefix = reln_prefix[0: len(reln_prefix)-1]
                self.child_accessor_name  = reln_prefix + self.source_cls + "List"
                # if self.parent_accessor_name.endswith(self.target_cls):
                #     self.child_accessor_name  = \
                #         self.parent_accessor_name[0:len(self.target_cls)-2] + self.source_cls + "List"
                #     pass  # (eg, Department.WorksForEmployeeList)
            else:
                self.parent_accessor_name += str(multi_reln_count)  # (Entity/TabGroup)??
                self.child_accessor_name += str(multi_reln_count)
        # If the two tables share more than one foreign key constraint,
        # SQLAlchemy needs an explicit primaryjoin to figure out which column(s) to join with
        common_fk_constraints = self.get_common_fk_constraints(
            constraint.table, constraint.elements[0].column.table)
        if len(common_fk_constraints) > 1:
            self.kwargs['primaryjoin'] = "'{0}.{1} == {2}.{3}'".format(
                child_cls, column_names[0], parent_cls, constraint.elements[0].column.name)
            # eg, 'Employee.OnLoanDepartmentId == Department.Id'
            # and, for SQLAlchemy 2, neds foreign_keys: foreign_keys='[Employee.OnLoanDepartmentId]'
            foreign_keys = "'["
            for each_column_name in column_names:
                foreign_keys += child_cls + "." + each_column_name + ", "
            self.kwargs['foreign_keys'] = foreign_keys[0 : len(foreign_keys)-2] + "]'"
            pass
        parent_accessor_name_valid_id = ModelClass._convert_to_valid_identifier(self.parent_accessor_name)
        if parent_accessor_name_valid_id != self.parent_accessor_name:
            self.parent_accessor_name = parent_accessor_name_valid_id  # unusual (DND - DND CharacterClass)
        if self.parent_accessor_name in ["user_", "class", "class_"]:
            debug_stop = "interesting breakpoint"   # DND CharacterClass renders attr as _class (reserved word)


    @staticmethod
    def get_common_fk_constraints(table1, table2):
        """Returns a set of foreign key constraints the two tables have against each other."""
        c1 = set(c for c in table1.constraints if isinstance(c, ForeignKeyConstraint) and
                 c.elements[0].column.table == table2)
        c2 = set(c for c in table2.constraints if isinstance(c, ForeignKeyConstraint) and
                 c.elements[0].column.table == table1)
        return c1.union(c2)


class ManyToManyRelationship(Relationship):
    def __init__(self, source_cls, target_cls, assocation_table):
        super(ManyToManyRelationship, self).__init__(source_cls, target_cls)

        prefix = (assocation_table.schema + '.') if assocation_table.schema else ''
        self.kwargs['secondary'] = repr(prefix + assocation_table.name)
        constraints = [c for c in assocation_table.constraints
                       if isinstance(c, ForeignKeyConstraint)]
        constraints.sort(key=_get_constraint_sort_key)
        colname = _get_column_names(constraints[1])[0]
        tablename = constraints[1].elements[0].column.table.name
        self.preferred_name = tablename if not colname.endswith('_id') else colname[:-3] + 's'

        # Handle self referential relationships
        if source_cls == target_cls:
            self.preferred_name = 'parents' if not colname.endswith('_id') else colname[:-3] + 's'
            pri_pairs = zip(_get_column_names(constraints[0]), constraints[0].elements)
            sec_pairs = zip(_get_column_names(constraints[1]), constraints[1].elements)
            pri_joins = ['{0}.{1} == {2}.c.{3}'.format(source_cls, elem.column.name,
                                                       assocation_table.name, col)
                         for col, elem in pri_pairs]
            sec_joins = ['{0}.{1} == {2}.c.{3}'.format(target_cls, elem.column.name,
                                                       assocation_table.name, col)
                         for col, elem in sec_pairs]
            self.kwargs['primaryjoin'] = (
                repr('and_({0})'.format(', '.join(pri_joins)))
                if len(pri_joins) > 1 else repr(pri_joins[0]))
            self.kwargs['secondaryjoin'] = (
                repr('and_({0})'.format(', '.join(sec_joins)))
                if len(sec_joins) > 1 else repr(sec_joins[0]))

code_generator = None  # type: CodeGenerator
""" Model needs to access state via this global, eg, included/excluded tables """

class CodeGenerator(object):
    template = """\
# coding: utf-8
{imports}

{metadata_declarations}


{models}"""

    def is_table_included(self, table_name: str) -> bool:
        """

        Determines table included per self.include_tables / exclude tables.

        See Run Config: Table Filters Tests

        Args:
            table_name (str): _description_

        Returns:
            bool: True means included
        """
        table_inclusion_db = False
        if self.include_tables is None:  # first time initialization
            include_tables_dict = {"include": [], "exclude": []}
            if self.model_creation_services.project.include_tables != "":
                with open(self.model_creation_services.project.include_tables,'rt') as f:  # 
                    include_tables_dict = yaml.safe_load(f.read())
                    f.close()
                log.debug(f"include_tables specified: \n{include_tables_dict}\n")  # {'include': ['I*', 'J', 'X*'], 'exclude': ['X1']}

            # https://stackoverflow.com/questions/3040716/python-elegant-way-to-check-if-at-least-one-regex-in-list-matches-a-string
            # https://www.w3schools.com/python/trypython.asp?filename=demo_regex
            # ApiLogicServer create --project_name=table_filters_tests --db_url=table_filters_tests --include_tables=../table_filters_tests.yml
            self.include_tables = include_tables_dict["include"]  \
                if "include" in include_tables_dict else ['.*']         # ['I.*', 'J', 'X.*']
            if self.include_tables is None:
                self.include_tables = ['.*']
            self.include_regex = "(" + ")|(".join(self.include_tables) + ")"  # include_regex: (I.*)|(J)|(X.*)
            self.include_regex_list = map(re.compile, self.include_tables)
            self.exclude_tables = include_tables_dict["exclude"] \
                if "exclude" in include_tables_dict else ['a^'] 
            if self.exclude_tables is None:
                self.exclude_tables = ['a^']
            self.exclude_regex = "(" + ")|(".join(self.exclude_tables) + ")"
            if self.model_creation_services.project.include_tables != "":
                if table_inclusion_db:
                    log.debug(f"include_regex: {self.include_regex}")
                    log.debug(f"exclude_regex: {self.exclude_regex}\n")
                    log.debug(f"Test Tables: I, I1, J, X, X1, Y\n")

        table_included = True
        if self.model_creation_services.project.bind_key == "authentication":
            if table_inclusion_db:
                log.debug(f".. authentication always included")
        else:
            if len(self.include_tables) == 0:
                if table_inclusion_db:
                    log.debug(f"All tables included: {table_name}")
            else:
                if re.match(self.include_regex, table_name):
                    if table_inclusion_db:
                        log.debug(f"table included: {table_name}")
                else:
                    if table_inclusion_db:
                        log.debug(f"table excluded: {table_name}")
                    table_included = False
            if not table_included:
                if table_inclusion_db:
                    log.debug(f".. skipping exclusions")
            else:
                if len(self.exclude_tables) == 0:
                    if table_inclusion_db:
                        log.debug(f"No tables excluded: {table_name}")
                else:
                    if re.match(self.exclude_regex, table_name):
                        if table_inclusion_db:
                            log.debug(f"table excluded: {table_name}")
                        table_included = False
                    else:
                        if table_inclusion_db:
                            log.debug(f"table not excluded: {table_name}")
        return table_included


    def table_has_primary_key(self, table) -> bool:
        """_summary_

        Args:
            table (_type_): SQLAlchemy table

        Returns:
            bool: if has pkey AND table.primary_key.columns > 0
        """
        if table.primary_key is None:
            return False
        return len(table.primary_key.columns) > 0
    

    def is_model_not_table(self, table, association_tables, noclasses) -> bool:
        """

        Determine whether to create table (no api, no rules, no admin) or class

        Test with Run Config: unique_yes, and verify...

        Table               Result

        KeyTest_unique      Class
        NoKey_no_unique     Table
        unique_col_no_key   Class
        unique_no_key_alt   Class             
        unique_with_key     Class

        users, user_notes, SampleDBVersion

        Args:
            table (_type_): table class instance
            has_unique_constraint (bool): 
            association_tables (_type_): set of association tables
            noclasses (_type_): _description_

        Returns:
            _type_: _description_
        """

        if noclasses:  # not sure what this is
            log.debug(f'\t\t .. .. .. ..Create {table.name} as table, because noclasses')
            return False
        if table.name in association_tables:
            log.debug(f'\t\t .. .. .. ..Create {table.name} as table, because table.name in association_tables')
            return False
        
        table_name = table.name + ""
        test_classes = ['KeyTest_unique', 'unique_no_key_alt', 'NoKey_no_unique', 'unique_col_no_key', 'unique_with_key']
        if table_name in test_classes:
            debug_stop = "good breakpoint"  # table.indexes

        if self.table_has_primary_key(table):
            return True  # normal path

        has_unique_constraint = False
        for each_constraint in table.constraints:
            if isinstance(each_constraint, sqlalchemy.sql.schema.UniqueConstraint):
                has_unique_constraint = True  # eg, ??
                break
            if isinstance(each_constraint, sqlalchemy.sql.schema.PrimaryKeyConstraint):  # FIXME same instance?
                # has_unique_constraint = True  # eg, KeyTest_unique
                pkey_columns = len(each_constraint.columns)
                pass  # eg, KeyTest_unique
        
        for each_index in table.indexes:
            if each_index.unique == 1:
                has_unique_constraint = True
                break
            else:
                debug_stop = "found non-unique index"
        
        if has_unique_constraint:    # notset 0, debug 10, info 20, warn 30, error 40, critical 50
            if self.model_creation_services.project.infer_primary_key:
                log.warn(f'\t\t .. .. .. ..Create {table.name} as class (no primary_key, but --infer_primary_key')
                return True 
            else:
                log.warn(f'\t\t .. .. .. ..Create {table.name} as table, because no primary key; has unique key, but --infer_primary_key is not set')
                return False

        log.warn(f"\t\t .. .. .. ..Create {table.name} as table, because no Unique Constraint   ")
        return False


    def __init__(self, metadata, noindexes=False, noconstraints=False, nojoined=False,
                 noinflect=False, noclasses=False, model_creation_services = None,
                 indentation='    ', model_separator='\n\n',
                 ignored_tables=('alembic_version', 'migrate_version'), 
                 table_model=ModelTable,
                 class_model=ModelClass,  
                 template=None, nocomments=False):
        """
            ApiLogicServer sqlacodegen_wrapper invokes this as follows;

                capture = StringIO()  # generate and return the model
                generator = CodeGenerator(metadata, args.noindexes, args.noconstraints,
                              args.nojoined, args.noinflect, args.noclasses, 
                              args.model_creation_services)
                args.model_creation_services.metadata = generator.metadata
                generator.render(capture)  # generates (preliminary) models as memstring
                models_py = capture.getvalue()

        """
        super(CodeGenerator, self).__init__()
        global code_generator
        """ instance of CodeGenerator - access to model_creation_services, meta etc """
        code_generator = self
        self.metadata = metadata
        """ SQLAlchemy metadata """
        self.noindexes = noindexes
        self.noconstraints = noconstraints
        self.nojoined = nojoined
        """ not used by API Logic Server """
        self.noinflect = noinflect
        self.noclasses = noclasses
        self.model_creation_services = model_creation_services  # type: ModelCreationServices
        self.generate_relationships_on = "parent"  # "child"
        """ FORMERLY, relns were genned ONLY on parent (== 'parent') """
        self.indentation = indentation
        self.model_separator = model_separator
        self.ignored_tables = ignored_tables
        self.table_model = table_model
        self.class_model = class_model
        """ class (not instance) of ModelClass [defaulted for ApiLogicServer] """
        self.nocomments = nocomments
        self.children_map = dict()
        """ key is table name, value is list of (parent-role-name, child-role-name, relationship) ApiLogicServer """
        self.parents_map = dict()
        """ key is table name, value is list of (parent-role-name, child-role-name, relationship) ApiLogicServer """

        self.include_tables = None  # regex of tables included
        self.exclude_tables = None  # excluded

        self.inflect_engine = self.create_inflect_engine()

        if template:
            self.template = template

        # Pick association tables from the metadata into their own set, don't process them normally
        links = defaultdict(lambda: [])
        association_tables = set()
        skip_association_table = True
        for table in metadata.tables.values():
            # Link tables have exactly two foreign key constraints and all columns are involved in
            # them
            fk_constraints = [constr for constr in table.constraints
                              if isinstance(constr, ForeignKeyConstraint)]
            if len(fk_constraints) == 2 and all(col.foreign_keys for col in table.columns):
                if skip_association_table:  # Chinook playlist tracks, SqlSvr, Postgres Emp Territories
                    debug_str = f'skipping associate table: {table.name}'
                    debug_str += "... treated as normal table, with automatic joins"
                else:
                    association_tables.add(table.name)
                    tablename = sorted(
                        fk_constraints, key=_get_constraint_sort_key)[0].elements[0].column.table.name
                    links[tablename].append(table)

        # Iterate through the tables and create model classes when possible
        self.models = []
        self.collector = ImportCollector()
        """ collect all the data types used in the models for import generation """
        self.classes = {}
        for table in metadata.sorted_tables:
            # Support for Alembic and sqlalchemy-migrate -- never expose the schema version tables
            if table.name in self.ignored_tables:
                continue
            
            if table.name in ['ProductDetails_V']:
                debug_stop = 'nice breakpoint'
                
            table_included = self.is_table_included(table_name= table.name)
            if not table_included:
                log.debug(f"====> table skipped: {table.name}")
                continue

            """
            if any(regex.match(table.name) for regex in self.include_regex_list):
                log.debug(f"list table included: {table.name}")
            else:
                log.debug(f"list table excluded: {table.name}")
            """

            if noindexes:
                table.indexes.clear()

            if noconstraints:
                table.constraints = {table.primary_key}
                table.foreign_keys.clear()
                for col in table.columns:
                    col.foreign_keys.clear()
            else:
                # Detect check constraints for boolean and enum columns
                for constraint in table.constraints.copy():
                    if isinstance(constraint, CheckConstraint):
                        sqltext = self._get_compiled_expression(constraint.sqltext)

                        # Turn any integer-like column with a CheckConstraint like
                        # "column IN (0, 1)" into a Boolean
                        match = _re_boolean_check_constraint.match(sqltext)
                        if match:
                            colname = _re_column_name.match(match.group(1)).group(3)
                            table.constraints.remove(constraint)
                            table.c[colname].type = Boolean()
                            continue

                        # Turn any string-type column with a CheckConstraint like
                        # "column IN (...)" into an Enum
                        match = _re_enum_check_constraint.match(sqltext)
                        if match:
                            colname = _re_column_name.match(match.group(1)).group(3)
                            items = match.group(2)
                            if isinstance(table.c[colname].type, String):
                                table.constraints.remove(constraint)
                                if not isinstance(table.c[colname].type, Enum):
                                    options = _re_enum_item.findall(items)
                                    table.c[colname].type = Enum(*options, native_enum=False)
                                continue

            # Tables vs. Classes ********
            # Only form model classes for tables that have a primary key and are not association
            # tables
            """ create classes iff unique col - CAUTION: fails to run """
            if self.is_model_not_table(table, association_tables, noclasses):
                model = self.class_model(table, links[table.name], self.inflect_engine, not nojoined)  # computes attrs (+ roles)
                self.classes[model.name] = model
            else:  # table, not model - no api, no rules, no admin
                model = self.table_model(table)  # eg, View: ProductDetails_V

            self.models.append(model)
            model.add_imports(self.collector)  # end mega-loop for table in metadata.sorted_tables

        # Nest inherited classes in their superclasses to ensure proper ordering
        for model in self.classes.values():
            if model.parent_name != 'Base':
                self.classes[model.parent_name].children.append(model)
                self.models.remove(model)

        # Add either the MetaData or declarative_base import depending on whether there are mapped
        # classes or not
        if not any(isinstance(model, self.class_model) for model in self.models):
            self.collector.add_literal_import('sqlalchemy', 'MetaData')
        else:
            self.collector.add_literal_import('sqlalchemy.ext.declarative', 'declarative_base')

    def create_inflect_engine(self):
        if self.noinflect:
            return _DummyInflectEngine()
        else:
            import inflect
            return inflect.engine()


    def render_imports(self):
        """

        Returns:
            str: data type imports, from ImportCollector
        """

        render_imports_result = '\n'.join('from {0} import {1}'.format(package, ', '.join(sorted(names)))
                         for package, names in self.collector.items())
        return render_imports_result


    def render_metadata_declarations(self):
        nw_info = ""
        if self.model_creation_services.project.nw_db_status in ["nw", "nw+"]:
            nw_info = """#
# Sample Database (Northwind) -- https://apilogicserver.github.io/Docs/Sample-Database/
#
#   Search:
#     manual  - illustrates you can make manual changes to models.py
#     example - more complex cases (explore in database/db_debug/db_debug.py)
"""

        api_logic_server_imports = f"""########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:
# Database:
# Dialect:
#
# mypy: ignore-errors
{nw_info}########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX, TestBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy, os
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.mysql import *

if os.getenv('APILOGICPROJECT_NO_FLASK') is None or os.getenv('APILOGICPROJECT_NO_FLASK') == 'None':
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')
"""
        
        if self.model_creation_services.project.bind_key != "":
            api_logic_server_imports = api_logic_server_imports.replace('Base = declarative_base()',
                            f'Base{self.model_creation_services.project.bind_key} = declarative_base()')
            api_logic_server_imports = api_logic_server_imports.replace('metadata = Base.metadata',
                            f'metadata = Base{self.model_creation_services.project.bind_key}.metadata')
        if "sqlalchemy.ext.declarative" in self.collector:  # Manually Added for safrs (ApiLogicServer)
            # SQLAlchemy2: 'MetaData' object has no attribute 'bind'
            bind = self.model_creation_services.session.bind  # SQLAlchemy2
            dialect_name = bind.engine.dialect.name  # sqlite , mysql , postgresql , oracle , or mssql
            if dialect_name in ["firebird", "mssql", "oracle", "postgresql", "sqlite", "sybase", "mysql"]:
                rtn_api_logic_server_imports = api_logic_server_imports.replace("mysql", dialect_name)
            else:
                rtn_api_logic_server_imports = api_logic_server_imports
                print(".. .. ..Warning - unknown sql dialect, defaulting to msql - check database/models.py")
            rtn_api_logic_server_imports = rtn_api_logic_server_imports.replace(
                "Created:", "Created:  " + str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")))
            rtn_api_logic_server_imports = rtn_api_logic_server_imports.replace(
                "Database:", "Database: " + self.model_creation_services.project.abs_db_url)
            rtn_api_logic_server_imports = rtn_api_logic_server_imports.replace(
                "Dialect:", "Dialect:  " + dialect_name)
            return rtn_api_logic_server_imports
        return "metadata = MetaData()"  # (stand-alone sql1codegen - never used in API Logic Server)

    def _get_compiled_expression(self, statement: sqlalchemy.sql.expression.TextClause): 
        """Return the statement in a form where any placeholders have been filled in."""
        bind = self.model_creation_services.session.bind  # SQLAlchemy2
        # https://docs.sqlalchemy.org/en/20/errors.html#a-bind-was-located-via-legacy-bound-metadata-but-since-future-true-is-set-on-this-session-this-bind-is-ignored
        return str(statement.compile(  # 'MetaData' object has no attribute 'bind' (unlike SQLAlchemy 1.4)
            bind = bind, compile_kwargs={"literal_binds": True}))

    @staticmethod
    def _getargspec_init(method):
        try:
            if hasattr(inspect, 'getfullargspec'):
                return inspect.getfullargspec(method)
            else:
                return inspect.getargspec(method)
        except TypeError:
            if method is object.__init__:
                return ArgSpec(['self'], None, None, None)
            else:
                return ArgSpec(['self'], 'args', 'kwargs', None)

    @classmethod
    def render_column_type(cls, coltype):
        """ Compute the column type, and remember the types for later use in the imports 
            see render_imports, using self.collector
        """
        args = []
        kwargs = OrderedDict()
        argspec = cls._getargspec_init(coltype.__class__.__init__)
        defaults = dict(zip(argspec.args[-len(argspec.defaults or ()):],
                            argspec.defaults or ()))
        missing = object()
        use_kwargs = False
        for attr in argspec.args[1:]:
            # Remove annoyances like _warn_on_bytestring
            if attr.startswith('_'):
                continue

            value = getattr(coltype, attr, missing)
            default = defaults.get(attr, missing)
            if value is missing or value == default:
                use_kwargs = True
            elif use_kwargs:
                kwargs[attr] = repr(value)
            else:
                args.append(repr(value))

        if argspec.varargs and hasattr(coltype, argspec.varargs):
            varargs_repr = [repr(arg) for arg in getattr(coltype, argspec.varargs)]
            args.extend(varargs_repr)

        if isinstance(coltype, Enum) and coltype.name is not None:
            kwargs['name'] = repr(coltype.name)

        for key, value in kwargs.items():
            args.append('{}={}'.format(key, value))

        rendered = coltype.__class__.__name__
        if args:
            rendered += '({0})'.format(', '.join(args))
        if rendered.startswith("CHAR("):  # temp fix for non-double byte chars
            rendered = rendered.replace("CHAR(", "String(")
        return rendered

    def render_constraint(self, constraint):
        def render_fk_options(*opts):
            opts = [repr(opt) for opt in opts]
            for attr in 'ondelete', 'onupdate', 'deferrable', 'initially', 'match':
                value = getattr(constraint, attr, None)
                if value:
                    opts.append('{0}={1!r}'.format(attr, value))

            return ', '.join(opts)

        if isinstance(constraint, ForeignKey):  # TODO: need to check is_included here?
            remote_column = '{0}.{1}'.format(constraint.column.table.fullname,
                                             constraint.column.name)
            return 'ForeignKey({0})'.format(render_fk_options(remote_column))
        elif isinstance(constraint, ForeignKeyConstraint):
            local_columns = _get_column_names(constraint)
            remote_columns = ['{0}.{1}'.format(fk.column.table.fullname, fk.column.name)
                              for fk in constraint.elements]
            return 'ForeignKeyConstraint({0})'.format(
                render_fk_options(local_columns, remote_columns))
        elif isinstance(constraint, CheckConstraint):
            return 'CheckConstraint({0!r})'.format(
                self._get_compiled_expression(constraint.sqltext))
        elif isinstance(constraint, UniqueConstraint):
            columns = [repr(col.name) for col in constraint.columns]
            return 'UniqueConstraint({0})'.format(', '.join(columns))

    @staticmethod
    def render_index(index):
        extra_args = [repr(col.name) for col in index.columns]
        if index.unique:
            extra_args.append('unique=True')
        return 'Index({0!r}, {1})'.format(index.name, ', '.join(extra_args))

    def render_column(self, column: Column, show_name: bool) -> str:
        """_summary_

        Args:
            column (Column): column attributes
            show_name (bool): True means embed col name into render_result

        Returns:
            str: eg. Column(Integer, primary_key=True), Column(String(8000))
        """        
        global code_generator
        fk_debug = False
        kwarg = []
        do_show_name = show_name
        if self.model_creation_services.project.quote:
            do_show_name = True
        is_sole_pk = column.primary_key and len(column.table.primary_key) == 1
        dedicated_fks_old = [c for c in column.foreign_keys if len(c.constraint.columns) == 1]
        dedicated_fks = []  # c for c in column.foreign_keys if len(c.constraint.columns) == 1
        for each_foreign_key in column.foreign_keys:
            if fk_debug:
                log.debug(f'FK: {each_foreign_key}')  # 
                log.debug(f'render_column - is fk: {dedicated_fks}')
            if code_generator.is_table_included(each_foreign_key.column.table.name) \
                                and len(each_foreign_key.constraint.columns) == 1:
                dedicated_fks.append(each_foreign_key)
            else:
                log.debug(f'Excluded single field fl on {column.table.name}.{column.name}')
        if len(dedicated_fks) > 1:
            log.error(f'codegen render_column finds unexpected col with >1 fk:' 
                      f'{column.table.name}.{column.name}')
        is_unique = any(isinstance(c, UniqueConstraint) and set(c.columns) == {column}
                        for c in column.table.constraints)
        is_unique = is_unique or any(i.unique and set(i.columns) == {column}
                                     for i in column.table.indexes)
        has_index = any(set(i.columns) == {column} for i in column.table.indexes)
        server_default = None

        # Render the column type if there are no foreign keys on it or any of them points back to
        # itself
        render_coltype = not dedicated_fks or any(fk.column is column for fk in dedicated_fks)
        if 'DataTypes.char_type DEBUG ONLY' == str(column):
            debug_stop = "Debug Stop: Column"  # char_type = Column(CHAR(1, 'SQL_Latin1_General_CP1_CI_AS'))
        if str(column) in ['Credit_limit', 'credit_limit']:
            debug_stop = "Debug Stop: Column"
        if column.key != column.name:
            kwarg.append('key')
        if column.primary_key:
            kwarg.append('primary_key')
        if not column.nullable and not is_sole_pk:
            kwarg.append('nullable')
        if is_unique:
            column.unique = True
            kwarg.append('unique')
            if self.model_creation_services.project.infer_primary_key:
                # print(f'ApiLogicServer infer_primary_key for {column.table.name}.{column.name}')
                column.primary_key = True
                kwarg.append('primary_key')
        elif has_index:
            column.index = True
            kwarg.append('index')

        if Computed and isinstance(column.server_default, Computed):
            expression = self._get_compiled_expression(column.server_default.sqltext)

            persist_arg = ''
            if column.server_default.persisted is not None:
                persist_arg = ', persisted={}'.format(column.server_default.persisted)

            server_default = 'Computed({!r}{})'.format(expression, persist_arg)

        elif column.server_default:
            # The quote escaping does not cover pathological cases but should mostly work FIXME SqlSvr no .arg
            # not used for postgres/mysql; for sqlite, text is '0'
            if not hasattr( column.server_default, 'arg' ):
                server_default = 'server_default=text("{0}")'.format('0')
            else:
                default_expr = self._get_compiled_expression(column.server_default.arg)
                if '\n' in default_expr:
                    server_default = 'server_default=text("""\\\n{0}""")'.format(default_expr)
                else:
                    default_expr = default_expr.replace('"', '\\"')
                    server_default = 'server_default=text("{0}")'.format(default_expr)

        comment = getattr(column, 'comment', None)
        if (column.name + "") == "xx_id":
            print(f"render_column target: {column.table.name}.{column.name}")  # ApiLogicServer fix for putting this at end:  index=True
        if do_show_name and column.table.name != 'sqlite_sequence':
            log.debug(f"render_column show name is true: {column.table.name}.{column.name}")  # researching why
        if column.name == "credit_limit" and column.table.name == "customers":
            debug_stop = "render column breakpoint"
        rendered_col_type = self.render_column_type(column.type) if render_coltype else ""
        rendered_name = repr(column.name) if do_show_name else ""
        render_result = 'Column({0})'.format(', '.join(
            ([repr(column.name)] if do_show_name else []) +
            ([self.render_column_type(column.type)] if render_coltype else []) +
            [self.render_constraint(x) for x in dedicated_fks] +
            [repr(x) for x in column.constraints] +
            ([server_default] if server_default else []) +
            ['{0}={1}'.format(k, repr(getattr(column, k))) for k in kwarg] +
            (['comment={!r}'.format(comment)] if comment and not self.nocomments else []) + 
            (['quote = True'] if self.model_creation_services.project.quote else [])
            ))
        
        """
                return 'Column({0})'.format(', '.join(
                    ([repr(column.name)] if show_name else []) +
                    ([self.render_column_type(column.type)] if render_coltype else []) +
                    [self.render_constraint(x) for x in dedicated_fks] +
                    [repr(x) for x in column.constraints] +
                    ([server_default] if server_default else []) +
                    ['{0}={1}'.format(k, repr(getattr(column, k))) for k in kwarg] +
                    (['comment={!r}'.format(comment)] if comment and not self.nocomments else [])
                ))
        """
        return render_result

    def render_relationship(self, relationship) -> str:
        ''' returns string like: Department = relationship(\'Department\', remote_side=[Id])
        '''
        rendered = 'relationship('
        args = [repr(relationship.target_cls)]

        if 'secondaryjoin' in relationship.kwargs:
            rendered += '\n{0}{0}'.format(self.indentation)
            delimiter, end = (',\n{0}{0}'.format(self.indentation),
                              '\n{0})'.format(self.indentation))
        else:
            delimiter, end = ', ', ')'

        args.extend([key + '=' + value for key, value in relationship.kwargs.items()])
        return rendered + delimiter.join(args) + end

    def render_relationship_on_parent(self, relationship) -> str:
        ''' returns string like: Department = relationship(\'Department\', remote_side=[Id])
        '''
        rendered = 'relationship('
        args = [repr(relationship.source_cls)]

        if 'secondaryjoin' in relationship.kwargs:
            rendered += '\n{0}{0}'.format(self.indentation)
            delimiter, end = (',\n{0}{0}'.format(self.indentation),
                              '\n{0})'.format(self.indentation))
        else:
            delimiter, end = ', ', ')'

        args.extend([key + '=' + value for key, value in relationship.kwargs.items()])
        return rendered + delimiter.join(args) + end

    def render_table(self, model):
        # Manual edit:
        # replace invalid chars for views etc  TODO review ApiLogicServer -- using model.name vs model.table.name
        table_name = model.name
        bad_chars = r"$-+ "
        if any(elem in table_name for elem in bad_chars):
            print(f"Alert: invalid characters in {table_name}")

        table_name = table_name.replace("$", "_S_")
        table_name = table_name.replace(" ", "_")
        table_name = table_name.replace("+", "_")
        if model.table.name == "Plus+Table":
            debug_stop = "Debug Stop on table"
        rendered = "t_{0} = Table(\n{1}{0!r}, metadata,\n".format(table_name, self.indentation)

        for column in model.table.columns:
            if column.name == "char_type DEBUG ONLY":
                debug_stop = "Debug Stop - column"
            rendered += '{0}{1},\n'.format(self.indentation, self.render_column(column, True))

        for constraint in sorted(model.table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, PrimaryKeyConstraint):
                continue
            if (isinstance(constraint, (ForeignKeyConstraint, UniqueConstraint)) and
                    len(constraint.columns) == 1):
                continue  # TODO: need to check is_included here?
            rendered += '{0}{1},\n'.format(self.indentation, self.render_constraint(constraint))

        for index in model.table.indexes:
            if len(index.columns) > 1:
                rendered += '{0}{1},\n'.format(self.indentation, self.render_index(index))

        if model.schema:
            rendered += "{0}schema='{1}',\n".format(self.indentation, model.schema)

        table_comment = getattr(model.table, 'comment', None)
        if table_comment:
            quoted_comment = table_comment.replace("'", "\\'").replace('"', '\\"')
            rendered += "{0}comment='{1}',\n".format(self.indentation, quoted_comment)

        return rendered.rstrip('\n,') + '\n)\n'

    def render_class(self, model):
        """ returns string for model class, written into model.py by sqlacodegen_wrapper """
        super_classes = model.parent_name
        if model.name in ["QtrTotal", "StressBinaryDouble", "STRESSAllChar"]:
            debug_stop = "nice breakpoint for class rendering"
        
        ''' rework SafrsBaseX 12/28/2024 - just Base now
        if self.model_creation_services.project.bind_key != "":
            super_classes = f'Base{self.model_creation_services.project.bind_key}, db.Model, UserMixin'
            rendered = 'class {0}(SAFRSBaseX, {1}):  # type: ignore\n'.format(model.name, super_classes)   # ApiLogicServer
            # f'Base{self.model_creation_services.project.bind_key} = declarative_base()'
        else:
            rendered = 'class {0}(SAFRSBaseX, {1}):\n'.format(model.name, super_classes)   # ApiLogicServer
        '''
        rendered = 'class {0}(Base):  # type: ignore\n'.format(model.name)   # ApiLogicServer
        if model.table.name in self.model_creation_services.project.table_descriptions:
            rendered += '    """\n'
            rendered += '    ' + 'description: ' + self.model_creation_services.project.table_descriptions[model.table.name] + '\n'  
            rendered += '    """\n'
        rendered += '{0}__tablename__ = {1!r}\n'.format(self.indentation, model.table.name)

        end_point_name = model.name
        if self.model_creation_services.project.bind_key != "":
            if self.model_creation_services.project.model_gen_bind_msg == False:
                self.model_creation_services.project.model_gen_bind_msg = True
                log.debug(f'.. .. ..Setting bind_key = {self.model_creation_services.project.bind_key}')
            end_point_name = self.model_creation_services.project.bind_key + \
                self.model_creation_services.project.bind_key_url_separator + model.name
        rendered += '{0}_s_collection_name = {1!r}  # type: ignore\n'.format(self.indentation, end_point_name)
        if self.model_creation_services.project.bind_key != "":
            bind_key = self.model_creation_services.project.bind_key
            rendered += '{0}__bind_key__ = {1!r}\n'.format(self.indentation, bind_key)  # usually __bind_key__ = None
        # else:  bind_key no longer required for 'main' objects
       #   bind_key = "None"

        # Render constraints and indexes as __table_args__
        autonum_col = False
        table_args = []
        for constraint in sorted(model.table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, PrimaryKeyConstraint):
                if constraint._autoincrement_column is not None:
                    autonum_col = True
                continue
            if (isinstance(constraint, (ForeignKeyConstraint, UniqueConstraint)) and
                    len(constraint.columns) == 1):
                continue
            # eg, Order: ForeignKeyConstraint(['Country', 'City'], ['Location.country', 'Location.city'])
            this_included = code_generator.is_table_included(model.table.name)
            target_included = True
            if isinstance(constraint, ForeignKeyConstraint):  # CheckConstraints don't have elements
                target_included = code_generator.is_table_included(constraint.elements[0].column.table.name)
            if this_included and target_included:
                table_args.append(self.render_constraint(constraint))
            else:
                log.debug(f'foreign key constraint excluded on {model.table.name}: '
                          f'{self.render_constraint(constraint)}')
        for index in model.table.indexes:
            if len(index.columns) > 1:
                table_args.append(self.render_index(index))

        table_kwargs = {}
        if model.schema:
            table_kwargs['schema'] = model.schema

        table_comment = getattr(model.table, 'comment', None)
        if table_comment:
            table_kwargs['comment'] = table_comment

        kwargs_items = ', '.join('{0!r}: {1!r}'.format(key, table_kwargs[key])
                                 for key in table_kwargs)
        kwargs_items = '{{{0}}}'.format(kwargs_items) if kwargs_items else None
        if table_kwargs and not table_args:
            rendered += '{0}__table_args__ = {1}\n'.format(self.indentation, kwargs_items)
        elif table_args:
            if kwargs_items:
                table_args.append(kwargs_items)
            if len(table_args) == 1:
                table_args[0] += ','
            table_args_joined = ',\n{0}{0}'.format(self.indentation).join(table_args)
            rendered += '{0}__table_args__ = (\n{0}{0}{1}\n{0})\n'.format(
                self.indentation, table_args_joined)

        # Render columns
        # special case id: https://github.com/valhuber/ApiLogicServer/issues/69#issuecomment-1579731936
        rendered += '\n'
        for attr, column in model.attributes.items():
            if isinstance(column, Column):
                show_name = attr != column.name
                if not attr.isascii():
                    log.debug(f'Non-ascii column name: {column.name} in {model.name}')
                    rendered_name = attr.encode('ascii', 'ignore').decode('ascii')
                    rendered_column = '{0}{1} = {2}\n'.format(
                            self.indentation, rendered_name, self.render_column(column, show_name))
                else:
                    rendered_column = '{0}{1} = {2}\n'.format(
                        self.indentation, attr, self.render_column(column, show_name))
                if column.name == "id":  # add name to Column(Integer, primary_key=True)
                    """ add name to Column(Integer, primary_key=True) - but makes system fail
                    rendered_column = rendered_column.replace(
                        'id = Column(', 'Id = Column("id", ')
                    log.debug(f' id = Column(Integer, primary_key=True) -->'\
                              f' Id = Column("id", Integer, primary_key=True)')
                    """
                    if model.name not in["User", "Api"]:
                        pass
                        # log.info(f'** Warning: id columns will not be included in API response - {model.name}.id\n')
                attr_typing = True  # verify this in nw database/db_debug/db_debug.py
                if attr_typing:
                    if "= Column(DECIMAL" in rendered_column:
                        rendered_column = rendered_column.replace(
                            f'= Column(DECIMAL',
                            f': DECIMAL = Column(DECIMAL'
                        )
                rendered += rendered_column
        if not autonum_col:
            rendered += '{0}{1}'.format(self.indentation, "allow_client_generated_ids = True\n")

        if any(isinstance(value, Relationship) for value in model.attributes.values()):
            pass
            # rendered += '\n'
        
        self.render_relns(model = model)

        # Render subclasses
        for child_class in model.children:
            rendered += self.model_separator + self.render_class(child_class)  # ApiLogicServer - not executed
        # rendered += "\n    # END RENDERED CLASS\n"  # useful for debug, as required
        return rendered
    
    def render_relns(self, model: ModelClass):
        """ accrue 

        Update for SQLAlchemy 2 typing 

        https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html#tutorial-orm-related-objects

        e.g. for single field relns:

        children (in customer...)
            * OrderList : Mapped[List['Order']] = relationship(back_populates="Customer")

        parent (in order...)
            * Customer : Mapped["Customer"] = relationship(back_populates="OrderList")

        specials:
            * self-relns: https://docs.sqlalchemy.org/en/20/orm/self_referential.html
            * multi-relns: https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#handling-multiple-join-paths
                    * suggests foreign_keys=[] on child only, *but* parent too (eg, Dept)
                    * https://github.com/sqlalchemy/sqlalchemy/discussions/10034
                    * Department : Mapped["Department"] = relationship("Department", foreign_keys='[Employee.OnLoanDepartmentId]', back_populates=("EmployeeList"))
                    * EmployeeList : Mapped[List["Employee"]] = relationship("Employee", foreign_keys='[Employee.OnLoanDepartmentId]', back_populates="Department")

        
        Args:
            model (ModelClass): gen reln accessors for this model

        Returns:
            Just updates model.rendered_parent_relationships
        """

        backrefs = {}
        """ <class>.<children-accessor: <children-accessor """

        # TODO mult-reln https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#handling-multiple-join-paths

        for attr, relationship in model.attributes.items():  # this list has parents only, order random
            if isinstance(relationship, Relationship):

                reln: ManyToOneRelationship = relationship  # for typing; each parent for model child
                multi_reln_fix = ""
                if "foreign_keys" in reln.kwargs:
                    multi_reln_fix = 'foreign_keys=' + reln.kwargs["foreign_keys"] + ', '
                    pass

                parent_model = self.classes[reln.target_cls]
                parent_accessor_name = reln.parent_accessor_name
                self_reln_fix = ""
                if "remote_side" in reln.kwargs:
                    self_reln_fix = 'remote_side=' + reln.kwargs["remote_side"] + ', '
                parent_accessor = f'    {attr} : Mapped["{reln.target_cls}"] = relationship({multi_reln_fix}{self_reln_fix}back_populates=("{reln.child_accessor_name}"))\n'

                child_accessor_name = reln.child_accessor_name
                child_accessor = f'    {child_accessor_name} : Mapped[List["{reln.source_cls}"]] = '\
                                 f'relationship({multi_reln_fix}back_populates="{reln.parent_accessor_name}")\n'

                if model.name in ["Item", "Employee", "CharacterClass"]:  # Emp has Department and Department1
                    debug_str = "nice breakpoint"  # DND CharacterClass - check parent acceossor (class_ not class)
                model.rendered_parent_relationships += parent_accessor
                parent_model.rendered_child_relationships += child_accessor



    def render(self, outfile=sys.stdout):
        """ create model from db, and write models.py file to in-memory buffer (outfile)

            relns created from not-yet-seen children, so
            * save *all* class info,
            * then append rendered_model_relationships (since we might see parent before or after child)
        """
        for model in self.models:  # class, with __tablename__ & __collection_name__ cls variables, attrs
            if isinstance(model, self.class_model):
                # rendered_models.append(self.render_class(model))
                model.rendered_model = self.render_class(model)  # also sets parent_model.rendered_model_relationships

        rendered_models = []  # now append the rendered_model + rendered_model_relationships
        for model in self.models:
            if isinstance(model, self.class_model):
                each_rendered_model = model.rendered_model

                reln_accessors = "\n    # parent relationships (access parent)\n"
                if self.model_creation_services.project.nw_db_status in ["nw", "nw+"]:
                    if model.name == "Employee":
                        reln_accessors = "\n    # parent relationships (access parent) -- example: multiple join paths\n"
                        reln_accessors += "    # .. https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#handling-multiple-join-paths\n"
                    elif model.name == "Department":
                        reln_accessors = "\n    # parent relationships (access parent) -- example: self-referential\n"
                        reln_accessors += "    # .. https://docs.sqlalchemy.org/en/20/orm/self_referential.html\n"
                each_rendered_model += reln_accessors
                each_rendered_model += model.rendered_parent_relationships

                each_rendered_model += "\n    # child relationships (access children)\n"
                each_rendered_model += model.rendered_child_relationships
                
                each_rendered_model += "\n" + self.model_creation_services.opt_locking

                rendered_models.append(each_rendered_model)
            elif isinstance(model, self.table_model):  # eg, views, database id generators, etc
                rendered_models.append(self.render_table(model))

        output = self.template.format(
            imports=self.render_imports(),
            metadata_declarations=self.render_metadata_declarations(),
            models=self.model_separator.join(rendered_models).rstrip('\n'))
        print(output, file=outfile)  # write the in-mem class file


def key_module_map():
    pass
    read_tables = CodeGenerator()               # invoked by sqlacodegen_wrapper
    read_tables = CodeGenerator.__init__()      # ctor here
    calls_class = ModelClass.__init__()         # gets attrs, roles
    build_reln = ManyToOneRelationship(None)    # complex code for accessors
    CodeGenerator.render_class()
    CodeGenerator.render_column()
    CodeGenerator.render_relns()                # accrue relns, then render these...
    CodeGenerator.render_relationship()         # accrue relns, then render
    CodeGenerator.render_relationship_on_parent()
