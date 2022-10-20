"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""

from flask import Flask, jsonify, request
from send_email import run

app = Flask(__name__)

parameter_data = {'recipients': [], 'meeting_day': []}

def send_email_to_customer(list_of_recipients, list_of_days):
    """
    It sends an email to a customer.
    :return: the result of the send_email.run() function.
    """
    email_status = run(list_of_recipients, list_of_days)
    return jsonify(email_status)

@app.route('/send_email', methods=['POST'])
def get_parameters():
    """
    It takes a list of recipients and a list of meeting days
    and sends an email to each recipient with
    the meeting day
    :return: The result of the function send_email_to_customer
    """
    content = request.json
    print("Conteudo ", content)

    recipients_list = content['recipients']
    meeting_day_list = content['meeting_day']

    result = send_email_to_customer(recipients_list, meeting_day_list)

    return result

@app.route('/')
def root():
    """
    It returns the parameter_data variable.
    :return: the variable parameter_data.
    """
    return parameter_data

app.run()
