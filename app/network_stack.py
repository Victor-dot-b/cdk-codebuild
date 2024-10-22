from aws_cdk import Stack, CfnOutput, aws_ssm as ssm
from aws_cdk.aws_ec2 import (
    Vpc,
    Subnet,
    SubnetType,
    IpAddresses,
    CfnInternetGateway,
    CfnVPCGatewayAttachment,
    CfnRouteTable,
    CfnRoute,
    CfnSubnetRouteTableAssociation
)
from constructs import Construct


SSM_VPC_ID="/macos/vpc/id"

class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        #ssm_vpc_id = self.node.try_get_context("SSM_VPC_ID")

        # Création du VPC
        vpc = Vpc(
            self,
            "pipeline-vpc",
            ip_addresses=IpAddresses.cidr("10.1.0.0/16"),
            max_azs=2,
            subnet_configuration=[],
        )
        
        # Store the VPC ID in SSM Parameter Store
        ssm.StringParameter(self, "VpcIdParameter",
            parameter_name=SSM_VPC_ID,
            string_value=vpc.vpc_id
        )

        # Create a CfnOutput for visibility
        CfnOutput(self, "VpcIdOutput", value=vpc.vpc_id, description="VPC ID")

        # Création d'un Subnet Public indépendant
        public_subnet = Subnet(
            self,
            "public1",
            vpc_id=vpc.vpc_id,
            cidr_block="10.1.1.0/24",
            availability_zone=vpc.availability_zones[0],
            map_public_ip_on_launch=True
        )

        # CfnOutput for the public subnet for visibility
        CfnOutput(self, "PublicSubnetIdOutput", value=public_subnet.subnet_id, description="Public Subnet ID")

        # *** Internet Gateway Creation and Attachment ***

        # Step 1: Create the Internet Gateway
        internet_gateway = CfnInternetGateway(self, "InternetGateway")

        # Step 2: Attach the Internet Gateway to the VPC
        gateway_attachment = CfnVPCGatewayAttachment(self, "VpcGatewayAttachment",
            vpc_id=vpc.vpc_id,
            internet_gateway_id=internet_gateway.ref
        )

        # *** Route Table Configuration ***

        # Step 3: Create a Route Table for the public subnet
        route_table = CfnRouteTable(self, "PublicRouteTable",
            vpc_id=vpc.vpc_id
        )

        # Step 4: Add a route to the Route Table that directs traffic to the Internet Gateway
        CfnRoute(self, "PublicRoute",
            route_table_id=route_table.ref,
            destination_cidr_block="0.0.0.0/0",  # Default route to the internet
            gateway_id=internet_gateway.ref  # Route traffic to the internet via the IGW
        )

        # Step 5: Associate the Route Table with the Public Subnet
        CfnSubnetRouteTableAssociation(self, "PublicSubnetAssociation",
            subnet_id=public_subnet.subnet_id,
            route_table_id=route_table.ref
        )

