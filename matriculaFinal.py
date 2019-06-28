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


def pegaHorario(urlHorario):
    browser.get(urlHorario)

    xPathData = '//*[@id="conteudo"]/div[4]/div[2]'
    infoHora = str(browser.find_element_by_xpath(xPathData).get_attribute("innerHTML"))[20:]
    horarioAtual = time.strptime(infoHora, '%H:%M:%S')
    return horarioAtual


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

TEMPO_DE_ESPERA = 10

browser = webdriver.Chrome()
urlLogin = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/" 
browser.get(urlLogin)

matricula, senha, horarioDeAbertura, disciplinas_para_matricular = ler_do_json()
fazLogin(matricula, senha)


urlHorario = 'https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHorarioConfirmar&ano=2019&periodo=1'

while (horarioDeAbertura > pegaHorario(urlHorario)):
    print ("Esperando horário!")
    print ("Pausa de {} segundos...".format(TEMPO_DE_ESPERA))
    time.sleep(TEMPO_DE_ESPERA)


urlMatricula = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoMatriculaGetForm"

while (True):
    browser.get(urlMatricula)
    if browser.find_element_by_xpath('//*[@id="conteudo"]/div[1]').get_attribute("class") == "alert alert-danger":
        print ("Ainda não abriu!")
    else:
        print("Abriu!")
        break
    print ("Pausa de {} segundos...".format(TEMPO_DE_ESPERA))
    time.sleep(TEMPO_DE_ESPERA)


codigo_e_posicoes = {}
localizador_de_disciplinas(codigo_e_posicoes)

for codigo in disciplinas_para_matricular.keys() :
    try:
        linha = codigo_e_posicoes[codigo]
        xpath = '//*[@id="tabOferta"]/tbody/tr[{}]/td[6]/input'.format(linha)
        browser.find_element_by_xpath(xpath).click()
        print("Selecionado a disciplina {}".format(disciplinas_para_matricular[codigo]))
    except:
        print("Não foi possível se matricular na disciplina {}".format(disciplinas_para_matricular[codigo]))

browser.find_element_by_xpath(
    '//*[@id="conteudo"]/form/div[3]/input[3]').click()

print("Matriculado!")