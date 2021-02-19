from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import time


def ler_do_json():
    with open("dados.json", encoding="utf-8") as json_file:
        dados = json.load(json_file)
        for d in dados:
            matricula = d["matricula"]
            senha = d["senha"]
            horarioDeAbertura = d["horarioDeAbertura"]
            disciplinas = d["disciplinas"]
    horarioDeAbertura = time.strptime(horarioDeAbertura, '%H:%M:%S')
    return matricula, senha, horarioDeAbertura, disciplinas


def fazLogin(matricula, senha):
    user = browser.find_element_by_name("login")
    password = browser.find_element_by_name("senha")
    user.clear()
    user.send_keys(matricula)
    password.clear()
    password.send_keys(senha)
    browser.find_element_by_xpath(
        ".//*[contains(text(), 'OK')]").click()


def fazLogout():
    XPathBotaoDeSair = '//*[@id="menu"]/ul/li[6]/a'
    botaoDeSair = browser.find_element_by_xpath(XPathBotaoDeSair)
    botaoDeSair.click()


def pegaHorario(urlHorario):
    browser.get(urlHorario)

    xPathData = '//*[@id="conteudo"]/div[4]/div[2]'
    infoHora = str(browser.find_element_by_xpath(
        xPathData).get_attribute("innerHTML"))[20:]
    horarioAtual = time.strptime(infoHora, '%H:%M:%S')
    return horarioAtual


def localizador_de_disciplinas(codigo_e_posicoes):
    print("Lendo as disciplinas da página")
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


def selecionaDisciplinasDesejadas(disciplinas_para_matricular, codigo_e_posicoes, browser):
    matriculadas = 0

    while matriculadas == 0:
        localizador_de_disciplinas(codigo_e_posicoes)

        for codigo in disciplinas_para_matricular.keys():
            try:
                linha = codigo_e_posicoes[codigo]
                xpath = '//*[@id="tabOferta"]/tbody/tr[{}]/td[6]/input'.format(
                    linha)
                browser.find_element_by_xpath(xpath).click()
                matriculadas += 1
                print("Selecionado a disciplina {}".format(
                    disciplinas_para_matricular[codigo]))
            except:
                print("Não foi possível se matricular na disciplina {}".format(
                    disciplinas_para_matricular[codigo]))

        browser.refresh()


TEMPO_DE_ESPERA = 5

# Inicialização do navagador e acesso à página de login.
browser = webdriver.Chrome()
urlLogin = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/"
browser.get(urlLogin)

# Carrega informações do json.
matricula, senha, horarioDeAbertura, disciplinas_para_matricular = ler_do_json()
# Faz login com as informações
fazLogin(matricula, senha)


# Aguarda o horário previsto para abertura da plataforma.
urlHorario = 'https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHorarioConfirmar&ano=2019&periodo=1'

while (horarioDeAbertura > pegaHorario(urlHorario)):
    print("Esperando horário!")
    print("Pausa de {} segundos...".format(TEMPO_DE_ESPERA))
    time.sleep(TEMPO_DE_ESPERA)

# Tenta acessar a página da plataforma e aguarda caso esteja fechada.
urlMatricula = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoMatriculaGetForm"

while (True):
    browser.get(urlMatricula)
    if browser.find_element_by_xpath('//*[@id="conteudo"]/div[1]').get_attribute("class") == "alert alert-danger":
        print("Ainda não abriu!")

    else:
        print("Abriu!")
        break
    fazLogout()
    print("Pausa de {:.2f} segundos...".format(TEMPO_DE_ESPERA//3))
    time.sleep(TEMPO_DE_ESPERA//3)
    fazLogin(matricula, senha)


# Ler e seleciona as disciplinas para matrícula especificadas.
codigo_e_posicoes = {}
selecionaDisciplinasDesejadas(
    disciplinas_para_matricular, codigo_e_posicoes, browser)


# Clica no botão de fazer matrícula.
browser.find_element_by_xpath(
    '//*[@id="conteudo"]/form/div[3]/input[3]').click()

print("Matriculado!")
