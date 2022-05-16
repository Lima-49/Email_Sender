from datetime import date,datetime,timedelta
from unidecode import unidecode
import PySimpleGUI as sg
import pandas as pd
import win32com.client 
import time
import os
import sys

## GLOBAL ##
#Variavel responsavel por auxiliar nos prints das mensagens dentro da tela, armazenando todos os prints
str_aux  = ''

## Paths ##
path = r'Paths aonde os emails serao salvos '
path_time_control = path + "\\" + "Time Sheet control.xlsx"
path_sheets = path + "\\" + "Sheets"
path_auxiliar = path + "\\" + "Auxiliar"
path_erro = 'lugar aonde o log sera salvo'

## Funcions ##
def error(e, path_erro):
    print("Apresentou erro, gravando o erro")
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    today = date.today()
    name = str(fname) + '_' + str(today) + '.txt'
    arquivo = open(path_erro + '\\' + name, 'w')
    arquivo.write(str(fname) + "\n")
    arquivo.write("\n" + str(e) + "\n")
    arquivo.write(str(exc_type) + "\n")
    arquivo.write(str(exc_tb.tb_lineno) + "\n")
    arquivo.close()
    
def date_list(list_of_messages, first_message):
    
    message = first_message
    
    lista = []
    
    for _ in list_of_messages:
        current_date = str(message.senton.date())
        data_datetime = datetime.strptime(current_date, "%Y-%m-%d")
        data = datetime.strftime(data_datetime, '%d/%m/%Y')
            
        if (data not in lista):
            lista.append(data)
            
        #Passando para a proxima mensagem
        message = messages.GetNext()

    
    return lista

def LimpandoGeral(path):
    print("Limpando arquivos gerais")
    if (os.path.exists(path)):
        print(path)
        dir = os.listdir(path)
        for file in dir:
            print(file)
            os.remove(path + '\\' + file)
            print(file + " removido com sucesso.")
    else:
        os.mkdir(path)
        print("Não tinha pasta, pasta criada.")
        
def formatDate(data):
    current_date = data
    data_datetime = datetime.strptime(current_date, "%d/%m/%Y")
    data_format = datetime.strftime(data_datetime, '%d-%m-%Y')
    
    return(data_format)

def layoutTela():
    
    
    #Criando o layout da janela
    layout = [

        [
            sg.Column([   
                #Titulo da pagina
                [sg.Text('Escolha a data do email que deseja extrair', key='-TXT-')],

                #Calenadario para inserir a data que deseja extrair os emails
                [sg.Input(key='calendario', size=(20,1)), sg.CalendarButton('Data',  target='calendario', format='%d/%m/%Y', close_when_date_chosen=True)],

                #Botão para enviar a data informada
                [sg.Button('Enviar')],
            ]),

            sg.VSeparator(),
            
            sg.Column([   
                #Mostra os prints do processo no elemento multiline 
                [sg.Multiline(size=(50,10), key='output', autoscroll=True, enable_events=True, auto_refresh=True, disabled=True, no_scrollbar=True)],
            ])
        ]
    ]

    return layout

def printOUT(output,mensagem):
    """
    Função print responsavel para mostrar para o usuario na tela interativa os processos do robo
    - str_aux = variavel global que ira armazenar todos os prints anteriores, para não subescrever o processo
    - mensagem = mensagem que sera mostrada na tela
    - output = objeto responsavel por mostrar a mensagem na tela
    """

    global str_aux
    str_aux = str_aux + "\n" + mensagem
    output.update(str_aux)

def criandoTime(path):
    #Diretorio do projeto
    dir = os.listdir(path)

    #Se o arquivo Time Sheet, ainda não existe, precisa ser criado
    if('Time Sheet control.xlsx' not in dir):
        
        print("Arquivo de horario inexistente, criando arquivo")
        
        #Criando o arquivo Time Sheet control
        df_cols = ['Employee','Project','Active Type','Time of each project','Date','Flag']
        df = pd.DataFrame(columns=df_cols)
        df.to_excel(path_time_control, index=False)

def findingTime(df, coluna, string_buscada):
    
    for linha in range(df.shape[0]):
        
        string = df.at[linha, coluna]
        
        if(str(string).__contains__(string_buscada)):
            print("O total de horas esta na linha: ", linha)
            break
        else:
            linha+=1
            
    return linha

def DonwloadTimeSheet(output, messages,data):
    
    printOUT(mensagem="\n===== Iniciando a Extração dos emails =====", output=output)

    print("\nExtraindo os emails enviados no dia ", data)
    printOUT(output=output, mensagem="\nExtraindo os emails enviados no dia " + data)

    # Inicializando a varivel mensgem com o primeiro item dentro da pasta
    message = messages.GetFirst()

    # Loop dentro da pasta do outlook, percorrendo os itens
    for item in messages:
        
        #Descobrindo o assunto do email  
        current_subject = str(message.Subject)
        
        #Descobrindo a data que o email foi enviado
        current_date = str(message.senton.date())
        
        #Verificando se o email atual contem o assunto Timesheet e a data de envio bate com a data informada pelo usuario
        if(((current_subject.__contains__('Timesheet')) or (current_subject.__contains__('TimeSheet'))) and ((current_subject.__contains__(data)) or (current_subject.__contains__(formatDate(data))))): 
            
            #Pega os arquivos que foram enviados junto do email
            attachments = message.Attachments
            
            #Variavel auxiliar para contar quantos arquivos estao anexados
            x = 0 
            
            #Cada emal pode ter mais de um arquivo anexado, por isso um loop em torno desses arquivos
            for attachment in attachments:

                #Pegando o nome do arquivo 
                attachment_name = str(attachment.FileName)
                #print("Arquivo anexado: ", attachment_name)
                
                #Baixando apenas o arquivo que possuir xlsx ou xls como extensão, e conter a data atual 
                if((attachment_name.__contains__('xlsx') or attachment_name.__contains__('xls')) and ((attachment_name.__contains__(data)) or (attachment_name.__contains__(formatDate(data))))):    
                    
                    #Salvando em uma pasta local
                    attachment.SaveASFile(path_sheets + '\\' + attachment_name)
                    attachment.SaveASFile(path_auxiliar + '\\' + attachment_name)
                    print("\nSalvando o arquivo: ", attachment_name)
                    printOUT(output=output, mensagem=f"\nSalvando o arquivo: {attachment_name}")
                    
        #Passando para a proxima mensagem
        message = messages.GetNext()

def Timesheet_robots(output):

    #Criando o arquivo se ele ainda nao existir
    criandoTime(path=path)

    df_template = pd.read_excel(path_time_control)
    row = df_template.shape[0] + 1

    clt = ['Alan Silva Furquim', 'Joao Marcos Antunes', 'Jair Rodrigo de Goes Brisola', 'Juliana Mei Min Hua', 'Karen Torres de Oliveira', 'Rafael Felipe de Moraes', 'Vitor Augusto de Lima Soares']
    est = ['Carlos Eduardo Martins Barbosa', 'Gianluca Bueno Machado Ribeiro', 'Joao Henrique de Freitas Queiroz', 'Nathan Roberto Goncalves dos Santos', 'Luiz Henrique Goes Rodrigues', 'Pablo Henrique Fama Rodrigues',
        'Larissa Bianchi', 'Andre Luiz Oliveira Moreira', 'Wellington Henrique Franca de Santana']

    #Pegando o dia atual como Segunda, Terca...
    feira = datetime.today().strftime("%A")

    #diretorio que possui as planilhas de controle
    dir_files = os.listdir(path_auxiliar)

    printOUT(output=output, mensagem="\nConcatenando os arquivos dda timesheet ")
    #Loop dentro do diretorio que possui as planilhas de controle
    for arq in dir_files:
        
        print("\nArquivo: ", arq)
        
        #Abrindo o arquivo atual
        df_emp = pd.read_excel(path_auxiliar + "\\" + str(arq))
        
        #Cada item esta em uma linha especifica do arquivo
        linha_nome = 6
        linha = 10
        proxima = 11
        
        #Percorrendo as linhas da timesheet do empregado    
        while linha < proxima:
            
            #Valoes que serão inseridos no base de dados final            
            employee = unidecode(df_emp.at[int(linha_nome), 'Unnamed: 7'])
            project = df_emp.at[int(linha), 'Unnamed: 4']
            active = df_emp.at[int(linha), 'Unnamed: 5']
            work_description = df_emp.at[int(linha), 'Unnamed: 6']
            time = df_emp.at[int(linha), 'Unnamed: 9']
            date = df_emp.at[int(linha), 'Unnamed: 1']
            project_p = df_emp.at[int(linha+1), 'Unnamed: 4']
            
            #Se a informacão buscada for vazia
            if str(project_p) == "nan":
                
                #Procura na proxima linha
                df_template.at[int(row), 'Employee'] = str(unidecode(employee))
                df_template.at[int(row), 'Project'] = str(project)
                df_template.at[int(row), 'Active Type'] = str(active)
                df_template.at[int(row), 'Time of each project'] = str(time)
                df_template.at[int(row), 'Date'] = str(date)
                df_template.at[int(row), 'Working Description'] = str(work_description)

                #Incrementa a linha atual 
                linha = linha + 1
                row = row +1  
            
            else:
                
                df_template.at[int(row), 'Employee'] = str(unidecode(employee))
                df_template.at[int(row), 'Project'] = str(project)
                df_template.at[int(row), 'Active Type'] = str(active)
                df_template.at[int(row), 'Time of each project'] = str(time)
                df_template.at[int(row), 'Date'] = str(date)
                df_template.at[int(row), 'Working Description'] = str(work_description)
                
                row = row + 1
                linha = linha + 1
                proxima = proxima + 1
            
            #No final de percorrer a timesheet do empregado, procura-se as horas totais trabalhadas
            linha_hora = findingTime(df=df_emp, coluna='Unnamed: 8', string_buscada='Total Hours:')

            #As horas totais trabalhadas, estão na mesma linha que a string procurada, então buscamos o valor na coluna ao lado
            horas = df_emp.at[linha_hora, 'Unnamed: 9']
            horas = horas.strftime('%H:%M')
            print("Quantidade de horas trabalhadas: ",horas)

            #Separando a string de tempo, e transformando em int, para validacao de horas trabalhadas
            horas_sep = horas.split(":")
            hora = int(horas_sep[0])
            minuto = int(horas_sep[1])

            #Se o empregado for um clt
            if(unidecode(employee) in clt):
                
                #As horas trabalhadas devem ser entre 8 horas, com 10 minutos de margem
                if( (hora == 7 and minuto >=50) or (hora == 8 and minuto <= 10) ):
                    
                    print(f"Horas trabalhadas estão corretas")
                    
                    df_template.at[int(row)-1, 'Flag'] = str('RIGHT')
                else:
                    
                    print(f"Horas trabalhadas estão incorretas")
                    
                    df_template.at[int(row)-1, 'Flag'] = str('WRONG')

            #Se o empregado for um est
            if(unidecode(employee) in est):
                
                #As horas trabalhadas devem ser entre 6 horas, com 10 minutos de margem
                if( (hora == 5 and minuto >= 50) or (hora == 6 and minuto <= 10) ):
                    
                    print(f"Horas trabalhadas estão corretas")
                    
                    df_template.at[int(row)-1, 'Flag'] = str('RIGHT')
                else: 
                    
                    print(f"Horas trabalhadas estão incorretas")
                    
                    df_template.at[int(row)-1, 'Flag'] = str('WRONG')

    #Salvando o arquivo com todas as sheets juntas   
    df_template.to_excel(path_time_control,index=False)

def convert(seconds): 
    """
    Funcao responsavel para calcular o tempo de excecucao do processo
    - seconds: segundos enviados que sera retornado como h:min:seg
    """
    return time.strftime("%H:%M:%S", time.gmtime(seconds))  

def sendEmail(mensagem, email_to):
    """
    Função responsavel por enviar o email de erro 
    - mensagem: mensagem de erro que sera enviada 
    """

    #Criando um objeto que conecta com o email
    outlook = win32com.client.Dispatch('outlook.application')
    
    #Cria um novo email para ser enviado
    mail = outlook.CreateItem(0)

    #Para quem sera enviado o email
    mail.To = email_to
    
    #Assundo do email
    mail.Subject = 'Erro TimeSheet'
    
    #Conteudo do emaul enviado
    mail.Body = 'Erro apresentado:\n\n' + mensagem
    
    #Envia o email 
    mail.Send()

## Main ## 
try:
    #Tempo incial do processo
    start = time.time()

    #Criando o layout da tela
    sg.theme("Reddit")
    layout = layoutTela()

    #Criando a janela
    window = sg.Window(title='Nome da tela', layout=layout)

    # Criando um objeto, para acessar o Outlook.
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    # Criando um objeto que acessa uma pasta dentro do outlook.
    # Nesse caso acessara a pasta, Caixa de entrada = 6, e a subpasta Relatorio Robos
    inbox = outlook.GetDefaultFolder(6).folders("Nome da pasta que ira acessar dentro da caixa de entrada (6)")

    # Selecionando os itens dentro da pata selecionada
    messages = inbox.Items

    # Inicializando a varivel mensgem com o primeiro item dentro da pasta
    message = messages.GetFirst()

    #Lista de datas disponiveis para a extração 
    list_date = date_list(list_of_messages=messages, first_message=message)
    print(list_date)

    #Criando uma variavel que ira armazenar os prints
    output = window.find_element('output')

    while True:

        #GErenciando os eventos e valores inforamdos pelo usuario
        eventos, valores = window.read()

        #Se o usuario clicar em Fechar, a janela fecha e quebra o processo
        if eventos == sg.WINDOW_CLOSED:
            break

        #Quando o usuario clicar em enviar ele pega o valor informado pelo usuario e verifica se esta dentro das datas do email
        if eventos == 'Enviar':
            
            #Data informada
            data = valores['calendario']  

            #Verifaicando se existem emails enviados na data que o usuario selecionou
            if(data not in list_date):
                print("\nAinda não existe timesheet enviada na data escolhida !")
                sg.popup(f"Ainda não existe timesheet enviada na data escolhida !\nEscolha uma dessas datas\n{list_date}")

            else:

                #Rodando o primeiro robo, que baixa os emails da timesheet
                DonwloadTimeSheet(output=output, messages=messages, data=data)

                #Rodando o segundo robo que consolida os dados extraidos em uma base de dados
                Timesheet_robots(output=output)

                #Tenpo final do processo
                end = time.time()
                final = end - start

                output.update(f"\n======== Arquivos Extraidos com sucesso ========\nProcesso finalizado com sucesso\nTempo de processamento: {convert(final)}")
            

    window.close()

except Exception as e:
    error(e, path_erro)
    sg.popup(f"Ocorreu um erro inesperado\nPor favor avise o suporte")
    window.close()
    sendEmail(mensagem=e, to=email_to)
            
