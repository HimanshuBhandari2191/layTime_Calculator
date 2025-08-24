#!/usr/bin/env python3
"""
Test script for Azure Storage configuration
Run this to test your Azure Storage connection and get the connection string
"""

import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime


def test_azure_storage():
    """Test Azure Storage connection and upload a test file."""
    
    # Your Azure Storage details
    account_name = "sofstor123"
    account_key = input("Enter your Azure Storage Account Key: ").strip()
    container_name = "files"
    
    # Build connection string
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    
    try:
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Check if container exists, create if not
        if not container_client.exists():
            print(f"Creating container '{container_name}'...")
            container_client.create_container()
            print(f"Container '{container_name}' created successfully!")
        else:
            print(f"Container '{container_name}' already exists.")
        
        # Upload a test file
        test_content = f"Test file created at {datetime.now()}"
        blob_name = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(test_content, overwrite=True)
        
        print(f"✅ Test file uploaded successfully: {blob_name}")
        print(f"✅ Azure Storage connection working!")
        print(f"\n📋 Your connection string for environment variable:")
        print(f"AZURE_STORAGE_CONNECTION_STRING={connection_string}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your account key is correct")
        print("2. Check if your storage account is accessible")
        print("3. Verify the container name 'files' exists or can be created")
        return False


def get_connection_string():
    """Get the connection string format."""
    account_name = "sofstor123"
    print(f"\n📋 To get your connection string:")
    print("1. Go to Azure Portal → Storage Account 'sofstor123'")
    print("2. Access keys → Show connection string")
    print("3. Copy the connection string")
    print(f"4. Set environment variable: AZURE_STORAGE_CONNECTION_STRING=<your_connection_string>")


if __name__ == "__main__":
    print("🔧 Azure Storage Configuration Test")
    print("=" * 40)
    
    choice = input("Do you want to test with account key? (y/n): ").lower().strip()
    
    if choice == 'y':
        test_azure_storage()
    else:
        get_connection_string()

