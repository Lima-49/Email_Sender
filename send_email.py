
"""
Codigo utilizado para automatizar o envio de emails
"""

import configparser
import smtplib
import os
import email.message

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

def create_email_body(sender, recipients, subject='Teste de email automatico'):
    """
    It creates an email body.
    :param remetente: The email address of the sender
    :param destinatarios: list of email addresses
    :param assunto: Subject of the email
    """
    email_body = """
        <p> Envio de email automatico <p>
    """
    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_body)

    return msg

def main(user, psw):
    """
    It creates an email server, logs in with the user and password, creates an email message
    and sends it
    """
    email_server = create_email_server(user, psw)

    email_msg = create_email_body(sender=user, recipients=['vitorlima.soares@hotmail.com'])
    email_server.sendmail(email_msg['From'], [email_msg['To']], email_msg.as_string().encode('utf-8'))
    print("Email enviado")

if __name__ == '__main__':
    USER = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
    PSW = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

    main(USER, PSW)
