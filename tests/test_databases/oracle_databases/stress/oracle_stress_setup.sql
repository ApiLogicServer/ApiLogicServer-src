1. create user & schema
    https://apilogicserver.github.io/Docs/Database-Docker/#new-userdatabase

2. load db from oracle_stress.sql

3. Run Config: ORACLE-STRESS, or
    ApiLogicServer create --project_name=oracle_stress --db_url='oracle+oracledb://stress:tiger@localhost:1521/?service_name=ORCL'



Failing with invalid chars... :
===============================

Genned
        SELECT "STRESS_AllChars".parent AS "STRESS_AllChars_parent", "STRESS_AllChars".description AS "STRESS_AllChars_description" 
FROM "STRESS_AllChars" ORDER BY "STRESS_AllChars".description
 OFFSET 0 ROWS
 FETCH FIRST 25 ROWS ONLY

manual sql works by force-quoting the attr names:
SELECT "STRESS_AllChars"."PARENT" AS "STRESS_AllChars_parent", "STRESS_AllChars"."description" AS "STRESS_AllChars_description" 
FROM "STRESS_AllChars" ORDER BY "STRESS_AllChars"."description"
 OFFSET 0 ROWS
 FETCH FIRST 25 ROWS ONLY;

which is forced by using quote=True on the column ctor
    https://github.com/sqlalchemy/sqlalchemy/discussions/10814



__tablename__ has odd mixed case
================================

STRESS_BINARY_DOUBLE --> StressBinaryDouble.__tablename__ = 'stress_binary_double'

STRESS_AllChars --> STRESSAllChar.__tablename__ = 'STRESS_AllChars'
