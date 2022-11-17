
"""
Codigo utilizado para automatizar o envio de emails
"""

import configparser
import os
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

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

def run(user_input):
    """
    It creates an email server, logs in with the user and password, creates an email message
    and sends it
    """
    try:
        user = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
        psw = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = user
        app.config['MAIL_PASSWORD'] = psw
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True

        mail = Mail(app)

        id_meeting = user_input['id']
        list_of_recipients = user_input['recipients'][0]
        list_of_days = user_input['meeting_day']
        creator_name = user_input['creator_name']

        email_subject = f'Melhor data para a reuniao {id_meeting}'
        msg = Message(subject=email_subject,sender=user, recipients=[list_of_recipients['email']], charset='utf-8')
       
        email_message = f"Olá {list_of_recipients['name']}\nVocê foi convidado para uma reuniao com {creator_name}\n Para escolher a melhor data, clique no link: http://127.0.0.1:5000/template"
        msg.body = email_message
        mail.send(msg)
        dictionary = {"Status":"Sucesso ao enviar o email"}

    except Exception as email_error:
        print(email_error)
        dictionary = {"Status":"Erro ao enviar o email"}

    return dictionary
