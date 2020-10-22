from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import time


def ler_do_json():
    with open("dados.json", encoding="utf-8") as json_file:
        dados = json.load(json_file)
        for dado in dados:
            matricula = dado["matricula"]
            senha = dado["senha"]
            horario_de_abertura = dado["horario_de_abertura"]
            disciplinas = dado["disciplinas"]

            ano = dado["ano"]
            periodo = dado["periodo"]
    horario_de_abertura = time.strptime(horario_de_abertura, '%H:%M:%S')
    return matricula, senha, horario_de_abertura, disciplinas, ano, periodo


def faz_login(matricula, senha):
    user = browser.find_element_by_name("login")
    password = browser.find_element_by_name("senha")
    user.clear()
    user.send_keys(matricula)
    password.clear()
    password.send_keys(senha)
    browser.find_element_by_xpath(
        ".//*[contains(text(), 'OK')]").click()


def faz_logout():
    XPath_botao_de_sair = '//*[@id="menu"]/ul/li[6]/a'
    botao_de_sair = browser.find_element_by_xpath(XPath_botao_de_sair)
    botao_de_sair.click()


def pega_horario(url_horario):
    browser.get(url_horario)

    xPath_data = '//*[@id="conteudo"]/div[4]/div[2]'
    info_hora = str(browser.find_element_by_xpath(
        xPath_data).get_attribute("innerHTML"))[20:]
    horario_atual = time.strptime(info_hora, '%H:%M:%S')
    return horario_atual


def localizador_de_disciplinas(codigo_e_posicoes):
    for contador in range(1, 400):
        try:
            xpath = '//*[@id="tabOferta"]/tbody/tr[{Contador}]/td[2]'.format(
                Contador=contador)
            codigo_e_turma_da_disciplina = str(
                browser.find_element_by_xpath(xpath).get_attribute("innerHTML"))
            codigo_e_turma_da_disciplina = str(     # Verificar se precisa desse cast para str
                codigo_e_turma_da_disciplina[1:13])
            codigo_e_posicoes[codigo_e_turma_da_disciplina] = str(
                contador)
        except:
            print("Foram lidas {} linhas".format(contador))
            break


def seleciona_disciplinas_desejadas(disciplinas_para_matricular, codigo_e_posicoes):
    for codigo in disciplinas_para_matricular.keys():
        try:
            linha = codigo_e_posicoes[codigo]
            xpath = '//*[@id="tabOferta"]/tbody/tr[{}]/td[6]/input'.format(
                linha)
            browser.find_element_by_xpath(xpath).click()
            print("Selecionado a disciplina {}".format(
                disciplinas_para_matricular[codigo]))
        except:
            print("Não foi possível se matricular na disciplina {}".format(
                disciplinas_para_matricular[codigo]))


TEMPO_DE_ESPERA = 5

# Inicialização do navagador e acesso à página de login.
browser = webdriver.Chrome()
url_login = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/"
browser.get(url_login)

# Carrega informações do json.
matricula, senha, horario_de_abertura, disciplinas_para_matricular, ano, periodo = ler_do_json()
# Faz login com as informações
faz_login(matricula, senha)

# Aguarda o horário previsto para abertura da plataforma.
url_horario = 'https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHorarioConfirmar&ano=%d&periodo=%d' % (
    ano, periodo)

while (horario_de_abertura > pega_horario(url_horario)):
    print("Esperando horário!")
    print("Pausa de {} segundos...".format(TEMPO_DE_ESPERA))
    time.sleep(TEMPO_DE_ESPERA)

# Tenta acessar a página da plataforma e aguarda caso esteja fechada.
url_matricula = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoMatriculaGetForm"

while (True):
    browser.get(url_matricula)
    if browser.find_element_by_xpath('//*[@id="conteudo"]/div[1]').get_attribute("class") == "alert alert-danger":
        print("Ainda não abriu!")

    else:
        print("Abriu!")
        break
    faz_logout()
    print("Pausa de {:.2f} segundos...".format(TEMPO_DE_ESPERA//3))
    time.sleep(TEMPO_DE_ESPERA//3)
    faz_login(matricula, senha)

# Ler todas as disciplinas nas páginas e as armazena.
codigo_e_posicoes = {}
localizador_de_disciplinas(codigo_e_posicoes)

# Seleciona as disciplinas para matrícula especificadas.
seleciona_disciplinas_desejadas(disciplinas_para_matricular, codigo_e_posicoes)


# Clica no botão de fazer matrícula.
browser.find_element_by_xpath(
    '//*[@id="conteudo"]/form/div[3]/input[3]').click()

print("Matriculado!")
