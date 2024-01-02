create user & schema
    https://apilogicserver.github.io/Docs/Database-Docker/#new-userdatabase

load db from oracle_stress.sql


Run Config: ORACLE-STRESS, or
    ApiLogicServer create --project_name=oracle_stress --db_url='oracle+oracledb://stress:tiger@localhost:1521/?service_name=ORCL'

Failing with invalid chars... :

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