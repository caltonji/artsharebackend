import os
from flask import g
from azure.cosmosdb.table.tableservice import TableService
from twilio.rest import Client
from azure.storage.blob import BlobServiceClient

def get_table_service():
    if 'table_service' not in g:
        g.table_service = TableService(connection_string=os.environ['AZURE_STORAGE_CONNECTION_STRING'])

    return g.table_service

def get_blob_service_client():
    if 'blob_service_client' not in g:
        g.blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])

    return g.blob_service_client

def get_twilio_client():
    if 'twilio_client' not in g:
        g.twilio_client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

    return g.twilio_client