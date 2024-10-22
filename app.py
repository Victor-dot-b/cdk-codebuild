#!/usr/bin/env python3
import os

import aws_cdk as cdk

from app.app_stack import AppStack
from app.network_stack import NetworkStack
from app.codebuild_stack import MacOSCodeBuildStack


app = cdk.App()
env = cdk.Environment(account='351334432989', region='eu-central-1')
NetworkStack(app, "pipeline-network", env=env)
MacOSCodeBuildStack(app, "pipeline-codebuild", env=env)

app.synth()
