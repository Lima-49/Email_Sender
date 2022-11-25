"""
Código utilizado para criar uma api responsavel em ativar o send_email
ASsim toda a vez q o usuario clicar no botão do app envia uma requisição
para ativar o robo send_email
"""
from flask import Flask, request, render_template
from send_email import main_call

app = Flask(__name__)

parameter_data = {
    'meeting_day': [],
    'recipients': [{'name':"nome do participante", 'email':'email do participante'}],
    'creator_name':"Nome do criador da reuniao",
    'id':"id da reunião para salvar no banco"
}

def send_email_to_customer(user_input):
    """
It takes in a user input, passes it to a function in another file, and returns the result of that
    function
    :param user_input: This is the user input that is passed to the function
    :return: the jsonified version of the email_status variable.
    """

    main_call(user_input)
    return {"Status":"Sucesso ao enviar o email"}

@app.route('/send_email', methods=['POST'])
def get_parameters():
    """
    It receives a JSON object, prints it, and then calls another function that sends an email
    :return: The result of the function send_email_to_customer
    """
    user_input = request.json
    print("Conteudo ", user_input)

    result = send_email_to_customer(user_input)

    return result

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

if __name__ == "__main__":
    app.run(debug=True)
