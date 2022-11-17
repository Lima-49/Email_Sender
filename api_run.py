"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""

from flask import Flask, jsonify, request, render_template
from send_email import run

app = Flask(__name__)

parameter_data = {
    'meeting_day': [],
    'recipients': [{'name':"nome do participante", 'email':'email do participante'}],
    'creator_name':"Nome do criador da reuniao",
    'id':"id da reunião para salvar no banco"
}

def send_email_to_customer(user_input):
    """
    It sends an email to a customer.
    :return: the result of the send_email.run() function.
    """
    email_status = run(user_input)
    return jsonify(email_status)

@app.route('/send_email', methods=['POST'])
def get_parameters():
    """
    It takes a list of recipients and a list of meeting days
    and sends an email to each recipient with
    the meeting day
    :return: The result of the function send_email_to_customer
    """
    user_input = request.json
    print("Conteudo ", user_input)

    result = send_email_to_customer(user_input)

    return result

@app.route('/template', methods=['GET'])
def show_template():

    """
  It takes a JSON object, prints it, and then renders a template with the JSON object as a variable
    :return: The list of meeting days.
    """

    return render_template('index.html')

@app.route('/')
def root():
    """
    It returns the parameter_data variable.
    :return: the variable parameter_data.
    """
    return parameter_data

app.run()
