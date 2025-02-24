import os
import sys
import runpy
import glob
import json
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, List
from dotmap import DotMap
from openai import OpenAI
from api_logic_server_cli.cli_args_project import Project
from api_logic_server_cli.genai.genai_svcs import (
    get_prompt_messages_from_dirs,
    select_messages,
    get_create_prompt__with_inserts,
    get_prompt_you_are,
    call_chatgpt,
    fix_and_write_model_file,
    get_manager_path,
    remove_als_from_models_py,
    read_and_expand_prompt,
    Rule,
    rebuild_test_data_for_project,
    WGResult
)
import create_from_model.api_logic_server_utils as utils
from  genai.json2rules import json2rules

log = logging.getLogger(__name__)


class GenAIUtils:
    """
    Provides functionality to fix, import, or submit projects to ChatGPT-like services.
    Capable of gathering and processing models, rules, and test data to adapt user projects.
    """

    def __init__(
        self,
        project: Project,
        using: str,
        genai_version: str,
        fixup: bool,
        submit: bool,
        import_genai: bool,
        import_resume: bool = False,
        rebuild_test_data: bool = False,
        response: str = None
    ):
        """
        Initialization for GenAIUtils.

        :param project: The Project object with CLI arguments/config.
        :param using: Directory path for data to process (e.g., docs or fixup folder).
        :param genai_version: The model/version for the AI service.
        :param fixup: Whether to fix project issues by analyzing models and rules.
        :param submit: Whether to submit directory content to the AI service.
        :param import_genai: Whether to import a wg-project into the dev-project.
        :param import_resume: Resume importing if partial data already exists.
        """

        self.project = project
        self.fixup = fixup
        self.using = using
        self.genai_version = genai_version
        self.submit = submit
        self.import_genai = import_genai
        self.import_resume = import_resume
        self.rebuild_test_data = rebuild_test_data
        self.response = response

    def run(self) -> None:
        """Decides which operation to perform based on the provided flags."""
        if self.fixup:
            self.fixup_project()
        elif self.submit:
            self.submit_project()
        elif self.import_genai:
            self.import_genai_project()
        elif self.rebuild_test_data:
            self.rebuild_test_data_project()
        else:
            log.info(".. no action specified")

    def submit_project(self) -> None:
        """
        Submits directory contents to ChatGPT or similar services for processing.
        Example command (from CLI): als genai_utils --submit --using=docs/fixup
        """
        log.info(f".. submitting: {self.using}")
        self.messages = get_prompt_messages_from_dirs(self.using)
        self.messages_chatgpt = []
        for each_path, each_message in self.messages:  # get rid of the path
            self.messages_chatgpt.append(each_message)

        api_version = f"{self.genai_version}"
        start_time = time.time()
        db_key = os.getenv("APILOGICSERVER_CHATGPT_APIKEY", "")
        model = api_version if api_version else os.getenv("APILOGICSERVER_CHATGPT_MODEL", "gpt-4o-2024-08-06")
        self.resolved_model = model

        call_chatgpt(api_version=model,
                        messages=self.messages_chatgpt,
                        using=self.using)

        log.info(
            f"ChatGPT ({str(int(time.time() - start_time))} secs) - response at:"
            " system/genai/temp/chatgpt_original.response"
        )


    def rebuild_test_data_project(self) -> None:
        """rebuilds test data from the response.json file by calling response2code.py
        """        
        rebuild_test_data_for_project(project = self.project, response = self.response)


    def fixup_project(self) -> None:
        """
        Fixes project issues by updating the Data Model and Test Data:
          1. Collects the latest model, rules, and test data from the --using directory.
          2. Calls ChatGPT (or similar) to resolve missing columns or data in the project.
          3. Saves the fixup request/response under a 'fixup' folder.
        
        Example: 
        als genai-utils --fixup --using=genai/fixup
        mgr 
            * comment out the balance
            * run: GenAI - FixUp f1 Samples/nw_sample
        """

        manager_path = get_manager_path()
        fixup_prompt_path = manager_path.joinpath("system/genai/prompt_inserts/fixup.prompt")
        with open(fixup_prompt_path, "r") as file:
            f_fixup_prompt = file.read()

        def add_rule(messages_out: Dict[str, List[Rule]], value: List[Rule]) -> None:
            """
            Adds rules from the parsed message to the messages_out dictionary.
            """
            if isinstance(value, list) and not value:
                log.debug(".. fixup ignores: rules [] ...")
                return
            if messages_out["rules"] is None:
                messages_out["rules"] = value
                log.debug(f".. .. fixup/add_rule sees first rules: {str(value)[:50]}...")
            else:
                log.debug(f".. .. fixup/add_rule sees more rules: {str(value)[:50]}...")
                messages_out["rules"].append(value)

        def message_selector(messages_out: Dict[str, str], message: Dict, each_message_file: str) -> None:
            """
            Updates messages_out with the latest rules, models and test data (for JSON content).
            """
            message_obj = json.loads(message["content"])

            if isinstance(message_obj, list):
                return  # Not expected for fixup handling

            for key, value in message_obj.items():
                if key not in messages_out:
                    continue
                if key in ["rules", "models"]:
                    if isinstance(value, list):
                        add_rule(messages_out, value)
                elif key == "test_data_rows":
                    # Intentionally skip adding test data here (may want to handle differently).
                    pass
                else:
                    messages_out[key] = value

        def create_fixup_files(this_ref: "GenAIUtils") -> None:
            """
            Moves request.json and response.json to fixup folder, then creates
            separate parts for models, rules, test data, and the fixup command prompt.
            """
            fixup_dir = Path(this_ref.using).joinpath("fixup")
            request_path = Path(this_ref.using).joinpath("request.json")
            response_path = Path(this_ref.using).joinpath("response.json")

            new_file_path = fixup_dir.joinpath("request_fixup.json")
            shutil.move(request_path, new_file_path)

            new_file_path = fixup_dir.joinpath("response_fixup.json")
            shutil.move(response_path, new_file_path)

            you_are_content = get_prompt_you_are()["content"]
            with open(fixup_dir.joinpath("1_you-are.prompt"), "w") as file:
                file.write(you_are_content)

            models_data = {"models": this_ref.fixup_response.models}
            with open(fixup_dir.joinpath("2_models.response"), "w") as file:
                json.dump(models_data, file, indent=4)

            rules_data = {"rules": this_ref.fixup_response.rules}
            with open(fixup_dir.joinpath("3_rules.response"), "w") as file:
                json.dump(rules_data, file, indent=4)

            test_data_rows_data = {"test_data_rows": this_ref.fixup_response.test_data_rows}
            with open(fixup_dir.joinpath("4_test_data_rows.response"), "w") as file:
                json.dump(test_data_rows_data, file, indent=4)

            with open(fixup_dir.joinpath("5_fixup_command.response"), "w") as file:
                file.write(this_ref.fixup_command)

        os.makedirs(Path(self.using).joinpath("fixup"), exist_ok=True)
        messages_out = {"models": None, "rules": None}

        self.import_request = [get_prompt_you_are()]
        all_messages = get_prompt_messages_from_dirs(self.using)
        select_messages(all_messages, messages_out, message_selector)

        logic_path = Path(self.using).joinpath("logic")
        if logic_path.is_dir():
            logic_messages = get_prompt_messages_from_dirs(str(logic_path))
            select_messages(logic_messages, messages_out, message_selector)

        self.models_and_rules = {
            "role": "user",
            "content": json.dumps(messages_out)
        }
        self.import_request.append(self.models_and_rules)
        self.fixup_command, _ = get_create_prompt__with_inserts(raw_prompt=f_fixup_prompt)
        fixup_command_prompt = {"role": "user", "content": self.fixup_command}
        self.import_request.append(fixup_command_prompt)

        self.response_str = call_chatgpt(
            messages=self.import_request,
            api_version=self.genai_version,
            using=self.using
        )
        self.fixup_response = DotMap(json.loads(self.response_str))

        create_fixup_files(self)
        log.info(f".. fixup complete: {self.using}/fixup")
        log.info(f".. .. next step: cd <manager>  eg, cd ..")
        log.info(f".. .. and then, create fixed project: als genai --repaired-response={self.project.project_name}/{self.using}/fixup/response_fixup.json --project-name=fixed_project")

    def import_genai_project(self) -> None:
        """
        Imports a wg-project (--using from WebGenAI export) into the current dev-project.
          1. Merges models from wg-project and dev-project.
          2. Produces create_db_models.py (and SQLite DB) to replace dev-project /database/db.sqlite.
          3. Example usage: als genai-utils --import-genai --using=../wg_genai_demo_no_logic_fixed_from_CLI
        """

        def get_wg_project_models_from_docs_export(path_wg: Path) -> List[Dict]:
            """
            Return models from a wg-project's export.json.

            :param path_wg: Path to the wg-project root folder.
            """
            export_path = path_wg.joinpath("docs/export/export.json")
            with open(export_path, "r") as file:
                json_data = json.load(file)
            return json_data["models"]

        def get_dev_project_models_from_database_models_py(path_dev: Path) -> Dict[str, str]:
            """
            Retrieves existing models.py content from the dev-project.

            :param path_dev: Path to the developer project containing models.py
            """
            dev_models_path = path_dev.joinpath("database/models.py")
            with open(dev_models_path, "r") as file:
                dev_models = file.read()
            return {"existing_models": dev_models}

        def create_db_and_rebuild_project_from_db(this_ref: "GenAIUtils") -> None:
            """
            Creates the dev DB and models.py from import data:
              1. Create create_db_models_no_als.py from the merged models.
              2. Generate an SQLite database for the dev-project.
              3. Run rebuild-from-database to finalize the updated project structure.
            """
            
            add_create_all = """
print('*** docs/import/create_db_models here ***')
engine = create_engine('sqlite:///docs/import/create_db_models.sqlite')

Base.metadata.create_all(engine)"""

            # Create the new SQLite DB using the merged models in docs/import/create_db_models.py
            new_db_path = this_ref.path_dev_import.joinpath("create_db_models.sqlite")
            create_db_models_path = this_ref.path_dev_import.joinpath("create_db_models.py")
            utils.replace_string_in_file(
                search_for="# end of model classes",
                replace_with=add_create_all,
                in_file=create_db_models_path
            )
            utils.replace_string_in_file(
                search_for="mgr_db_loc = True",
                replace_with="mgr_db_loc = False",
                in_file=create_db_models_path
            )
            
            runpy.run_path(path_name=create_db_models_path)  # Create the new DB by running dev_demo_no_logic_fixed/docs/import/create_db_models.py
            assert new_db_path.exists(), "FIXME failed to create new db using {create_db_models_path}"
            # dev_demo_no_logic_fixed/docs/import/create_db_models.sqlite
            shutil.copy(new_db_path, 
                        this_ref.path_dev.joinpath("database/db.sqlite"))  # Copy to dev-project ..dev_demo_no_logic_fixed

            # Rebuild the project from the newly created database
            os.environ["APILOGICPROJECT_NO_FLASK"] = "None"  # introspection requires safrs properties
            this_ref.project.command = "rebuild-from-database"
            this_ref.project.db_url = f"sqlite:///{new_db_path}"
            this_ref.project.project_name = "."
            this_ref.project.create_project()

        def setup_import_dir():
            """create the docs/import dir, and delete files from prior run...
            """            
            self.path_dev_import = self.path_dev.joinpath("docs/import")
            os.makedirs(self.path_dev_import, exist_ok=True)
            if Path(self.path_dev_import.joinpath("create_db_models.py")).is_file():
                os.remove(Path(self.path_dev_import.joinpath("create_db_models.py"))) 
            if Path(self.path_dev_import.joinpath("create_db_models.sqlite")).is_file():
                os.remove(Path(self.path_dev_import.joinpath("create_db_models.sqlite"))) 
            if Path(self.path_dev_import.joinpath("request.json")).is_file():
                os.remove(Path(self.path_dev_import.joinpath("request.json"))) 
            pass

        def add_web_genai_logic(this_ref: "GenAIUtils") -> None:
            """
            Adds or updates WebGenAI logic (if any) into the dev-project's logic/discovery folder.
            """
            logic_discovery_path = this_ref.path_dev.joinpath("logic/logic_discovery")
            os.makedirs(logic_discovery_path, exist_ok=True)
            export_json = self.path_wg.joinpath("docs/export/export.json")
            if export_json.is_file():
                try:
                    json2rules(export_json, logic_discovery_path)
                except Exception as exc:
                    log.error(f"Failed to import logic from {export_json}: {exc}")


        ##############################
        # Main import_genai_project
        ##############################

        log.info(f"import_genai from genai export at: {self.using}")
        self.path_wg = Path(self.using)
        if not self.path_wg.is_dir():
            raise FileNotFoundError(f"Missing genai-import project directory: {self.using}")

        self.path_dev = Path(os.getcwd())
        setup_import_dir()
        os.environ["APILOGICPROJECT_NO_FLASK"] = "1"  # no automatic data loading
        
        if self.import_resume:
            log.debug(".. import_genai: rebuild-from-response")
            response_json = self.path_dev_import.joinpath("response.json")
            with open(response_json, "r") as file:
                import_response = json.load(file)
            self.import_response = DotMap(import_response)
            fix_and_write_model_file(response_dict=self.import_response, save_dir=self.path_dev_import)
        else:
            manager_path = get_manager_path()
            import_prompt_path = manager_path.joinpath("system/genai/prompt_inserts/import.prompt")
            f_import_prompt = read_and_expand_prompt(import_prompt_path)

            self.import_request = []
            self.import_request.append(get_prompt_you_are())

            wg_models = {"models": get_wg_project_models_from_docs_export(self.path_wg)}
            self.import_request.append({"role": "user", "content": json.dumps(wg_models)})

            dev_models = get_dev_project_models_from_database_models_py(self.path_dev)
            self.import_request.append({"role": "user", "content": json.dumps(dev_models)})

            self.import_command, _ = get_create_prompt__with_inserts(
                raw_prompt=f_import_prompt,
                arg_prompt_inserts="*"
            )
            import_command_prompt = {"role": "user", "content": self.import_command}
            self.import_request.append(import_command_prompt)

            self.response_str = call_chatgpt(
                messages=self.import_request,
                api_version=self.genai_version,
                using=self.path_dev_import
            )
            self.import_response = DotMap(json.loads(self.response_str))

            fix_and_write_model_file(response_dict=self.import_response, save_dir=self.path_dev_import)

        create_db_and_rebuild_project_from_db(self)
        add_web_genai_logic(self)
        
        log.info(f".. import complete: {self.using}/import\n")