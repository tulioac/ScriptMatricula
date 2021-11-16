from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import json
import time

URL_LOGIN = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/"
URL_HORARIO = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoHorarioConfirmar&ano=2019&periodo=1"
URL_MATRICULA = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline/Controlador?command=AlunoMatriculaGetForm"
TEMPO_DE_ESPERA = 5


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def ler_do_json():
    with open("dados.json", encoding="utf-8") as json_file:
        dados = json.load(json_file)
        for d in dados:
            matricula = d["matricula"]
            senha = d["senha"]
            horarioDeAbertura = d["horarioDeAbertura"]
            disciplinas = d["disciplinas"]
    horarioDeAbertura = time.strptime(horarioDeAbertura, "%H:%M:%S")
    return matricula, senha, horarioDeAbertura, disciplinas


class ScriptMatricula:
    def __init__(self, matricula, senha, horario_de_abertura, disciplinas_desejadas):
        self.matricula = matricula
        self.senha = senha
        self.horario_de_abertura = horario_de_abertura
        self.disciplinas_desejadas = disciplinas_desejadas
        self.browser = webdriver.Chrome()
        self.codigos_e_posicoes = {}

    def faz_login(self):
        user = self.browser.find_element_by_name("login")
        password = self.browser.find_element_by_name("senha")
        user.clear()
        user.send_keys(self.matricula)
        password.clear()
        password.send_keys(self.senha)
        self.browser.find_element_by_xpath(".//*[contains(text(), 'OK')]").click()

    def faz_logout(self):
        XPathBotaoDeSair = '//*[@id="menu"]/ul/li[6]/a'
        botaoDeSair = self.browser.find_element_by_xpath(XPathBotaoDeSair)
        botaoDeSair.click()

    def aguarda_horario(self):
        while horarioDeAbertura > self.pega_horario():
            clear_console()
            print("⏳  Esperando horário!")
            print("⏲️  Pausa de {} segundos...".format(TEMPO_DE_ESPERA))
            time.sleep(TEMPO_DE_ESPERA)

    def pega_horario(
        self,
    ):
        self.browser.get(URL_HORARIO)

        xPathData = '//*[@id="conteudo"]/div[4]/div[2]'
        infoHora = str(
            self.browser.find_element_by_xpath(xPathData).get_attribute("innerHTML")
        )[20:]
        horarioAtual = time.strptime(infoHora, "%H:%M:%S")
        return horarioAtual

    def verifica_abertura(self):
        while True:
            self.browser.get(URL_MATRICULA)
            if (
                self.browser.find_element_by_xpath(
                    '//*[@id="conteudo"]/div[1]'
                ).get_attribute("class")
                == "alert alert-danger"
            ):
                clear_console()
                print("⚠️  Ainda não abriu!")

            else:
                print("✨  Abriu!")
                break

            self.faz_logout()
            print("⏲️  Pausa de {:.2f} segundos...".format(TEMPO_DE_ESPERA // 3))
            time.sleep(TEMPO_DE_ESPERA // 3)
            self.faz_login()

    def localizador_de_disciplinas(self):
        self.browser.refresh()

        print("⏳  Lendo as disciplinas da página")
        for contador in range(1, 400):
            try:
                xpath = '//*[@id="tabOferta"]/tbody/tr[{Contador}]/td[2]'.format(
                    Contador=contador
                )
                codigo_e_turma_da_disciplina = str(
                    self.browser.find_element_by_xpath(xpath).get_attribute("innerHTML")
                )
                codigo_e_turma_da_disciplina = (
                    str(  # Verificar se precisa desse cast para str
                        codigo_e_turma_da_disciplina[1:13]
                    )
                )
                self.codigos_e_posicoes[codigo_e_turma_da_disciplina] = str(contador)
            except:
                print("⌛  Foram lidas {} disciplinas".format(contador))
                break

    def seleciona_disciplinas_desejadas(self):
        matriculadas = 0

        while matriculadas == 0:
            self.localizador_de_disciplinas()

            for codigo in disciplinas_para_matricular.keys():
                try:
                    linha = self.codigos_e_posicoes[codigo]
                    xpath = '//*[@id="tabOferta"]/tbody/tr[{}]/td[6]/input'.format(
                        linha
                    )
                    self.browser.find_element_by_xpath(xpath).click()
                    matriculadas += 1
                    print(
                        "✅  Selecionado a disciplina {}".format(
                            disciplinas_para_matricular[codigo]
                        )
                    )
                except:
                    print(
                        "❌  Não foi possível se matricular na disciplina {}".format(
                            disciplinas_para_matricular[codigo]
                        )
                    )

    def clica_matricular(self):
        self.browser.find_element_by_xpath(
            '//*[@id="conteudo"]/form/div[3]/input[3]'
        ).click()

    def faz_matricula(self):
        # Acessa a página de login
        self.browser.get(URL_LOGIN)

        # Faz login
        self.faz_login()

        # Aguarda o horário da abertura
        self.aguarda_horario()

        # Acessa a página de registrar e aguarda abertura
        self.verifica_abertura()

        # Lê e seleciona as disciplinas desejadas na página
        self.seleciona_disciplinas_desejadas()

        # Clica no botão de fazer matrícula
        self.clica_matricular()

        # Imprime "Matriculado!"
        print("🎆  Matriculado!")


# Carrega informações do json.
matricula, senha, horarioDeAbertura, disciplinas_para_matricular = ler_do_json()

scriptMatricula = ScriptMatricula(
    matricula, senha, horarioDeAbertura, disciplinas_para_matricular
)

scriptMatricula.faz_matricula()
