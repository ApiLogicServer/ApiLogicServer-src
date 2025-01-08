this test fails, because appears that flask/safrs included.  Cannot see why.

note: it often fails because it drops many tables (in violation of the prompt)... just re-run.

log shown below.

recreate using the run config "Create students_classes_informal, iteration / informal logic", or

als genai --test-data-rows=4 --temperature=0.7 --using=system/genai/examples/students_classes_informal_iteration --project-name=students_classes_informal
