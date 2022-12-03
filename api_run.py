"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""
from pathlib import Path
import configparser
import multiprocessing
from flask import Flask, request, render_template
from send_email import main_call
from firebase_insert_data import run_insert

app = Flask(__name__)
queue = multiprocessing.Queue()

MAIN_PATH = Path(__file__).parent

@app.route('/send_email', methods=['POST'])
def get_parameters():
    """
    It gets the parameters from the request
    and then it starts a process for each email in the email
    list
    """

    user_input = request.json
    creator = user_input['creator']
    date = user_input['date']
    email_list = user_input['email']
    id_meeting = user_input['id']
    meeting_link = user_input['link']
    status = user_input['status']
    title = user_input['title']

    environment_url = get_config_data(iten_title='URL', iten='prod')

    for email in email_list:

        user_dict = {
            "creator_name":creator,
            "date": date,
            "email": email,
            "id":id_meeting,
            "link":meeting_link,
            "qtdParticipantes": len(email_list),
            "status":status,
            "title": title,
        }

        char_date = ",".join(date)
        url = environment_url+"?meeting_day="+char_date+"&id_meeting="+id_meeting+"&email="+email

        job = multiprocessing.Process(target=main_call, args=(user_dict, url, queue))
        job.start()

    return {"Status": "Sucesso"}

@app.route("/external_url")
def get_best_date():
    """
    It receives a list of dates and an id_meeting
    and returns the index.html template with the list of
    dates and the id_meeting.
    :return: A list of dates
    """

    args = request.args
    date_list = args.get("meeting_day")
    date_list = date_list.split(',')
    id_meeting = args.get("id_meeting")
    email_answer = args.get('email')

    return render_template('index.html',lista_datas=date_list,id_meeting=id_meeting,email=email_answer)

@app.route("/date_answer", methods=['GET', 'POST'])
def get_date_answer():
    """
    It takes the date from the form and returns it.
    :return: The date
    """
    date = request.form['datePicker']
    date_list = date.split("/")
    date_list.pop(len(date_list)-1)
    date = "/".join(date_list)

    args = request.args
    id_meeting = args.get("id_meeting")
    email_answer = args.get("email")
    user_dict = consume_queue(id_meeting,email_answer)

    insert_dict = user_dict
    insert_dict["id"] = id_meeting
    insert_dict["user_date_choosed"] = date
    run_insert(insert_dict)

    return render_template("answer_screen.html", data=date)

@app.route('/')
def root():
    """
    It returns the parameter_data variable.
    :return: the variable parameter_data.
    """
    parameter_data = {
        "creator":"Nome do criador da reuniao",
        "date": ["Lista das possveis datas para a reuniao"],
        "email_list": ["lista de email dos participantes"],
        "id":"id da reuniao para filtrar no banco",
        "link":"link para acessar a reuniao",
        "qtdParticipantes": "Quantidade de participantes para a reuniao",
        "status":"Status das respostas",
        "title": "Assunto da reunião que sera enviado no corpo do email",
    }
    return parameter_data

def relative_to_assets(path: str) -> Path:
    """
    It takes a path relative to the assets folder and returns a path relative to the main folder
    :param path: str
    :type path: str
    :return: A path object
    """
    return MAIN_PATH / Path(path)

def get_config_data(iten_title, iten, config_path=relative_to_assets('config.txt')):
    """
    It reads a config file and returns the value of a given item
    :param iten_title: The title of the section in the config file
    :param iten: the name of the parameter you want to get from the config file
    :param config_path: The path to the config file
    :return: A string
    """

    arq_config = configparser.RawConfigParser()
    arq_config.read(config_path)

    data = arq_config.get(iten_title, iten)

    return str(data)

def consume_queue(id_meeting,email_answer):
    """
    It's a function that consumes a queue and returns an item if the id_meeting is in the item

    :param id_meeting: the id of the meeting
    :return: The first item in the queue that matches the id_meeting.
    """

    while True:
        item = queue.get()

        if item is None:
            break
        elif id_meeting in item['id'] and email_answer in item['email']:
            return item

if __name__ == "__main__":
    app.run()
