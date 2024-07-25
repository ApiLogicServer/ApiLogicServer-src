import importlib
from pathlib import Path
import logging

app_logger = logging.getLogger(__name__)

def discover_models():
    """
    Discover models in the discovery directory
    """
    import os
    models = []
    models_path = Path(__file__).parent
    for root, dirs, files in os.walk(models_path):
        for file in files:
            if file.endswith(".py"):
                spec = importlib.util.spec_from_file_location("module.name", models_path.joinpath(file))
                if file.endswith("auto_discovery.py"):
                    pass
                else:
                    models.append(file)
                    each_model = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(each_model)  # runs "bare" module code (e.g., initialization)
    app_logger.info(f"..discovered models: {models}")
    return
