
"""
Codigo utilizado para automatizar o envio de emails
"""

import configparser
import smtplib
import os
import email.message
from flask import render_template

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

def create_email_body(sender, recipients, creator_name, subject):
    """
    It creates an email body.
    :param remetente: The email address of the sender
    :param destinatarios: list of email addresses
    :param assunto: Subject of the email
    """
    email_body = f"Olá {recipients['name']}\nVocê foi convidado para uma reuniao com {creator_name}\n Para escolher a melhor data, clique no link: http://127.0.0.1:5000/template"

    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients['email']

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_body)

    return msg

def run(user_input):
    """
    It creates an email server, logs in with the user and password, creates an email message
    and sends it
    """
    try:
        user = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
        psw = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

        id_meeting = user_input['id']
        list_of_recipients = user_input['recipients'][0]
        list_of_days = user_input['meeting_day']
        creator_name = user_input['creator_name']

        email_server = create_email_server(user, psw)
        email_msg = create_email_body(user, list_of_recipients, creator_name, f'Melhor data para a reuniao {id_meeting}')

        sender = email_msg['From']
        recipients = [email_msg['To']]

        email_server.sendmail(sender, recipients, email_msg.as_string().encode('utf-8'))
        dictionary = {"Status":"Sucesso ao enviar o email"}

    except Exception as email_error:
        print(email_error)
        dictionary = {"Status":"Erro ao enviar o email"}

    return dictionary
