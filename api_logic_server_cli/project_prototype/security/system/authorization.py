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
    def __init__(self, user, entity_name, access, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = f"Grant Security Error on User: {user.id} with roles: [{user.UserRoleList}] does not have {access} access on entity: {entity_name}"
        self.status_code = status_code.value
        security_logger.error(f"Grant Security Error on User: {user.id} with roles: [{user.UserRoleList}] does not have {access} access on entity: {entity_name}")

class DefaultRolePermission:
    """_summary_
        DefaultRolePermission(
                to_role = Roles.tenant,
                can_delete = False,
                can_update = False,
                can_insert = False,
                can_read = False)
    Raises:
        GrantSecurityException: 
       
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
            :filter: where clause to be added to each select
        
        per calls from declare_security.py
      
    """

    grants_by_table : Dict[str, list['Grant']] = {}

    '''
    Dict keyed by Table name (obtained from class name), value is a (role, filter)
    '''

    def __init__(self, on_entity: DeclarativeMeta, 
        to_role: str = None,
        can_read: bool = True,
        can_insert: bool = True,
        can_update: bool = True,
        can_delete: bool = True,
        filter: object = None):
        
        
        self.class_name = on_entity
        self.class_name : str = on_entity._s_class_name  # type: ignore
        self.role_name : str = to_role
        self.filter = filter
        self.entity :DeclarativeMeta = on_entity 
        self.can_read = can_read
        self.can_insert = can_insert
        self.can_update = can_update
        self.can_delete = can_delete
        self.orm_execute_state = None # used by filter
        self.table_name : str = on_entity.__tablename__   # type: ignore
        
        self._entity_name:str =  on_entity._s_type # Class Name
        if self._entity_name is not None:
            if self._entity_name not in self.grants_by_table:
                Grant.grants_by_table[self._entity_name] = []
            Grant.grants_by_table[self._entity_name].append( self )
        
        
        def current_user():
            return Security.current_user() if Args.security_enabled else None
            
    @staticmethod
    def exec_grants(entity_name: str,crud_state: str, orm_execute_state: any = None) -> None:
        '''
        SQLAlchemy select event for current user's roles, append that role's grant filter to the SQL before execute 

        if you have a select() construct, you can add new AND things just calling .where() again.
        
        e.g. existing_statement.where(or_(f1, f2)) .

        u2 is a manager and a tenant
        '''
       
        
        if not Args.security_enabled:
            return
        
        user = Security.current_user()
        
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
        for each_role in DefaultRolePermission.grants_by_role:
            for each_user_role in user.UserRoleList:
                if each_role == each_user_role.role_name:
            #if Security.current_user_has_role(each_role):
                    for grant_role in DefaultRolePermission.grants_by_role[each_role]:
                        can_read = can_read or grant_role.can_read
                        can_insert = can_insert or grant_role.can_insert
                        can_delete = can_delete or grant_role.can_delete
                        can_update = can_update or grant_role.can_update
                        print(f"Grant on role: {each_role} Read: {can_read}, Update: {can_update}, Insert: {can_insert}, Delete: {can_delete}")
                    
        if entity_name in Grant.grants_by_table:
            grant_list = []
            grant_entity = None
            for each_grant in Grant.grants_by_table[entity_name]:
                grant_entity = each_grant.entity
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
            security_logger.debug(f"Grants applied for entity {entity_name}")
            if grant_entity is not None \
                and grant_list and crud_state == "is_select":
                grant_filter = or_(*grant_list)
                # apply filter(s) (additional where clause) for row security on select
                orm_execute_state.statement = orm_execute_state.statement.options(
                    with_loader_criteria(grant_entity,grant_filter))
        else:
            security_logger.debug(f"No Grants for entity {entity_name}")
            
        security_logger.debug(f"user:{user} crud:{crud_state},r:{can_read},c:{can_insert},u:{can_update},d:{can_delete}")   
        
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
def receive_do_orm_execute(orm_execute_state):
    "listen for the 'do_orm_execute' event from SQLAlchemy"
    if (
        Args.security_enabled
        and orm_execute_state.is_select
        and not orm_execute_state.is_column_load
        and not orm_execute_state.is_relationship_load
    ):            
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
