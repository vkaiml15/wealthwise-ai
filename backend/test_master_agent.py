from strands.models import BedrockModel
from strands.agent import Agent
import boto3
import os

def get_risk_agent():
    session = boto3.Session(profile_name='my-dev-profile')
    bedrock_client = session.client("bedrock-runtime", region_name="us-east-1")

    os.environ["AWS_PROFILE"] = "my-dev-profile"
    os.environ["AWS_REGION"] = "us-east-1"


    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        client=bedrock_client,  # ✅ explicitly give the client
    )

    agent = Agent(
        model=bedrock_model,
       
        system_prompt="""You are the Risk Profile Agent for WealthWise AI..."""
    )

    return agent

agent = get_risk_agent()
response = agent("Generate a sample risk summary.")
print(response)