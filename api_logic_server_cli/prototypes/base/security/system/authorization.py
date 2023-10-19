"""
System support for role based authorization.

Supports declaring grants,
and enforcing them using SQLAlchemy 
   * do_orm_execute
   * with_loader_criteria(each_grant.entity, each_grant.filter)

You typically do not alter this file.
"""

from typing import Dict, Tuple
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import ORMExecuteState
from sqlalchemy.orm import session
from sqlalchemy import event, MetaData, and_, or_
import inspect
import safrs
from sqlalchemy import event, MetaData, text
from sqlalchemy.orm import with_loader_criteria, DeclarativeMeta, ColumnProperty
from database import models
from logic_bank.exec_row_logic.logic_row import LogicRow
import logging, sys
from safrs.errors import JsonapiError
from http import HTTPStatus



from flask_jwt_extended import current_user

from config import Args
authentication_provider = Args.security_provider

security_logger = logging.getLogger(__name__)

security_logger.debug(f'\nAuthorization loaded via api_logic_server_run.py -- import \n')


db = safrs.DB         # Use the safrs.DB, not db!
session = db.session  # sqlalchemy.orm.scoping.scoped_session


class Security:

    @classmethod
    def set_user_sa(cls):
        from flask import g
        g.isSA = True
    
    @classmethod
    def set_current_user(cls, user):
        current_user = user

    @classmethod
    def current_user(cls):
        """ 
        User code calls this as required to get user/roles (eg, multi-tenant client_id)

        see https://flask-login.readthedocs.io/en/latest/
        """
        return current_user

    @staticmethod
    @classmethod
    def current_user_has_role(cls, role_name: str) -> bool: 
        '''
        Helper, e.g. rules can determine if update allowed

        If user has role xyz, then for update authorization s/he can... 
        '''
        result = False
        return any(
            role_name == each_role.name
            for each_role in Security.current_user().UserRoleList
        )

class GrantSecurityException(JsonapiError):
    """
    enables clients to identify "any grant constraint"

    Constraint failures raise GrantSecurityException, e.g.:
        try:
            session.commit()
        except GrantSecurityException as ce:
            print("Constraint raised: " + str(ce))

    """
    def __init__(self, user, entity_name, access, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = f"Grant Security Error on User: {user.id} with roles: [{user.UserRoleList}] does not have {access} access on entity: {entity_name}"
        self.status_code = status_code.value
        security_logger.error(f"Grant Security Error on User: {user.id} with roles: [{user.UserRoleList}] does not have {access} access on entity: {entity_name}")

class DefaultRolePermission:
    """Each Role can have a default set of CRUD settings
        DefaultRolePermission(
                to_role = Roles.tenant,
                can_delete = False,
                can_update = False,
                can_insert = False,
                can_read = False)
    Raises:
        execute GrantSecurityException: 
    
    """
    grants_by_role : Dict[str, list['Grant']] = {}
    
    def __init__(self,
        to_role: str = None,
        can_read: bool = True,
        can_insert: bool = True,
        can_update: bool = True,
        can_delete: bool = True):
        
        self.role_name : str = to_role
        self.can_read = can_read
        self.can_insert = can_insert
        self.can_update = can_update
        self.can_delete = can_delete

        if self.role_name not in self.grants_by_role:
            DefaultRolePermission.grants_by_role[self.role_name] = []
        DefaultRolePermission.grants_by_role[self.role_name].append( self )


class GlobalTenantFilter():
    """
    Apply a single global select to all tables to enforce multi-tenant

    TODO: why no role?  Admin would require a client_id, and alter it to look at account?

    Example
        GlobalTenantFilter(tenant_id = "Client_id",
                           filter = '{entity_class}.Client_id == 1')

    Args:
        :tenant_id:str - name of the attribute found in any entity
        :filter:str -e.g.filter='{entity_name}.EMPID == Security.current_user().emp_id'

    """

    globals_by_class_name : Dict[str, list['GlobalTenantFilter']] = {}
    """ key by class_name, return list['GlobalTenantFilter'] """

    def __init__(self,
                 multi_tenant_attribute_name: str,      # eg. Client_id, Is_soft_deleted
                 filter: str,                           # will be exec'd into lambda
                 roles_non_multi_tenant: list[str],     # filter not applied to these roles
                 class_name: str = None):               # internal use only
        
        self.multi_tenant_attribute_name = multi_tenant_attribute_name
        self.filter_str = filter
        self.class_name = None
        
        # if self.tenant_id not in GlobalTenantFilter.grants_by_multi_tenant_attribute_name:
        #    GlobalTenantFilter.grants_by_multi_tenant_attribute_name[self.multi_tenant_attribute_name] = self

        models_name = 'database.models'
        cls_members = inspect.getmembers(sys.modules[models_name], inspect.isclass)


        if self.class_name is None:  # add filter for all models (?) with tentant_id attr
            for each_cls_member in cls_members:
                each_class_def_str = str(each_cls_member)
                #  such as ('Category', <class 'models.Category'>)
                if (f"'{models_name}." in str(each_class_def_str) and
                        "Ab" not in str(each_class_def_str)):
                    self.class_name = each_cls_member[0]
                    self.classs = each_cls_member[1]
                    table_name = self.classs.__tablename__  # FIXME _s_collection_name
                    columns = self.classs._s_columns._all_columns
                    for each_column in columns:
                        if each_column.name == multi_tenant_attribute_name:
                            if table_name.startswith("Category"):
                                debug_str = "Excellent breakpoint"
                            # prove same filter works   1) as a normal Grant, and   2) using lambda variable
                            filter_lambda1 = lambda :  models.Customer.Client_id == 1  # SQLAlchemy "binary expression"
                            filter_lambda = None
                            self.lambda_str = self.filter_str.replace("{entity_class}", f"lambda : models.{self.class_name}")
                            filter_lambda = eval(self.lambda_str)
                            # eval('filter_lambda = lambda :  models.Customer.Client_id == 1')
                            security_logger.debug(f"adding Global tenant filter for {self.class_name}: {self.lambda_str}")
                            self.lambda_filter = eval(self.lambda_str)
                            assert self.lambda_filter is not None, "exec failed to set self.lambda_filter"
                            grant_str = f'Grant (on_entity=models.{self.class_name}, to_role="*", filter={self.lambda_str})'
                            security_logger.debug(f".. using explict lambda {grant_str}")
                            exec(grant_str)  # create a 'standard' grant
                            break  # next resource class

            
class Grant:
    """
    Invoke these to declare Role Permissions.
    Use code completion to discover models.
    Create grant for <on_entity> / <to_role>

        Example
        =======
        Grant(  on_entity = models.Category,  # use code completion
                to_role = Roles.tenant,
                can_delete = False,
                can_update = False,
                can_insert = False,
                can_read = False,
                filter = models.Category.Id == Security.current_user().client_id)  # User table attributes 
        Args
        ----
            :on_entity: a class from models.py
            :to_role: valid role name from Authentication Provider
            :can_read: bool = True,
            :can_insert: bool = True,
            :can_update: bool = True,
            :can_delete: bool = True,
            :filter: where clause to be added to each select e.g.: lambda row: row.clientId == Security.current_user().client_id
        
        per calls from declare_security.py
    """

    grants_by_table : Dict[str, list['Grant']] = {}
    entity_list : Dict[str, list['str']] = {}    

    '''
    Dict keyed by Table name (obtained from class name), value is a (role, filter)
    '''

    def __init__(self, on_entity: DeclarativeMeta, 
        to_role: str = None,
        can_read: bool = True,
        can_insert: bool = True,
        can_update: bool = True,
        can_delete: bool = True,
        filter: object = None,
        filter_debug: str = ""):
        
        
        self.class_name = on_entity
        self.class_name : str = on_entity._s_class_name  # type: ignore
        self.role_name : str = to_role
        self.filter = filter
        """ a filter lambda """
        self.entity :DeclarativeMeta = on_entity 
        self.can_read = can_read
        self.can_insert = can_insert
        self.can_update = can_update
        self.can_delete = can_delete
        self.orm_execute_state = None # used by filter
        self.table_name : str = on_entity.__tablename__   # type: ignore
        self.filter_debug = filter_debug
        
        self._entity_name:str =  on_entity._s_type # Class Name
        if self._entity_name is not None:
            if self._entity_name not in self.grants_by_table:
                Grant.grants_by_table[self._entity_name] = []
            Grant.grants_by_table[self._entity_name].append( self )
        
        
        def current_user():
            return Security.current_user() if Args.security_enabled else None
    
    @staticmethod
    def entity_has_attribute(entity_name: str, tenant_id:str, property_list) -> bool:
        """returns true if tenant_id is property_list

        Args:
            entity_name (str): _description_
            tenant_id (str): _description_
            property_list (_type_): eg, from mapper.iterate_properties -- you only get 1 shot

        Returns:
            bool: _description_
        """
        if tenant_id not in Grant.entity_list:
            Grant.entity_list[entity_name] = {}
            db_list_properties = False  # FIXME True eats the property_list, so never finds attrs
            if db_list_properties:
                security_logger.debug(f'\nentity_has_attribute {entity_name}')
                for each_property in property_list:
                    security_logger.debug(f'.. {each_property}')
            attr_list = [
                each_property.class_attribute.key
                for each_property in property_list
                    if isinstance(
                        each_property, ColumnProperty
                    )
            ]
            Grant.entity_list[entity_name] = attr_list
        return  tenant_id in Grant.entity_list[entity_name]
            
    @staticmethod
    def exec_grants(entity_name: str, crud_state: str, orm_execute_state: any = None, property_list: any = None) -> None:
        """
        SQLAlchemy select event for current user's roles, append that role's grant filter to the SQL before execute 

        if you have a select() construct, you can add new AND things just calling .where() again.
        
        e.g. existing_statement.where(or_(f1, f2)) .

        u2 is a manager and a tenant

        Args:
            entity_name (str): class name
            crud_state (str): _description_
            orm_execute_state (any, optional): _description_. Defaults to None.
            property_list (any, optional): _description_. Defaults to None.

        Raises:
            GrantSecurityException: _description_
            GrantSecurityException: _description_
            GrantSecurityException: _description_
            GrantSecurityException: _description_
        """
        
        if not Args.security_enabled:
            return
        
        user = Security.current_user()
        
        can_read = False
        can_insert = False
        can_delete = False
        can_update = False
        try:
            from flask import g
            if user.id == 'sa' or g.isSA:
                security_logger.debug("sa (eg, set_user_sa()) - no grants apply")
                return
        except Exception as ex:
            if not user:
                security_logger.debug(f"no user - ok (eg, system initialization) error: {ex}")
                return

        grant_list = []
        """ grant filters for this query; can be > 1, since users have > 1 role, and global tenant filters """

        grant_entity = entity_name 
                    
        #########################################
        # Role crud permissions 
        #########################################
        # start out full restricted - any True will turn on access
        for each_role in DefaultRolePermission.grants_by_role:
            for each_user_role in user.UserRoleList:
                if each_user_role.role_name == "sa":
                    can_read = True
                    can_insert = True
                    can_delete = True
                    can_update = True
                    security_logger.debug(f"Grant on role sa - all permissions")
                    break
                if each_role == each_user_role.role_name:
                    #if Security.current_user_has_role(each_role):
                    for grant_role in DefaultRolePermission.grants_by_role[each_role]:
                        can_read = can_read or grant_role.can_read
                        can_insert = can_insert or grant_role.can_insert
                        can_delete = can_delete or grant_role.can_delete
                        can_update = can_update or grant_role.can_update
                        security_logger.debug(f"Grant on role: {each_role} Read: {can_read}, Update: {can_update}, Insert: {can_insert}, Delete: {can_delete}")
                    
        #########################################
        # Grants 
        #########################################
        if entity_name in Grant.grants_by_table:
            for each_grant in Grant.grants_by_table[entity_name]:
                grant_entity = each_grant.entity
                if each_grant.role_name == "*":
                    if each_grant.filter is not None \
                        and orm_execute_state is not None:
                        grant_list.append(each_grant.filter())
                        security_logger.debug(f".. Accruing global grant for entity {entity_name}: {each_grant.filter_debug} ({each_grant.filter})")
                else:
                    for each_user_role in user.UserRoleList:
                        if each_grant.role_name == each_user_role.role_name:
                            security_logger.debug(f'Amend Grant for class / role: {entity_name} / {each_grant.role_name} - {each_grant.filter}')
                            print(f"Grant on entity: {entity_name} Role: {each_user_role.role_name:} Read: {each_grant.can_read}, Update: {each_grant.can_update}, Insert: {each_grant.can_insert}, Delete: {each_grant.can_delete}")
                            # 
                            can_read = can_read or each_grant.can_read 
                            can_insert = can_insert or each_grant.can_insert
                            can_delete = can_delete or each_grant.can_delete
                            can_update = can_update or each_grant.can_update
                                
                            if each_grant.filter is not None \
                                and orm_execute_state is not None:
                                grant_list.append(each_grant.filter())
                                security_logger.debug(f".. Accruing grant for entity {entity_name}: {each_grant.filter_debug} ({each_grant.filter})")
            security_logger.debug(f"Grants accrued for entity {entity_name}")
        else:
            security_logger.debug(f"No Grants for entity {entity_name}")
            
        security_logger.debug(f"user:{user} state:{crud_state}, read:{can_read}, insert:{can_insert}, update:{can_update}, delete:{can_delete}")   
        
        if not can_read and crud_state == 'is_select':
            raise GrantSecurityException(user=user,entity_name=entity_name,access="read")
        elif not can_update and crud_state == 'is_update':
                raise GrantSecurityException(user=user,entity_name=entity_name,access="update")
        elif not can_insert and crud_state == 'is_insert':
                raise GrantSecurityException(user=user,entity_name=entity_name,access="insert")
        elif not can_delete and crud_state == 'is_delete':
                raise GrantSecurityException(user=user,entity_name=entity_name,access="delete")
    
        if grant_entity is not None and grant_list and crud_state == "is_select":
            grant_filter = or_(*grant_list)
            # apply filter(s) (additional where clause) for row security on select
            orm_execute_state.statement = orm_execute_state.statement.options(
                with_loader_criteria(grant_entity,grant_filter))
            security_logger.debug(f"Filter(s) applied for entity {entity_name} ")   

    @staticmethod
    class process_updates():
        #cls, logic_row: LogicRow):
        """
        This will be called from logic/declare_logic.py handle all row events
        if security is enabled for insert/update/delete
        Args:
            logic_row (LogicRow): 
        """
        def __init__(self,
            logic_row:LogicRow):
        
            self.logic_row = logic_row
        
            if Args.security_enabled: 
                entity_name = self.logic_row.name 
                #select is handled by orm_execution_state
                _event_state = ""
                if self.logic_row.ins_upd_dlt == "upd":
                    _event_state = 'is_update'
                elif self.logic_row.ins_upd_dlt == "ins":
                    _event_state = 'is_insert'
                elif self.logic_row.ins_upd_dlt == "dlt": 
                    _event_state = 'is_delete'
                    
                Grant.exec_grants(entity_name, _event_state, None)

@event.listens_for(session, 'do_orm_execute')
def receive_do_orm_execute(orm_execute_state: ORMExecuteState ):
    """listen for the 'do_orm_execute' event from SQLAlchemy

    Args:
        orm_execute_state (_type_): _description_
    """

    if (
        Args.security_enabled
        and orm_execute_state.is_select
        and not orm_execute_state.is_column_load
        and not orm_execute_state.is_relationship_load
    ):            
        mapper = orm_execute_state.bind_arguments['mapper']
        class_name = mapper.class_.__name__   # mapper.mapped_table.fullname disparaged
        if class_name == "Users":  # TODO: table_name?
            #pass
            security_logger.debug('No grants - avoid recursion on User table')
        elif  session._proxied._flushing:  # type: ignore
            security_logger.debug('No grants during logic processing')
        else:
            # verbose++ security_logger.debug(f"ORM Listener table: {table_name}, class: {mapper.class_}  is_select: {orm_execute_state.is_select}")    
            property_list = mapper.iterate_properties
            Grant.exec_grants(class_name, "is_select" , orm_execute_state, property_list)
