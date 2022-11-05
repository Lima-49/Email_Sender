
"""
Codigo utilizado para automatizar o envio de emails
"""

import configparser
import os
from flask import Flask, render_template
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

def run(list_of_recipients, list_of_days):
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

        msg = Message(subject='Email de teste',sender=user, recipients=list_of_recipients)
        msg.html = render_template('index.html', list=list_of_days)
        mail.send(msg)
        dictionary = {"Status":"Sucesso ao enviar o email"}

    except Exception as email_error:
        print(email_error)
        dictionary = {"Status":"Erro ao enviar o email"}

    return dictionary
