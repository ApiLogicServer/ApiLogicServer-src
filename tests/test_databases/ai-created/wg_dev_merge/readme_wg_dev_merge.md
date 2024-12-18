The Diego Lo Giudice challenge: coordinate parallel dev streams
    WG_Team: new rules & attributes
        Implicit Assumption: WG is not a day-1-only pilot... it lives for a while...
    Dev_Team: their own new rules & attributes, using either genai and/or alembic...

Groundrules:
    No Dev_Team -> WG_Team integration (just deploy Dev_Team version, and use)
        Dev team code cannot be integrated into WG - dependencies, libs, integration, ...
    WG_Team - serial dev (as now)
    WG_Team logic files are separate from Dev_Team (eg, using logic/discovery)
    sqlite only, for now (presume upgrade to 'some other db' is doable later)
        Tyler, what were the issues you mentioned in sqlite that forced you to use PG?
    All Dev_Team and logic generations are finished before merge-G

Key Idea: is 'source of truth' the WG_Results json data, or the .py files?
    Seems like it comes to what each group sees and edits:
        Dev_Team: .py 
        WG_Team: WG_Results json data (via Nat Lang) 
            Are these maintained in WG db?  Seems like they'd have to be...
                It's all the WG_Team sees.
                And they need to be able to delete them.
                Does this hold true over multiple iterations?
    If this is true, I need to verify that GenAI can merge json/py data models.
        Probably a fixup bug (is ignoring .py).
        Note our big advantage is the logic merges automatically, without worrying about order.
            That's because execution is automatically ordered by dependencies.

Base Project is GenAI_no_logic.  No rule-based attributes.

WG adds standard rules - Customer.balance etc.

Dev (wg_genai_demo_no_logic_fixed) adds Product.carbon_neutral.