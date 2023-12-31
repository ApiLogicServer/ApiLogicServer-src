--------------------------------------------------------
--  DDL for Table ARI_023_NOTES
--------------------------------------------------------

  CREATE TABLE "CSAMTEST_SCHEMA"."ARI_023_NOTES" 
   (	"NOTESID" NUMBER(9,0) GENERATED BY DEFAULT ON NULL AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 13467 NOCACHE  NOORDER  NOCYCLE  NOKEEP  NOSCALE , 
	"SHIPID" NUMBER(9,0), 
	"NOTES" VARCHAR2(200 BYTE), 
	"CREATE_TMSTP" TIMESTAMP (6) WITH TIME ZONE DEFAULT systimestamp, 
	"UPDATE_TMSTP" TIMESTAMP (6) WITH TIME ZONE DEFAULT systimestamp, 
	"CREATE_UID" VARCHAR2(10 BYTE) DEFAULT 999999, 
	"UPDATE_UID" VARCHAR2(10 BYTE) DEFAULT 999999
   ) SEGMENT CREATION IMMEDIATE 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "CSAMTEST_TS"   NO INMEMORY ;
  GRANT DELETE ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_ADMIN_ROLE";
  GRANT INSERT ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_ADMIN_ROLE";
  GRANT SELECT ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_ADMIN_ROLE";
  GRANT UPDATE ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_ADMIN_ROLE";
  GRANT SELECT ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_RO_ROLE";
  GRANT DELETE ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_APP";
  GRANT INSERT ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_APP";
  GRANT SELECT ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_APP";
  GRANT UPDATE ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_APP";
  GRANT SELECT ON "CSAMTEST_SCHEMA"."ARI_023_NOTES" TO "CSAMTEST_RO_APP";
