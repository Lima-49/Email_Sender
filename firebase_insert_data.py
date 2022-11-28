"""
Código que será utilizado para adicionar os dados do usuário no banco de dados
"""

import firebase_admin
from firebase_admin import credentials, firestore

def create_fb_database():
    """
    It creates a database connection to Firebase.
    :return: The database object.
    """

    cred = credentials.Certificate(r"FireBase_Project_Key\easyMeeting_teste.json")
    firebase_admin.initialize_app(cred)
    database = firestore.client()

    return database

def insert_fb(database, insert_dict):
    """
    It takes a dictionary as an argument and inserts it into a Firestore collection
    :param database: The database object that you created in the previous step
    :param insert_dict: This is the dictionary that you want to insert into the database
    """

    collection = database.collection('programmer_details')  # create collection
    res = collection.document(insert_dict['id_meeting']).set(insert_dict)
    print(res)
