from google.cloud import firestore
from google.oauth2 import service_account
import json
import os
import streamlit as st
import traceback

def connect_to_firebase_db_and_authenticate(project_name: str = None, local_auth_file: str = "firestore-key.json"):
    """Connects to a firebase project using a local authentication file, or using a streamlit toml secrets file.

    Args:
        project_name (str, optional): Firebase project name. Defaults to None.
        local_auth_file (str, optional): Local authentication file. Defaults to "firestore-key.json".

    Returns:
        db: Firebase database object.
    """

    # Authenticate to Firestore with the JSON account key.
    if os.path.exists(local_auth_file):
        db = firestore.Client.from_service_account_json("firestore-key.json")

    # Authenticate with streamlit secrets
    elif "textkey" in st.secrets.keys():
        key_dict = json.loads(st.secrets["textkey"])
        with open("firestore-key.json", "w+") as f:
            json.dump(key_dict,f)
        #creds = service_account.Credentials.from_service_account_info(key_dict)
        #db = firestore.Client(credentials=creds, project=project_name)
        db = firestore.Client.from_service_account_json("firestore-key.json")

    # Other cases
    else:
        raise ValueError(
            "Impossible to access credentials for firebase database.")

    return db

def get_all_backtests(db) -> dict:
    """Returns all the backtests available in the database.

    Args:
        db: Firebase database instance.

    Returns:
        dict: Nested dictionary of all backtest instances.
    """

    # Let's make a reference to ALL of the posts
    posts_ref = db.collection("Backtest")

    # For a reference to a collection, we use .stream() instead of .get()
    all_backtests = {}
    for doc in posts_ref.stream():
        all_backtests[doc.id] = doc.to_dict()

    return all_backtests

def get_all_experiments(db) -> dict:

    # Let's make a reference to ALL of the posts
    posts_ref = db.collection("Experiment")

    # For a reference to a collection, we use .stream() instead of .get()
    all_experiments = {}
    for doc in posts_ref.stream():
        all_experiments[doc.id] = doc.to_dict()

    return all_experiments


def get_all_experiments_name(db) -> dict:

    # Let's make a reference to ALL of the posts
    posts_ref = db.collection("Experiment")

    # For a reference to a collection, we use .stream() instead of .get()
    experiments_names = []
    for doc in posts_ref.stream():
        experiments_names.append(doc.id)

    return experiments_names

def get_specific_experiment(db, experiment_name: str) -> dict:
    doc_ref = db.collection("Experiment").document(experiment_name)
    doc = doc_ref.get()  # Get data for document

    return doc.to_dict()

def get_specific_backtest(db, backtest_name: str) -> dict:
    """Fetches all information for a specific backtest.

    Args:
        db: Firebase database instance.
        backtest_name (str): Backtest name.

    Returns:
        backtest: Backtest information, as a dictionary. 
    """
    doc_ref = db.collection("Backtest").document(backtest_name)
    doc = doc_ref.get()  # Get data for document

    return doc.to_dict()

def create_backtest(db, backtest_name: str, data: dict) -> dict:
    doc_ref = db.collection("Backtest").document(backtest_name)
    doc = doc_ref.set(data)  # Get data for document

def delete_backtest(db, backtest_name: str) -> bool:

    doc_ref = db.collection("Backtest").document(backtest_name)
    doc_ref.set({})
    doc_ref.delete()


if __name__ == '__main__':

    project_name = 'autotrader'
    db = connect_to_firebase_db_and_authenticate(project_name=project_name)

    #all_backtests = get_all_backtests(db)
    #create_backtest(db, 'test_name', {'val1':1, 'val2':2})
    #delete_backtest(db, "test_name")
