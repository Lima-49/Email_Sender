"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""
import multiprocessing
from flask import Flask, request, render_template
from send_email import main_call

app = Flask(__name__)
queue = multiprocessing.Queue()

@app.route('/send_email', methods=['POST'])
def get_parameters():

    """
    It receives a JSON object, prints it, and then calls another function that sends an email
    :return: The result of the function send_email_to_customer
    """

    user_input = request.json

    id_meeting = user_input['id']
    list_of_recipients = user_input['recipients']
    creator_name = user_input['creator_name']
    date_list = user_input['meeting_day']
    #url = "https://easy-meeting.azurewebsites.net/external_url?meeting_day="+",".join(date_list)
    url = "http://127.0.0.1:5000/external_url?meeting_day="+",".join(date_list)

    for recipients_dict in list_of_recipients:

        user_dict = {
            "id_meeting":id_meeting,
            "recipients_dict":recipients_dict,
            "creator_name":creator_name,
        }

        #email_status = main_call(user_dict, url)
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

    return render_template('index.html', lista_datas=date_list)

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

    return render_template("answer_screen.html", data=date)

@app.route('/')
def root():
    """
    It returns the parameter_data variable.
    :return: the variable parameter_data.
    """
    parameter_data = {
        'meeting_day': [],
        'recipients': [{'name':"nome do participante", 'email':'email do participante'}],
        'creator_name':"Nome do criador da reuniao",
        'id':"id da reunião para salvar no banco"
    }
    return parameter_data

if __name__ == "__main__":
    app.run()
