import os
import json
from google.cloud import firestore
from google.oauth2 import service_account
from firebase_admin import credentials, firestore as admin_firestore, initialize_app

# Initialize Firestore
def init_firestore():
    google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    
    if google_credentials_json:
        credentials_dict = json.loads(google_credentials_json)
        cred = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # Initialize Firebase Admin (optional, for additional features)
        firebase_cred = credentials.Certificate(credentials_dict)
        initialize_app(firebase_cred)
        
        # Return Firestore client
        return firestore.Client(credentials=cred, project=project_id)
    else:
        # Use default credentials
        return firestore.Client(project=project_id)

db = init_firestore()