from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
)
from constructs import Construct


SSM_VPC_ID="/macos/vpc/id"

class MacOSCodeBuildStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket for storing CodeBuild artifacts
        artifact_bucket = s3.Bucket(self, "ArtifactBucket")

        # Define the IAM role that CodeBuild will assume
        codebuild_role = iam.Role(self, "CodeBuildRole",
                                  assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
                                  managed_policies=[
                                      iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"),
                                      iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess")
                                  ])


        vpc_id = ssm.StringParameter.value_from_lookup(self, SSM_VPC_ID)

        vpc = ec2.Vpc.from_lookup(self, "ImportedVpc",
            vpc_id=vpc_id
        )

        # Define a Security Group
        security_group = ec2.SecurityGroup(
            self, "macosFleetSecurityGroup",
            vpc=vpc,
            description="Allow SSH inbound traffic",
            allow_all_outbound=True  # Allow all outbound traffic
        )

        # Allow inbound traffic on port 22 (SSH) from anywhere
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),  # Allows traffic from anywhere
            connection=ec2.Port.tcp(22),  # Port 22 for SSH
            description="Allow SSH access from anywhere"
        )

        cfn_fleet = codebuild.CfnFleet(self, "MacOsFleet",
                                       base_capacity=2,
                                       environment_type="MAC_ARM",
                                       compute_type="BUILD_GENERAL1_MEDIUM",
                                       fleet_service_role=codebuild_role.role_arn,
                                       #fleet_vpc_config=codebuild.CfnFleet.VpcConfigProperty(
                                       #    security_group_ids=[security_group.id],
                                       #    subnets=["subnet-03fe6055097ce7a28"],
                                       #    vpc_id=vpc_id
                                       #),x
                                       #image_id="imageId",
                                       name="macosFleet",
                                       #overflow_behavior="overflowBehavior",
                                       #tags=[CfnTag(
                                       #    key="key",
                                       #    value="value"
                                       #)]
                                       )

        ## Create the macOS CodeBuild project
        #macos_project = codebuild.Project(self, "MacOSCodeBuildProject",
        #                                  source=codebuild.Source.git_hub(
        #                                      owner="your-github-username",
        #                                      repo="your-github-repository",
        #                                      webhook=True,
        #                                      webhook_filters=[
        #                                          codebuild.FilterGroup.in_event_of(
        #                                              codebuild.EventAction.PUSH).and_branch_is("main")]
        #                                  ),
        #                                  role=codebuild_role,
        #                                  environment=codebuild.BuildEnvironment(
        #                                      build_image=codebuild.LinuxBuildImage.from_code_build_image_id("aws/codebuild/macos-10.15"),
        #                                      compute_type=codebuild.ComputeType.LARGE,
        #                                      environment_variables=codebuild.BuildEnvironment.MAC_ARM,
        #                                      privileged=True  # Required for macOS builds
        #                                  ),
        #                                  build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
        #                                  environment_variables={
        #                                      'EXAMPLE_ENV_VAR': codebuild.BuildEnvironmentVariable(
        #                                          value='example_value'
        #                                      )
        #                                  },
        #                                  artifacts=codebuild.Artifacts.s3(
        #                                      bucket=artifact_bucket,
        #                                      include_build_id=True,
        #                                      package_zip=True
        #                                  )
        #                                  )

        # Outputs the CodeBuild project name
        #self.output_project_name = macos_project.project_name
