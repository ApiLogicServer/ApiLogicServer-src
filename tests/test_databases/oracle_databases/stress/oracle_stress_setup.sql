# for ref: oracle+oracledb://hr:tiger@localhost:1521/?service_name=ORCL


create user STRESS identified by tiger;

GRANT CONNECT, RESOURCE, DBA TO STRESS;

connect STRESS;

SELECT table_name FROM all_tables WHERE owner = 'HR';

SELECT table_name FROM all_tables WHERE owner = 'STRESS';



create user VAL identified by tiger;

GRANT CONNECT, RESOURCE, DBA TO VAL;

connect VAL;

SELECT table_name FROM all_tables WHERE owner = 'VAL';

drop sequence "STRESS_TIMESTAMP_WITH_LTZ_SEQ";
drop table "STRESS_TIMESTAMP_WITH_LOCAL_TZ";

create sequence "STRESS_TIMESTAMP_WITH_LTZ_SEQ" increment by 1 start with 1 nocache;
create table "STRESS_TIMESTAMP_WITH_LOCAL_TZ" (  "id" integer not null ,"timestamp_default" timestamp with local time zone ,"timestamp_0" timestamp(0) with local time zone ,"timestamp_1" timestamp(1) with local time zone ,"timestamp_2" timestamp(2) with local time zone ,"timestamp_3" timestamp(3) with local time zone ,"timestamp_4" timestamp(4) with local time zone ,"timestamp_5" timestamp(5) with local time zone ,"timestamp_6" timestamp(6) with local time zone ,"timestamp_7" timestamp(7) with local time zone ,"timestamp_8" timestamp(8) with local time zone ,"timestamp_9" timestamp(9) with local time zone);
alter table "STRESS_TIMESTAMP_WITH_LOCAL_TZ"  add constraint "PK_STRESS_TIMESTAMP_WITH_LTZ"  primary key ("id");

insert into STRESS_TIMESTAMP_WITH_LOCAL_TZ ("id", "timestamp_default", "timestamp_0", "timestamp_1", "timestamp_2", "timestamp_3", "timestamp_4", "timestamp_5", "timestamp_6", "timestamp_7", "timestamp_8", "timestamp_9") values ("STRESS".STRESS_TIMESTAMP_WITH_LTZ_SEQ.nextval, current_timestamp, current_timestamp(0), current_timestamp(1), current_timestamp(2), current_timestamp(3), current_timestamp(4), current_timestamp(5), current_timestamp(6), current_timestamp(7), current_timestamp(8), current_timestamp(9));
insert into STRESS_TIMESTAMP_WITH_LOCAL_TZ ("id", "timestamp_default", "timestamp_0", "timestamp_1", "timestamp_2", "timestamp_3", "timestamp_4", "timestamp_5", "timestamp_6", "timestamp_7", "timestamp_8", "timestamp_9") values ("STRESS".STRESS_TIMESTAMP_WITH_LTZ_SEQ.nextval, TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789', TIMESTAMP '1999-12-31 23:59:59.123456789');
insert into STRESS_TIMESTAMP_WITH_LOCAL_TZ ("id", "timestamp_default", "timestamp_0", "timestamp_1", "timestamp_2", "timestamp_3", "timestamp_4", "timestamp_5", "timestamp_6", "timestamp_7", "timestamp_8", "timestamp_9") values ("STRESS".STRESS_TIMESTAMP_WITH_LTZ_SEQ.nextval, TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12', TIMESTAMP '1999-12-31 23:59:59.123456789 -01:12');


