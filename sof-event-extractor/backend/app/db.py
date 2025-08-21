from __future__ import annotations

import os
import pyodbc


def get_sql_connection():
	"""Create and return a pyodbc connection to Azure SQL.

	Relies on environment variables for secrets. Example variables:
	- SQL_SERVER: sof-sql-server.database.windows.net,1433
	- SQL_DATABASE: sof_dob
	- SQL_USER: adminuser
	- SQL_PASSWORD: admin@123
	"""
	server = os.getenv("SQL_SERVER", "")
	database = os.getenv("SQL_DATABASE", "")
	user = os.getenv("SQL_USER", "")
	password = os.getenv("SQL_PASSWORD", "")
	driver = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")

	conn_str = (
		f"DRIVER={{{driver}}};"
		f"SERVER={server};"
		f"DATABASE={database};"
		f"UID={user};"
		f"PWD={password};"
		"Encrypt=yes;"
		"TrustServerCertificate=no;"
		"Connection Timeout=30;"
	)
	return pyodbc.connect(conn_str)


