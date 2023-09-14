--------------------------------------------------------
--  DDL for Trigger TRG_023NOTES_UPDATE_TMSTP
--------------------------------------------------------

  CREATE OR REPLACE EDITIONABLE TRIGGER "CSAMTEST_SCHEMA"."TRG_023NOTES_UPDATE_TMSTP" 
before insert or update on "CSAMTEST_SCHEMA"."ARI_023_NOTES"
for each row
begin
  if INSERTING then
    if :new.UPDATE_TMSTP is null then
      :new.UPDATE_TMSTP := SYSTIMESTAMP;
    end if;
  end if;

  if UPDATING then
    :new.UPDATE_TMSTP := SYSTIMESTAMP;
  end if;
end;

/
ALTER TRIGGER "CSAMTEST_SCHEMA"."TRG_023NOTES_UPDATE_TMSTP" ENABLE;
