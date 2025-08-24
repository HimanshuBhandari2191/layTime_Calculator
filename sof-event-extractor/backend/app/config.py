import os
from typing import Dict, Any


def get_config() -> Dict[str, Any]:
    return {
        # Azure Storage Configuration for sofstor123
        "AZURE_STORAGE_CONNECTION_STRING": os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING", 
            "DefaultEndpointsProtocol=https;AccountName=sofstor123;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net"
        ),
        "AZURE_STORAGE_CONTAINER": os.getenv("AZURE_STORAGE_CONTAINER", "files"),
        "AZURE_STORAGE_ACCOUNT_NAME": os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "sofstor123"),
        "AZURE_STORAGE_ACCOUNT_KEY": os.getenv("AZURE_STORAGE_ACCOUNT_KEY", ""),
        
        # Upload settings
        "UPLOAD_MAX_MB": int(os.getenv("UPLOAD_MAX_MB", "25")),
        "ENV": os.getenv("FLASK_ENV", "development"),
        
        # SQL Database settings (if needed)
        "SQL_SERVER": os.getenv("SQL_SERVER", "sof-sql-server.database.windows.net,1433"),
        "SQL_DATABASE": os.getenv("SQL_DATABASE", "sof_dob"),
        "SQL_USER": os.getenv("SQL_USER", "adminuser"),
        "SQL_PASSWORD": os.getenv("SQL_PASSWORD", "admin@123"),
    }


