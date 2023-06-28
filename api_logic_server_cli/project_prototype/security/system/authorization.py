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
from sqlalchemy.orm import session
from sqlalchemy import event, MetaData, and_, or_
import safrs
from sqlalchemy import event, MetaData
from sqlalchemy.orm import with_loader_criteria, DeclarativeMeta
from database import models
from logic_bank.exec_row_logic.logic_row import LogicRow
import logging, sys
from safrs.errors import JsonapiError
from http import HTTPStatus
from config import Config
from flask_jwt_extended import current_user

from config import Config
authentication_provider = Config.SECURITY_PROVIDER

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
    def current_user(cls):
        """ 
        User code calls this as required to get user/roles (eg, multi-tenant client_id)

        see https://flask-login.readthedocs.io/en/latest/
        """
        return current_user

    @staticmethod
    @classmethod
    def current_user_has_role(role_name: str) -> bool: 
        '''
        Helper, e.g. rules can determine if update allowed

        If user has role xyz, then for update authorization s/he can... 
        '''
        result = False
        for each_role in Security.current_user().UserRoleList:
            if role_name == each_role.name:
                return True
        return False

class GrantSecurityException(JsonapiError):
    """
    enables clients to identify "any grant constraint"

    Constraint failures raise GrantSecurityException, e.g.:
        try:
            session.commit()
        except GrantSecurityException as ce:
            print("Constraint raised: " + str(ce))

    """
    def __init__(self, user, entity_name, access, status_code=HTTPStatus.UNAUTHORIZED):
        super().__init__()
        self.message = f"User: {user.id} with roles: [{user.UserRoleList}] does not have {access} access on entity: {entity_name}"
        self.status_code = status_code.value



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
            :filter: where clause to be added
        
        per calls from declare_security.py
    """

    grants_by_table : Dict[str, list['Grant']] = {}
    grants_by_role : Dict[str, list['Grant']] = {}
    '''
    Dict keyed by Table name (obtained from class name), value is a (role, filter)
    '''

    def __init__(self, on_entity: DeclarativeMeta, 
        to_role: str = None,
        can_read: bool = True,
        can_insert: bool = False,
        can_update: bool = False,
        can_delete: bool = False,
        filter: object = None):
        
        if isinstance(on_entity, str):
            self.class_name = on_entity
        else:
            self.class_name : str = on_entity._s_class_name  # type: ignore
        self.role_name : str = to_role
        self.filter = filter
        self.entity :DeclarativeMeta = on_entity 
        self.can_read = can_read
        self.can_insert = can_insert
        self.can_update = can_update
        self.can_delete = can_delete
        self.orm_execute_state = None # used by filter
        self.table_name : str = None if isinstance(on_entity, str) else on_entity.__tablename__   # type: ignore
        self.update_CRUD()
        self._entity_name:str = None if isinstance(on_entity, str) else on_entity._s_type # Class Name
        if self._entity_name is not None:
            if self._entity_name not in self.grants_by_table:
                Grant.grants_by_table[self._entity_name] = []
            Grant.grants_by_table[self._entity_name].append( self )
        else:
            if self.role_name not in self.grants_by_role:
                Grant.grants_by_role[self.role_name] = []
            Grant.grants_by_role[self.role_name].append( self )
        
        
        def current_user():
            return Security.current_user() if Config.SECURITY_ENABLED else None
        
    def update_CRUD(self):
        if self.class_name in ["ALL", "A"]:
            self._updateCRUD(True, True, True, True)
        elif self.class_name in ["None", "N"]:
            self._updateCRUD(False, False, False, False)
        elif self.class_name == "CRU":
            self._updateCRUD(True, True, True, False)
        elif self.class_name == "CU":
            self._updateCRUD(True, True, True, False)
        elif self.class_name == "U":
            self._updateCRUD(True, False, True, False)
        elif self.class_name == "D":
            self._updateCRUD(True, False, False, True)
        elif self.class_name == "C":
            self._updateCRUD(True, True, False, False)
        elif self.class_name == "R":
            self._updateCRUD(True, False, False, False)


    def _updateCRUD(self, read, create, update, delete):
        self.can_read = read
        self.can_insert = create
        self.can_update = update
        self.can_delete = delete
        
            
    @staticmethod
    def exec_grants(entity_name: str,crud_state: str, orm_execute_state: any = None) -> None:
        '''
        SQLAlchemy select event for current user's roles, append that role's grant filter to the SQL before execute 

        if you have a select() construct, you can add new AND things just calling .where() again.
        
        e.g. existing_statement.where(or_(f1, f2)) .

        u2 is a manager and a tenant
        '''
        user = Security.current_user()
        
        if not Config.SECURITY_ENABLED or not user:
            return
        
       
        can_read = False
        can_insert = False
        can_delete = False
        can_update = False
        try:
            from flask import g
            if user.id == 'sa':
                security_logger.debug("sa (eg, set_user_sa()) - no grants apply")
                return
        except Exception as ex:
            security_logger.debug(f"no user - ok (eg, system initialization) error: {ex}")
            return
        
        # start out full restricted - any True will turn on access
        for each_role in Grant.grants_by_role:
            for each_user_role in user.UserRoleList:
                if each_role == each_user_role.role_name:
            #if Security.current_user_has_role(each_role):
                    for grant_role in Grant.grants_by_role[each_role]:
                        can_read = can_read or grant_role.can_read
                        can_insert = can_insert or grant_role.can_insert
                        can_delete = can_delete or grant_role.can_delete
                        can_update = can_update or grant_role.can_update
                        print(f"Grant on role: {each_role} Read: {can_read}, Update: {can_update}, Insert: {can_insert}, Delete: {can_delete}")
                    
        for each_user_role in user.UserRoleList:
            # if False or True returns True for each role
            if entity_name in Grant.grants_by_table:
                grant_list = []
                grant_entity = None
                for each_grant in Grant.grants_by_table[entity_name]:
                    grant_entity = each_grant.entity
                    if each_grant.role_name == each_user_role.role_name:
                        security_logger.debug(f'Amend Grant for class / role: {entity_name} / {each_grant.role_name} - {each_grant.filter}')
                        print(f"Grant on entity: {entity_name} Read: {each_grant.can_read}, Update: {each_grant.can_update}, Insert: {each_grant.can_insert}, Delete: {each_grant.can_delete}")
                        # 
                        can_read = can_read or each_grant.can_read 
                        can_insert = can_insert or each_grant.can_insert
                        can_delete = can_delete or each_grant.can_delete
                        can_update = can_update or each_grant.can_update
                        
                        if each_grant.filter is not None \
                            and orm_execute_state is not None:
                            grant_list.append(each_grant.filter())
                security_logger.debug(f"Grants applied for entity {entity_name}")
                if grant_entity is not None \
                    and grant_list and crud_state == "is_select":
                    grant_filter = or_(*grant_list)
                    # apply filter(s) (additional where clause) for row security on select
                    orm_execute_state.statement = orm_execute_state.statement.options(
                        with_loader_criteria(grant_entity,grant_filter))
            else:
                security_logger.debug(f"No Grants for entity {entity_name}")
            
        if not can_read and crud_state == 'is_select':
            raise GrantSecurityException(user=user,entity_name=entity_name,access="read")
        elif not can_update and crud_state == 'is_update':
                raise GrantSecurityException(user=user,entity_name=entity_name,access="update")
        elif not can_insert and crud_state == 'is_insert':
                raise GrantSecurityException(user=user,entity_name=entity_name,access="insert")
        elif not can_delete and crud_state == 'is_delete':
                raise GrantSecurityException(user=user,entity_name=entity_name,access="delete")
    
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
        
            if Config.SECURITY_ENABLED: 
                entity_name = self.logic_row.name 
                #select is handled by orm_execution_state
                _event_state = ""
                if self.logic_row.is_updated():
                    _event_state = 'is_update'
                elif self.logic_row.is_inserted():
                    _event_state = 'is_insert'
                elif self.logic_row.is_deleted(): 
                    _event_state = 'is_delete'
                    
                Grant.exec_grants(entity_name, _event_state, None)

@event.listens_for(session, 'do_orm_execute')
def receive_do_orm_execute(orm_execute_state):
    "listen for the 'do_orm_execute' event from SQLAlchemy"
    if (
        Config.SECURITY_ENABLED
        and orm_execute_state.is_select 
        and not orm_execute_state.is_column_load
        and not orm_execute_state.is_relationship_load
    ):            
        security_logger.debug('receive_do_orm_execute alive')
        mapper = orm_execute_state.bind_arguments['mapper']
        table_name = mapper.class_.__name__   # mapper.mapped_table.fullname disparaged
        if table_name == "User":
            #pass
            security_logger.debug('No grants - avoid recursion on User table')
        elif  session._proxied._flushing:  # type: ignore
            security_logger.debug('No grants during logic processing')
        else:
            #security_logger.info(f"ORM Listener table: {table_name} is_select: {orm_execute_state.is_select}")    
            Grant.exec_grants(table_name, "is_select" , orm_execute_state)
