#!/usr/bin/env python3
"""
WealthWise AI - Credential Verification Script
Run this BEFORE starting the backend to verify AWS credentials
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🔍 WealthWise AI - Credential Verification")
print("=" * 60)
print()

# Step 1: Check if .env file exists
env_file = Path('.env')
if not env_file.exists():
    print("❌ PROBLEM: .env file not found in current directory!")
    print()
    print("📍 Current directory:", os.getcwd())
    print()
    print("✅ SOLUTION:")
    print("   1. Make sure you're in the 'backend' directory")
    print("   2. Create a file named '.env' (with the dot)")
    print("   3. Add your AWS credentials to it")
    print()
    print("Example .env file:")
    print("-" * 60)
    print("AWS_ACCESS_KEY_ID=ASIA1234567890")
    print("AWS_SECRET_ACCESS_KEY=abc123...")
    print("AWS_SESSION_TOKEN=IQoJb3...")
    print("AWS_REGION=us-east-1")
    print("-" * 60)
    sys.exit(1)

print("✅ .env file found!")
print()

# Step 2: Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv package installed")
except ImportError:
    print("❌ PROBLEM: python-dotenv package not installed!")
    print()
    print("✅ SOLUTION: Run this command:")
    print("   pip install python-dotenv")
    sys.exit(1)

print()
print("-" * 60)
print("📋 Environment Variables Check:")
print("-" * 60)

# Step 3: Check each credential
credentials = {
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_SESSION_TOKEN': os.getenv('AWS_SESSION_TOKEN'),
    'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1')
}

all_ok = True
for key, value in credentials.items():
    if value:
        if key == 'AWS_ACCESS_KEY_ID':
            print(f"✅ {key}: {value[:10]}...")
        elif key == 'AWS_SECRET_ACCESS_KEY':
            print(f"✅ {key}: {value[:10]}... (length: {len(value)})")
        elif key == 'AWS_SESSION_TOKEN':
            print(f"✅ {key}: {value[:20]}... (length: {len(value)})")
        else:
            print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: NOT SET")
        all_ok = False

print("-" * 60)
print()

if not all_ok:
    print("❌ PROBLEM: Some credentials are missing!")
    print()
    print("✅ SOLUTION:")
    print("   1. Open your .env file")
    print("   2. Make sure it has all required values")
    print("   3. Check for typos in variable names")
    print("   4. Make sure there are no spaces around the = sign")
    print()
    print("Example:")
    print("   AWS_ACCESS_KEY_ID=ASIA123456  ← Good")
    print("   AWS_ACCESS_KEY_ID = ASIA123456  ← Bad (spaces)")
    print("   AWS_ACCESS_KEY_ID=\"ASIA123456\"  ← Bad (quotes)")
    sys.exit(1)

# Step 4: Test AWS connection
print("🔌 Testing AWS connection...")
print()

try:
    import boto3
    
    # Try to create DynamoDB client
    dynamodb = boto3.client(
        'dynamodb',
        region_name=credentials['AWS_REGION'],
        aws_access_key_id=credentials['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['AWS_SECRET_ACCESS_KEY'],
        aws_session_token=credentials['AWS_SESSION_TOKEN']
    )
    
    # Try to list tables
    response = dynamodb.list_tables()
    tables = response.get('TableNames', [])
    
    print("✅ AWS connection successful!")
    print(f"✅ Found {len(tables)} DynamoDB table(s)")
    
    if tables:
        print()
        print("📊 Available tables:")
        for table in tables:
            print(f"   - {table}")
    else:
        print()
        print("⚠️  No DynamoDB tables found")
        print("   Run: python create_tables.py")
    
    print()
    print("=" * 60)
    print("🎉 ALL CHECKS PASSED!")
    print("=" * 60)
    print()
    print("✅ Your backend is ready to start!")
    print("   Run: python main.py")
    print()
    
except Exception as e:
    print("❌ AWS connection FAILED!")
    print()
    print(f"Error: {str(e)}")
    print()
    
    if "ExpiredToken" in str(e):
        print("🔴 PROBLEM: Your AWS credentials have expired!")
        print()
        print("✅ SOLUTION:")
        print("   1. Go to AWS Academy/Console")
        print("   2. Get fresh credentials")
        print("   3. Update your .env file with new values")
        print("   4. Run this script again")
    elif "InvalidClientTokenId" in str(e):
        print("🔴 PROBLEM: Invalid AWS credentials!")
        print()
        print("✅ SOLUTION:")
        print("   1. Check your .env file for typos")
        print("   2. Make sure you copied the complete values")
        print("   3. Session tokens are very long - copy all of it!")
    elif "UnrecognizedClientException" in str(e):
        print("🔴 PROBLEM: AWS doesn't recognize your credentials!")
        print()
        print("✅ SOLUTION:")
        print("   1. Get fresh credentials from AWS")
        print("   2. Update ALL THREE values in .env")
        print("   3. Make sure SESSION_TOKEN is included (for AWS Academy)")
    else:
        print("🔴 PROBLEM: Unknown AWS error")
        print()
        print("✅ SOLUTION:")
        print("   1. Check your internet connection")
        print("   2. Verify AWS region is correct")
        print("   3. Try getting fresh credentials")
    
    print()
    sys.exit(1)