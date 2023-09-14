-- list schemas

select * from all_users;

alter session set current_schema = HR;

SELECT table_name FROM all_tables WHERE owner = 'HR';

select sys_context('userenv','sessionid') Session_ID from dual;