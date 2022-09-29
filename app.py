import aws_cdk as cdk

import constants
from toolchain import Toolchain

app = cdk.App()


# Toolchain stack (defines the continuous deployment pipeline)
Toolchain(
    app,
    constants.APP_NAME + "Toolchain",
    env=cdk.Environment(account="018357457516", region="us-west-2"),
)

app.synth()
