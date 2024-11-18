import aws_cdk as core
import aws_cdk.assertions as assertions

from data_lack_stack.data_lack_stack_stack import DataLackStackStack

# example tests. To run these tests, uncomment this file along with the example
# resource in data_lack_stack/data_lack_stack_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DataLackStackStack(app, "data-lack-stack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
