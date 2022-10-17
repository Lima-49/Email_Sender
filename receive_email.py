
"""
Codigo utilizado para automatizar o recebimento de emails
"""

import configparser
import os
import imaplib

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

    email_server = imaplib.IMAP4_SSL('imap.gmail.com')
    email_server.login(usr, psw)

    return email_server

def main(user, psw):

    email_server = create_email_server(user, psw)
    email_server.select('inbox')


if __name__ == '__main__':

    USER = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
    PSW = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

    main(USER, PSW)
