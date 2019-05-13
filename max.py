"""
Crawler for fetching data from UFCG's Online Student Dashboard
Author: Maxwell Albuquerque
"""

import re
import bs4
import random
import requests
from bs4 import BeautifulSoup

_URL = "https://pre.ufcg.edu.br:8443/ControleAcademicoOnline"
_URI_LOGIN = "/Controlador"
_URI_CLASSES = "/Controlador?command=AlunoTurmasListar"
_URI_OFFERED_COURSES = "/Controlador?command=AlunoDisciplinasOfertadas"
_URI_REGISTER_COURSES = "/Controlador?command=AlunoMatriculaGetForm"

class Course:
    __uri = None
    __name = None
    __absences = None
    __absences_limit = None
    __scores = []

    def __init__(self, course_uri, name, absences, absences_limit, scores):
        self.__uri = course_uri
        self.__name = name
        self.__absences = absences
        self.__absences_limit = absences_limit
        self.__scores = scores

    def get_name(self):
        return self.__name

    def get_scores(self):
        return self.__scores
    
    def get_absences(self):
        return self.__absences

    def get_absences_limit(self):
        return self.__absences_limit

    def get_summary(self):
        message = "📖 %s\n\n" % self.get_name()
        scores = self.get_scores()

        if len(scores["scores"]) > 0:
            for index in range(len(scores["scores"])):
                text = "Nota %s - *%s* - _Peso %0.2f_.\n"
                score = ""

                if scores["scores"][index] == -1:
                    score = "indisponível"
                else:
                    score = "%0.2f" % scores["scores"][index]

                message += text % (index + 1, score, scores["weights"][index])

            message += "\nMédia parcial: *%0.2f*" % (scores["average"])
        else:
            message += "Ainda não foi registrada nenhuma nota dessa disciplina.\n"

        message += "\nFaltas registradas: %s/%s"
        message = message % (self.get_absences(), self.get_absences_limit())

        return message

class AcademicPanel:
    __registration_id = None
    __password = None
    __session = None
    _user_name = None

    def __init__(self, registration_id, password):
        self.__registration_id = registration_id
        self.__password = password

        self.__update_session()

    def __update_session(self):
        """Authenticates in website and gets a new
        session object.
        """
        self.__session = requests.Session()

        data_frame = {
            "login": self.__registration_id,
            "senha": self.__password,
            "command": "AlunoLogin"
        }

        self.__session.post(_URL + _URI_LOGIN, data=data_frame)

    def is_logged_in(self):
        request = self.__session.get(_URL)
        soup = BeautifulSoup(request.text, "html.parser")

        user = soup.find("div", {"class": "col-sm-9 col-xs-7"})
        return user is not None

    def __get_course_absences(self, course_uri):
        url = _URL + "/" + course_uri
        url = url.replace("AlunoTurmaNotas", "AlunoTurmaFrequencia")
        
        request = self.__session.get(url)
        soup = BeautifulSoup(request.text, "html.parser")
        
        table = soup.find("table")
        table_thead = table.thead.tr

        row = list(table_thead)
        offset = -1

        absences_limit = 0

        for index in range(7, len(row)):
            item = row[index]
            offset += 1            
            if type(item) is not bs4.element.NavigableString:
                if re.match(r"Total", item.get_text()) is not None:
                    limit_str = re.findall(r"\d+", item["title"])[0]
                    absences_limit = int(limit_str)
                    break

        table_tr = table.tbody.tr
        row = list(table_tr)

        table_tbody = table.tbody.tr
        row = list(table_tbody)

        absences = int(row[7 + offset].get_text())

        return absences, absences_limit

    def __get_course_scores(self, course_uri):
        data = {
            "weights": [],
            "scores": [],
            "average": -1.0,
            "final_exam": -1.0,
            "final_average": -1.0
        }

        request = self.__session.get(_URL + "/" + course_uri)
        soup = BeautifulSoup(request.text, "html.parser")
        
        table = soup.find("table")
        table_thead = table.thead.tr
        
        for item in list(table_thead):
            if type(item) is not bs4.element.NavigableString:
                weights = re.findall(r"P = \d+", item.get_text())

                if len(weights) > 0:
                    weight_str = re.findall(r"\d+", weights[0])[0]
                    weight = float(weight_str)
                    data["weights"].append(weight)

        table_tr = table.tbody.tr
        row = list(table_tr)

        score_amount = len(data["weights"])

        for score_index in range(score_amount):
            score_string = row[7 + 2 * score_index].get_text()

            score = -1.0

            if score_string != "":
                score = float(row[7 + 2 * score_index].get_text())

            data["scores"].append(score)

        average_index = 7 + 2 * score_amount
        average_str = row[average_index].get_text().replace(",", ".")

        if average_str != "":
            data["average"] = float(average_str)

        final_exam_index = average_index + 2
        final_exam_str = row[final_exam_index].get_text().replace(",", ".")

        if final_exam_str != "":
            data["final_exam"] = float(final_exam_str)

        final_average_index = final_exam_index + 2
        final_average_str = row[final_average_index].get_text().replace(",", ".")

        if final_average_str != "":
            data["final_average"] = float(final_average_str)

        return data

    def get_courses(self):
        courses = []

        request = self.__session.get(_URL + _URI_CLASSES)
        soup = BeautifulSoup(request.text, "html.parser")

        table_body = soup.find("table").tbody

        for item in list(table_body):
            if type(item) is not bs4.element.NavigableString:
                children = list(item.children)
                
                name = children[5].get_text()

                # Removing breaklines in course's name
                name = name[3:]
                name = name[: len(name) - 1]

                # Making name pretty
                name = prettify_name(name)
                course_uri = children[5].a["href"]
                
                scores = self.__get_course_scores(course_uri)
                absences, absences_limit = self.__get_course_absences(course_uri)

                courses.append(Course(course_uri, name, absences, absences_limit, scores))

        return courses

    def get_offered_courses(self, allow_blocked=True, semester=None):
        request = self.__session.get(_URL + _URI_OFFERED_COURSES)
        soup = BeautifulSoup(request.text, "html.parser")

        table_body = soup.find("table").tbody
        
        courses = {}
        used_hashs = []

        for item in list(table_body):
            if type(item) is not bs4.element.NavigableString:
                children = list(item.children)

                class_name = children[5].get_text().lower()
                class_name = class_name.replace("\r", "")                
                is_blocked = False

                if len(re.findall(r"\(bloqueada(.*)\)", class_name)) > 0:
                    is_blocked = True
                    class_name = class_name.split("\n")[1]

                if (is_blocked and not allow_blocked):
                    continue

                aux = children[3].get_text().split("-")
                class_code = int(aux[0])     
                class_number = int(aux[1])
                class_semester = list(children[1].children)[0]

                if is_number(class_semester):
                    class_semester = int(class_semester)
                else:
                    class_semester = 0

                if semester is not None and class_semester != semester:
                    continue

                class_name = class_name.replace("\n", "")
                class_name = prettify_name(class_name)

                # Getting schedule
                aux = children[7].get_text().split("\n")
                class_schedule = []

                for row in aux:
                    template = {"day": 0, "from": "", "to": "", "place": ""}
                    if len(row) > 0 and row[0].isdigit():
                        template["day"] = int(row[0])
                        template["from"] = row[2:7]
                        template["to"] = row[8:13]
                        template["place"] = re.findall(r"\((.*)\)", row)[0]

                    if template["day"] == 0:
                        continue
                    else:
                        class_schedule.append(template)

                if len(class_schedule) == 0:
                    continue

                class_hash = generate_unused_hash(used_hashs)
                template = {
#                    "number": class_number,
                    "schedule": class_schedule,
                    "blocked": is_blocked,
                    "class_hash": class_hash
                }

                if not class_code in courses:
                    courses[class_code] = {
                        "code": class_code,
                        "name": class_name,
                        "semester": class_semester,
                        "classes": {}
                    }

                courses[class_code]["classes"][class_number] = template
                used_hashs.append(class_hash)

        return courses

def generate_unused_hash(used_hashs):
    hash = random.getrandbits(64)

    while hash in used_hashs:
        hash = random.getrandbits(64)

    return hash

def prettify_name(name):
    new_name = ""
    last = " "
    
    for letter in name.lower():
        if last == " " or (letter == "i" and last == "I") or last == "(":
            new_name += letter.upper()
            last = letter.upper()
        else:
            new_name += letter
            last = letter

    return new_name

def is_number(value):
    try:
        int(value)
        return True
    except:
        return False