
import os
import time
from google.cloud import spanner
from google.api_core.exceptions import NotFound

def create_instance():
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "emulator-test-project")
    instance_id = "spanner-django-python-systest"
    
    print(f"Checking instance {project}/{instance_id}...")
    client = spanner.Client(project=project)
    instance = client.instance(instance_id)

    try:
        instance.reload()
        print("Instance exists.")
    except NotFound:
        print("Instance not found. Creating...")
        config_name = f"{client.project_name}/instanceConfigs/emulator-config"
        instance = client.instance(instance_id, configuration_name=config_name)
        operation = instance.create()
        operation.result(120)
        print("Instance created.")

if __name__ == "__main__":
    create_instance()
