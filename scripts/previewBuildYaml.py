import os
import sys
import time
import json

from msrest.authentication import BasicAuthentication

from azure.devops.v7_1.pipelines.pipelines_client import PipelinesClient
from azure.devops.exceptions import AzureDevOpsServiceError

# Read the organization URL, project name, build definition ID, and access token from environment variables
ORGANIZATION_URL = os.environ.get('ORGANIZATION_URL')
PROJECT_NAME = os.environ.get('PROJECT_NAME')
BUILD_DEFINITION_ID = int(os.environ.get('BUILD_DEFINITION_ID'))
ACCESS_TOKEN = os.environ.get('SYSTEM_ACCESSTOKEN')

print("Using configuration:\n\nORGANIZATION_URL is {}\nPROJECT_NAME is {}\nBUILD_DEFINITION_ID is {}\n".format(
    ORGANIZATION_URL, PROJECT_NAME, BUILD_DEFINITION_ID))

def previewYaml(input_parameters=None):
    # Create a client connection to Azure DevOps
    credentials = BasicAuthentication('', ACCESS_TOKEN)

    run_client = PipelinesClient(
        base_url=ORGANIZATION_URL,
        creds=credentials
    )

    print("Doing YAML preview...\n")
    try:
        pipeline_run = run_client.preview(
            project=PROJECT_NAME,
            pipeline_id=BUILD_DEFINITION_ID,
            run_parameters=input_parameters
        )
        print("The generated YAML content:\n")
        print(pipeline_run.final_yaml)
        return True
    except AzureDevOpsServiceError as exception:
        print(exception)
        return False

if __name__ == '__main__':
    # read input parameters from params.json file, or use empty params if file does not exist
    if os.path.exists('params.json'):
        with open('params.json', 'r') as f:
            params = json.load(f)
    else:
        params = ""

    # Call the function to run a build with the input parameters and wait for its completion
    succeeded = previewYaml(input_parameters=params)

    if succeeded:
        sys.exit(0)
    else:
        sys.exit(1)
