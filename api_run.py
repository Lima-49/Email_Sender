"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""
import configparser
import smtplib
import os
import email.message
import json
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

parameter_data = {
    'meeting_day': [],
    'recipients': [{'name':"nome do participante", 'email':'email do participante'}],
    'creator_name':"Nome do criador da reuniao",
    'id':"id da reunião para salvar no banco"
}

@app.route('/send_email', methods=['POST'])
def get_parameters():

    """
    It receives a JSON object, prints it, and then calls another function that sends an email
    :return: The result of the function send_email_to_customer
    """

    user_input = request.json
    print("Conteudo ", user_input)

    try:
        user = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
        psw = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

        id_meeting = user_input['id']
        list_of_recipients = user_input['recipients']
        creator_name = user_input['creator_name']
        date_list = user_input['meeting_day']
        subject = f'Melhor data para a reuniao {id_meeting}'
        url = "https://easy-meeting.azurewebsites.net/external_url?meeting_day="+",".join(date_list)
        email_server = create_email_server(user, psw)

        for recipients_dict in list_of_recipients:
            email_msg = create_email_body(user, recipients_dict, creator_name, subject, url)
            run(email_server, email_msg)

        dictionary = {"Status":"Sucesso ao enviar o email"}

    except Exception as email_error:
        dictionary = {"Status":"Erro ao enviar o email", "Error Message": email_error}
        print(email_error)

    dictionary = jsonify(dictionary)
    return dictionary

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
    return parameter_data

def get_config_data(iten_title, iten, config_path=os.path.join(os.getcwd(), 'config.txt')):
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

def create_email_server(usr, psw):
    """
    It creates a server that can send emails
    :return: The server object
    """

    email_server = smtplib.SMTP('smtp.gmail.com: 587')
    email_server.ehlo()
    email_server.starttls()
    email_server.login(usr, psw)

    return email_server

def create_email_body(sender, recipients, creator_name, subject, site_url):
    """
    It creates an email body.
    :param remetente: The email address of the sender
    :param destinatarios: list of email addresses
    :param assunto: Subject of the email
    """
    email_body = f"""Olá {recipients['name']}\n
    Você foi convidado para uma reuniao com {creator_name}\n 
    Para escolher a melhor data, clique no link: {site_url}
    """

    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients['email']

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_body)

    return msg

def run(email_server, email_msg):
    """
It takes an email server and an email message as input, and sends the email message using the email
    server.
    :param email_server: The SMTP server object
    :param email_msg: The email message to be sent
    """

    sender = email_msg['From']
    recipients = [email_msg['To']]

    email_server.sendmail(sender, recipients, email_msg.as_string().encode('utf-8'))

if __name__ == "__main__":
    app.run()
