import json
import pathlib
from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_codebuild as codebuild
from aws_cdk import pipelines
from constructs import Construct

GITHUB_CONNECTION_ARN = (
    "arn:aws:codestar-connections:us-west-2:"
    "018357457516:connection/a3e6f47e-23bc-43f9-83e0-c84a244dfe57"
)
GITHUB_OWNER = "DharmSonariya"
GITHUB_REPO = "experiment"
GITHUB_TRUNK_BRANCH = "main"
PRODUCTION_ENV_NAME = "Production"
PRODUCTION_ENV_ACCOUNT = "018357457516"
PRODUCTION_ENV_REGION = "us-west-2"


class Toolchain(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        source = pipelines.CodePipelineSource.connection(
            GITHUB_OWNER + "/" + GITHUB_REPO,
            GITHUB_TRUNK_BRANCH,
            connection_arn=GITHUB_CONNECTION_ARN,
        )
        build_spec = {"phases": {"install": {"runtime-versions": {"python": "3.7"}}}}
        synth = pipelines.CodeBuildStep(
            "Synth",
            input=source,
            partial_build_spec=codebuild.BuildSpec.from_object(build_spec),
            install_commands=["./scripts/install-deps.sh"],
            commands=["./scripts/run-tests.sh", "npx cdk synth"],
            primary_output_directory="cdk.out",
        )
        pipelines.CodePipeline(
            self,
            "Pipeline",
            cli_version=Toolchain._get_cdk_cli_version(),
            cross_account_keys=True,
            docker_enabled_for_synth=True,
            publish_assets_in_parallel=False,
            synth=synth,
        )

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.joinpath("package.json").resolve()
        )
        with open(package_json_path, encoding="utf_8") as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version
