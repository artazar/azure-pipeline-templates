import os
import sys
import time

from msrest.authentication import BasicAuthentication

from azure.devops.connection import Connection
from azure.devops.v7_1.build.build_client import BuildClient
from azure.devops.v7_1.build.models import Build

ORGANIZATION_URL = os.environ.get('ORGANIZATION_URL')
PROJECT_NAME = os.environ.get('PROJECT_NAME')
BUILD_DEFINITION_ID = int(os.environ.get('BUILD_DEFINITION_ID'))
SOURCE_BRANCH = os.environ.get('SOURCE_BRANCH')
ACCESS_TOKEN = os.environ.get('SYSTEM_ACCESSTOKEN')

print("Using configuration:\n\nORGANIZATION_URL is {}\nPROJECT_NAME is {}\nBUILD_DEFINITION_ID is {}\n".format(
    ORGANIZATION_URL, PROJECT_NAME, BUILD_DEFINITION_ID))


def run_build_and_wait_for_completion():
    # Create a client connection to Azure DevOps
    credentials = BasicAuthentication('', ACCESS_TOKEN)
    build_client = BuildClient(
        base_url=ORGANIZATION_URL,
        creds=credentials
    )

    # Get the build definition object
    build_definition = build_client.get_definition(
        definition_id=BUILD_DEFINITION_ID,
        project=PROJECT_NAME
    )

    # Create the build object with pullRequest reason
    build = Build(
        definition=build_definition,
        source_branch=SOURCE_BRANCH,
        reason='pullRequest',
    )

    # Queue the new build
    print("Queuing the build...\n")
    try:
        run = build_client.queue_build(build, PROJECT_NAME)
    except AzureDevOpsServiceError as exception:
        print(exception)
        return False

    # Get the run ID from the response
    run_id = run.id
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
            run = build_client.get_build(
                build_id=run_id,
                project=PROJECT_NAME
            )
            if run.status == 'completed':
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

    # Call the function to run a build with the input parameters and wait for its completion
    succeeded = run_build_and_wait_for_completion()

    if succeeded:
        sys.exit(0)
    else:
        sys.exit(1)
