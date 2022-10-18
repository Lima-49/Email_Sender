
"""
Codigo utilizado para automatizar o recebimento de emails
"""

import configparser
import os
import imaplib
import email

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

def get_email_id_list(receive_server):
    """
    It takes a server object as an argument and returns a list of email id's
    :param receive_server: The server object that you created in the previous step
    :return: A list of email id's
    """

    #Extract all email data insite the select folder, returning a list of ids
    data = receive_server.search(None, 'ALL')[1]

    #Extract the id's from the above list
    mail_ids = [block.split() for block in data].pop(0)

    #The fetch_data return a list with tuple with header and content
    fetch_data = [receive_server.fetch(idx,'(RFC822)')[1] for idx in mail_ids]

    return fetch_data

def extract_multipart_text(message):
    """
    If the message is multipart, then extract the text from each part and concatenate them together
    :param message: The message object that you want to extract the text from
    :return: The content of the email.
    """
    mail_content = ''
    for part in message.get_payload():
        if part.get_content_type == 'text/plain':
            mail_content += part.get_payload()
    return mail_content

def main(user, psw):

    email_server = create_email_server(user, psw)
    email_server.select('EasyMeetingAnswer')

    #The fetch_data return a list with tuple with header and content
    fetch_data = get_email_id_list(email_server)

    #Loop throught the list of tuples that contains the email content
    for response_part in fetch_data:
        if isinstance(response_part, tuple):

            #Extract the content message
            message = email.message_from_bytes(response_part[1])

            #Get sender and email subject
            email_sender = message['from']
            email_subject = message['subject']

            #In order to extract the mail message it needs to seprate the text
            #from annexes if necessary
            if message.is_multipart():
                mail_content = extract_multipart_text(message)
            else:
                mail_content = message.get_payload()

            print(f'From: {email_sender}')
            print(f'Subject: {email_subject}')
            print(f'Content: {mail_content}')

if __name__ == '__main__':

    USER = get_config_data(iten_title='EMAIL_LOGIN', iten='email')
    PSW = get_config_data(iten_title='EMAIL_LOGIN', iten='password')

    main(USER, PSW)
