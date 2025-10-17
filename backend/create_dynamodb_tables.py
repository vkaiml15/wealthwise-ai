"""
Script to create DynamoDB tables for WealthWise AI
Run this once to set up your database
"""

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

def create_users_table():
    """Create WealthWiseUsers table"""
    try:
        table = dynamodb.create_table(
            TableName='WealthWiseUsers',
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName='WealthWiseUsers')
        print("✅ WealthWiseUsers table created successfully!")
        
    except Exception as e:
        if 'ResourceInUseException' in str(e):
            print("⚠️  WealthWiseUsers table already exists")
        else:
            print(f"❌ Error creating WealthWiseUsers table: {str(e)}")

def create_portfolios_table():
    """Create WealthWisePortfolios table"""
    try:
        table = dynamodb.create_table(
            TableName='WealthWisePortfolios',
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName='WealthWisePortfolios')
        print("✅ WealthWisePortfolios table created successfully!")
        
    except Exception as e:
        if 'ResourceInUseException' in str(e):
            print("⚠️  WealthWisePortfolios table already exists")
        else:
            print(f"❌ Error creating WealthWisePortfolios table: {str(e)}")

def main():
    print("🚀 Creating DynamoDB tables for WealthWise AI...")
    print("-" * 50)
    
    create_users_table()
    create_portfolios_table()
    
    print("-" * 50)
    print(os.getenv('AWS_REGION', 'us-east-1'))
    print(os.getenv('AWS_ACCESS_KEY_ID'))
    print("✨ Setup complete!")

    print("\nYou can now run: python main.py")

if __name__ == "__main__":
    main()