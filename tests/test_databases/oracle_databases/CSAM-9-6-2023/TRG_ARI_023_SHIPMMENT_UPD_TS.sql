--------------------------------------------------------
--  DDL for Trigger TRG_ARI_023_SHIPMMENT_UPD_TS
--------------------------------------------------------

  CREATE OR REPLACE EDITIONABLE TRIGGER "CSAMTEST_SCHEMA"."TRG_ARI_023_SHIPMMENT_UPD_TS" 
before insert or update on "CSAMTEST_SCHEMA"."ARI_023_SHIPMENTS"
for each row
BEGIN
  if INSERTING then
    if :new.UPDATE_TMSTP is null then
      :new.UPDATE_TMSTP := SYSTIMESTAMP;
    end if;
  end if;

  if UPDATING then
    :new.UPDATE_TMSTP := SYSTIMESTAMP;
  end if;
END;

/
ALTER TRIGGER "CSAMTEST_SCHEMA"."TRG_ARI_023_SHIPMMENT_UPD_TS" ENABLE;
