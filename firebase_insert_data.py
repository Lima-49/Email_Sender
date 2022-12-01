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

    cred = credentials.Certificate("easyMeeting_prod.json")
    default_app = firebase_admin.initialize_app(cred)
    database = firestore.client()

    return database, default_app

def find_list_fb(collection, collection_name):
    """
    It takes a collection and a collection name
    and returns the document in the collection that has the
    same name as the collection name

    :param collection: the collection you want to search
    :param collection_name: The name of the collection you want to search
    :return: A list of dictionaries.
    """

    collection_list = collection.get()
    documnt_list = [doc.to_dict() for doc in collection_list]
    main_document = [doc for doc in documnt_list if doc['id']==collection_name]

    if len(main_document) > 0:
        return main_document[0]
    else:
        return None

def insert_fb(insert_dict, collection):
    """
    It takes a dictionary as an argument and inserts it into a Firestore collection
    :param database: The database object that you created in the previous step
    :param insert_dict: This is the dictionary that you want to insert into the database
    """

    res = collection.document(insert_dict['id']).set(insert_dict)
    print(res)

def most_frequent(date_list):
    """
    It takes a list of dates, converts it to a set
    and then returns the most frequent date in the set

    :param date_list: a list of dates in the format of 'YYYY-MM-DD'
    :return: The most frequent date in the list.
    """
    return max(set(date_list), key=date_list.count)

def find_best_date(collection_name, database):
    """
    It takes a collection name and a database as input, and returns the most frequent date in the
    collection

    :param collection_name: the name of the collection
    :param database: the database object
    :return: A list of the most frequent dates.
    """

    collection = database.collection('meetings')

    collection_return = find_list_fb(collection, collection_name)

    qtd_participantes = collection_return['qtdParticipantes']
    email_answer = collection_return['email']

    chosse_date = "--/--"
    if len(email_answer) == int(qtd_participantes):
        date_list = [doc['date'] for doc in email_answer]
        chosse_date = most_frequent(date_list)

    return chosse_date

def run_insert(user_input):
    """
    It takes a user input, checks if it exists in the database
    if it doesn't, it inserts it into the
    database.

    :param user_input: a dictionary
    """

    database, default_app = create_fb_database()
    collection = database.collection('meetings')
    collection_name = user_input['id']

    collection_return = find_list_fb(collection, collection_name)

    if collection_return is None:
        insert_fb(user_input,collection)
    else:
        data_usuario = user_input['email']
        data_fb = collection_return['email']
        user_date_choosed = user_input["user_date_choosed"]
        
        replace_index = data_fb.index(data_usuario)
        data_fb[replace_index] = {"email":data_usuario, "date":user_date_choosed}

        collection_return['email'] = data_fb
        print(collection_return)

        insert_fb(collection_return, collection)

    collection_return = find_list_fb(collection, collection_name)
    choosed_date = find_best_date(collection_name, database)

    collection_return['chooseDate'] = choosed_date
    insert_fb(user_input, collection)

    delete_app(default_app)
    