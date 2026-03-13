import importlib
from pathlib import Path
import logging

app_logger = logging.getLogger(__name__)

def discover_services(app, api, project_dir, swagger_host: str, PORT: str):
    """
    Discover services in the services directory
    """
    import os
    method_decorators : list = []
    services = []
    services_path = Path(__file__).parent
    for root, dirs, files in os.walk(services_path):
        for file in files:
            if file.endswith(".py"):
                spec = importlib.util.spec_from_file_location("module.name", services_path.joinpath(file))
                if file.endswith("auto_discovery.py"):
                    pass
                else:
                    services.append(file)
                    each_service = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(each_service)  # runs "bare" module code (e.g., initialization)
                    each_service.add_service(app, api, project_dir, swagger_host, PORT, method_decorators)  # invoke create function
    app.logger.info(f"..discovered services: {services}")
    return
