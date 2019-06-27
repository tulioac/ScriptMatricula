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


