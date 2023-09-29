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


def run_build_and_wait_for_completion(input_parameters=None):
    # Create a client connection to Azure DevOps
    credentials = BasicAuthentication('', ACCESS_TOKEN)

    run_client = PipelinesClient(
        base_url=ORGANIZATION_URL,
        creds=credentials
    )

    print("Queuing the build...\n")
    try:
        pipeline_run = run_client.run_pipeline(
            project=PROJECT_NAME,
            pipeline_id=BUILD_DEFINITION_ID,
            run_parameters=input_parameters
        )
    except AzureDevOpsServiceError as exception:
        print(exception)
        return False

    # Get the run ID from the response
    run_id = pipeline_run.id
    # Get run URL, example format:
    # https://dev.azure.com/MyOrg/DevOps/_build/results?buildId=3644&view=logs
    run_url = ORGANIZATION_URL+"/"+PROJECT_NAME + \
        "/_build/results?buildId="+str(run_id)+"&view=logs"
    # print(run)   ### DEBUG
    print("A new build run was created with ID: {}\nBuild logs: {}\n".format(
        run_id, run_url))

    # Wait for the build to complete
    while True:
        try:
            run = run_client.get_run(
                project=PROJECT_NAME,
                pipeline_id=BUILD_DEFINITION_ID,
                run_id=run_id
            )
            if run.state == 'completed':
                result = run.result
                break
            print("Waiting for the build to complete...")
            time.sleep(15)
        except AzureDevOpsServiceError:
            pass

    if result == 'succeeded':
        print("The build has completed successfully!")
        return True
    else:
        print("The build has failed, please check its logs by following the URL:")
        print(run_url)
        return False


if __name__ == '__main__':
    # read input parameters from params.json file, or use empty params if file does not exist
    if os.path.exists('params.json'):
        with open('params.json', 'r') as f:
            params = json.load(f)
    else:
        params = ""

    # Call the function to run a build with the input parameters and wait for its completion
    succeeded = run_build_and_wait_for_completion(input_parameters=params)

    if succeeded:
        sys.exit(0)
    else:
        sys.exit(1)
