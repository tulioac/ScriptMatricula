from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json


def ler_do_json():
    with open("dados.json", encoding="utf-8") as json_file:
        dados = json.load(json_file)
        for d in dados:
            matricula = d["matricula"]
            senha = d["senha"]
            disciplinas = d["disciplinas"]
    return matricula, senha, disciplinas

def localizador_de_disciplinas(codigo_e_posicoes):
    for contador in range(1, 400):
        try:
            xpath = '//*[@id="tabOferta"]/tbody/tr[{Contador}]/td[2]'.format(
                Contador=contador)
            codigo_e_turma_da_disciplina = str(
                browser.find_element_by_xpath(xpath).get_attribute("innerHTML"))
            codigo_e_turma_da_disciplina = str(
                codigo_e_turma_da_disciplina[1:13])
            codigo_e_posicoes[codigo_e_turma_da_disciplina] = str(
                contador)
        except:
            print("Foram lidas {} linhas".format(contador))
            break


browser = webdriver.Chrome()
browser.get(
    "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/")

matricula, senha, disciplinas_para_matricular = ler_do_json()

user = browser.find_element_by_name("login")
password = browser.find_element_by_name("senha")
user.clear()
user.send_keys(matricula)
password.clear()
password.send_keys(senha)
browser.find_element_by_xpath(
    ".//*[contains(text(), 'OK')]").click()
browser.get(
    "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoMatriculaGetForm")


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
