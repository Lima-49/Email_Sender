"""
Código que será utilizado para adicionar os dados do usuário no banco de dados
"""
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, delete_app

MAIN_PATH = Path(__file__).parent
JSON_PATH =  MAIN_PATH / Path('./FireBase_Project_Key')

def relative_to_assets(path: str) -> Path:
    """
    It takes a path relative to the assets folder and returns a path relative to the main folder
    :param path: str
    :type path: str
    :return: A path object
    """
    return JSON_PATH / Path(path)

def create_fb_database():
    """
    It creates a database connection to Firebase.
    :return: The database object.
    """
    json_path = relative_to_assets('easyMeeting_prod.json')

    cred = credentials.Certificate(json_path)
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

    #Accessing the collection defined by the user
    docs = collection.stream()

    #Loop throught the list of documents to get the right id to update the document
    for doc in docs:

        #Transform the doc object to dictionary
        doc_dict = doc.to_dict()

        #If the id sended by the user is equal to the id at the dictionary
        if collection_name == doc_dict['id']:
            return doc_dict, doc.id

def insert_fb(insert_dict, collection, insert_id):
    """
    It takes a dictionary as an argument and inserts it into a Firestore collection
    :param database: The database object that you created in the previous step
    :param insert_dict: This is the dictionary that you want to insert into the database
    """

    res = collection.document(insert_id).set(insert_dict)
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

    collection_return = find_list_fb(collection, str(collection_name))[0]

    qtd_participantes = collection_return['qtdParticipantes']
    email_answer = collection_return['email_date']
    date_answer = [date_dr for date_dr in email_answer if date_dr['date'] != '']

    chosse_date = "--/--"
    status = 'Pendente'

    if len(date_answer) == int(qtd_participantes):
        date_list = [doc['date'] for doc in email_answer]
        chosse_date = most_frequent(date_list)
        status = 'Concluido'

    return chosse_date, status

def run_insert(user_input):
    """
    If the user has already voted, update the vote, otherwise insert a new vote
    :param user_input: a dictionary with the following keys:
    """

    try:
        database, default_app = create_fb_database()
        collection = database.collection('meetings')
        collection_name = user_input['id']

        collection_return, firebase_id = find_list_fb(collection, collection_name)

        #Pegando o email do usuario que respondeu
        data_usuario = user_input['email']

        #Lista de de dicionarios do banco contendo as datas e emails dos usuariops
        data_fb = collection_return['email_date']

        #data que o usuario respondeu
        user_date_choosed = user_input["user_date_choosed"]

        for emai_date_dict in data_fb:
            if emai_date_dict['email_user'] == data_usuario:
                emai_date_dict['date'] = user_date_choosed
                print(emai_date_dict)

        collection_return['email_date'] = data_fb
        print(collection_return)

        insert_fb(collection_return, collection, firebase_id)

        collection_return, firebase_id = find_list_fb(collection, collection_name)
        choosed_date, status = find_best_date(collection_name, database)

        collection_return['chooseDate'] = choosed_date
        collection_return['status'] = status
        insert_fb(collection_return, collection, firebase_id)

        delete_app(default_app)

    except Exception as insert_error:
        print(insert_error)
        delete_app(default_app)
    