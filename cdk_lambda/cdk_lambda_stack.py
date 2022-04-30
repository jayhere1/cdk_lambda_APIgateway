import os

from aws_cdk import CfnParameter, Duration, Stack
from aws_cdk import aws_apigateway as apigateway  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

PYTHON_RUNTIME = _lambda.Runtime.PYTHON_3_9
STACK_NAME = os.environ.get("STACK_NAME", "My-Stack")
API_STAGE = os.environ.get("API_STAGE", "api")
AWS_REGION = os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"])
AWS_ACCOUNT = os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"])


class CdkProjectsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        REPO_VERSION = CfnParameter(self, "REPO_VERSION").value_as_string

        # The code that defines your stack goes here
        my_vpc = ec2.Vpc.from_lookup(self, "My-Vpc", vpc_name="test_VPC")
        my_sg = ec2.SecurityGroup.from_security_group_id(
            self, "My-Sg", "My-security=group-id", mutable=False)

        # Roles
        lambda_role = iam.Role(
            scope=self,
            id=f"role_{STACK_NAME}",
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            )]
        )

        api_role = iam.Role(self, 'apirole', assumed_by=iam.ServicePrincipal(
            "apigateway.amazonaws.com"))

        api_role.add_to_policy(iam.PolicyStatement(
            resources=["*"], actions=["lambda:InvoleFunction"]))

        cloudwatch_policy_statement = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, sid="AllowCloudWatch", resources=[f"arn:aws:logs:{AWS_REGION}:\
            {AWS_ACCOUNT}:log-group:/aws/lambda/{STACK_NAME}_lambda"])
    
        iam.Policy(self, "Policy", policy_name="lambda_policy",
                   roles=[lambda_role], statements=[cloudwatch_policy_statement])

        repo = ecr.Repository.from_repository_name(self, "Repo", repository_name="My-repo")

        _lambda.DockerImageFunction(
            self,
            f"{STACK_NAME}_lambda",
            code=_lambda.DockerImageCode.from_ecr(repository=repo, tag_or_digest=REPO_VERSION),
            memory_size=2048,
            timeout=Duration.seconds(60),
            environment=dict(
                PATH="/opt"
            ),
            role=lambda_role,
            vpc=my_vpc,
            allow_public_subnet=True,
            security_groups=[my_sg]
        )

        api_spec = "openAPIspec.yml"

        api = apigateway.SpecRestApi(
            self,
            f"{STACK_NAME}_api",
            role=api_role,
            api_definition=apigateway.APIDefinition.from_inline(api_spec)
        )

        deployment = apigateway.Deployment(self, "deployment", api=api)

        apigateway.Stage(self, "apistage", deployment=deployment, stage_name=API_STAGE)
