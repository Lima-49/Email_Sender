"""
Código que será utilizado para adicionar os dados do usuário no banco de dados
"""

import firebase_admin
from firebase_admin import credentials, firestore, delete_app

def create_fb_database():
    """
    It creates a database connection to Firebase.
    :return: The database object.
    """

    cred = credentials.Certificate(r"FireBase_Project_Key\easyMeeting_teste.json")
    default_app = firebase_admin.initialize_app(cred)
    database = firestore.client()

    return database, default_app

def find_list_fb(collection, collection_name):
    """
    It takes a collection and a collection name as input and returns a dictionary of the collection
    name.

    :param collection: the firestore collection
    :param collection_name: the name of the collection you want to search
    :return: A dictionary
    """

    res = collection.document(collection_name).get().to_dict()
    return res

def insert_fb(insert_dict, collection):
    """
    It takes a dictionary as an argument and inserts it into a Firestore collection
    :param database: The database object that you created in the previous step
    :param insert_dict: This is the dictionary that you want to insert into the database
    """

    res = collection.document(insert_dict['id_meeting']).set(insert_dict)
    print(res)

def run_insert(user_input):
    """
    It takes a user input, checks if it exists in the database
    if it doesn't, it inserts it into the
    database.

    :param user_input: a dictionary
    """

    database, default_app = create_fb_database()
    collection = database.collection('programmer_details')
    collection_name = user_input['id_meeting']

    collection_return = find_list_fb(collection, collection_name)

    if collection_return is None:
        insert_fb(user_input,collection)
    else:
        data_usuario = user_input['datas_escolhidas']
        data_fb = collection_return['datas_escolhidas']

        if data_usuario['data'] == data_fb['data']:
            email_participantes = data_fb['email_participante'] + ", " +  data_usuario['email_participante']
            collection_return['datas_escolhidas']['email_participante'] = email_participantes
        else:
            data_escolhida = [data_usuario, data_fb]
            collection_return['datas_escolhidas'] = data_escolhida
            print(collection_return)

        insert_fb(collection_return, collection)

    delete_app(default_app)
    