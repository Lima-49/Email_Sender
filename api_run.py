"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""
import multiprocessing
from flask import Flask, request, render_template
from send_email import main_call
from firebase_insert_data import run_insert

app = Flask(__name__)
queue = multiprocessing.Queue()

@app.route('/send_email', methods=['POST'])
def get_parameters():

    """
    It receives a JSON object, prints it, and then calls another function that sends an email
    :return: The result of the function send_email_to_customer
    """

    user_input = request.json
    creator = user_input['creator']
    date = user_input['date']
    email_list = user_input['email_list']
    id_meeting = user_input['id']
    meeting_link = user_input['link']
    status = user_input['status']
    title = user_input['title']

    #url = "https://easy-meeting.azurewebsites.net/external_url?meeting_day="+",".join(date_list)+"&id_meeting="+id_meeting
    url = "http://127.0.0.1:5000/external_url?meeting_day="+",".join(date)+"&id_meeting="+id_meeting

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

        job = multiprocessing.Process(target=main_call, args=(user_dict, url, queue))
        job.start()

    return {"Status": "Sucesso"}

@app.route("/external_url")
def get_best_date():
    """
    It receives a list of dates from the frontend, and returns the same list to the frontend
    :return: A list of dates
    """

    args = request.args
    date_list = args.get("meeting_day")
    date_list = date_list.split(',')
    id_meeting = args.get("id_meeting")

    return render_template('index.html', lista_datas=date_list, id_meeting=id_meeting)

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
    user_dict = consume_queue(id_meeting)

    insert_dict = user_dict
    insert_dict["id"] = id_meeting
    insert_dict["email"] = {"email_user":user_dict["email"], "date":date}
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

def consume_queue(id_meeting):
    """
    It's a function that consumes a queue and returns an item if the id_meeting is in the item

    :param id_meeting: the id of the meeting
    :return: The first item in the queue that matches the id_meeting.
    """

    while True:
        item = queue.get()

        if item is None:
            break
        elif id_meeting in item['id']:
            return item

if __name__ == "__main__":
    app.run()
