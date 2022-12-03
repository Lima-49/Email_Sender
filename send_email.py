
"""
Codigo utilizado para automatizar o envio de emails
"""
from pathlib import Path
import configparser
import smtplib
import email.message

MAIN_PATH = Path(__file__).parent

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

def create_email_body(sender, recipient_email, creator_name, subject, site_url):
    """
    It creates an email body.
    :param remetente: The email address of the sender
    :param destinatarios: list of email addresses
    :param assunto: Subject of the email
    """
    email_body = f"""Ola como vai ?\n
    Voce foi convidado para uma reuniao com {creator_name}\n 
    Para escolher a melhor data, clique no link: {site_url}
    """

    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient_email

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

def main_call(user_input, url, queue):
    """
    It creates an email server, logs in with the user and password, creates an email message
    and sends it
    """
    try:
        user = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
        psw = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

        recipient_email = user_input['email']
        creator_name = user_input['creator_name']
        subject = user_input['title']
        email_server = create_email_server(user, psw)

        email_msg = create_email_body(user, recipient_email, creator_name, subject, url)
        run(email_server, email_msg)

        user_input["robot_status"] = "sucesso"

    except Exception as email_error:

        user_input["robot_status"] = "Erro ao enviar o email"
        user_input["robot_status_error_msg"] = email_error

    queue.put(user_input)
