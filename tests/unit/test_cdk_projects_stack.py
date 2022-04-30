import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_lambda.cdk_lambda_stack import CdkProjectsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_projects/cdk_projects_stack.py


def test_sqs_queue_created():
    app = core.App()
    stack = CdkProjectsStack(app, "cdk-projects")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
