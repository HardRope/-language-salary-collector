import os

from dotenv import load_dotenv

import requests
from terminaltables import AsciiTable



def collect_vacancies_sj(languages):
    auth = {
        "X-Api-App-Id":
            os.getenv("X-Api-App-Id"),
    }
    url = "https://api.superjob.ru/2.0/vacancies/"

    languages_vacancies = {}

    for language in languages:
        page = 0
        page_numbers = 1

        languages_vacancies[language] = {
            "items": [],
            "vacancies_found": 0
        }

        while page < page_numbers:
            params = {
                "town": '4',
                "catalogue": 48,
                "keyword": "программист " + language,
                "count": 20,
                "page": page,
            }

            response = requests.get(url, headers=auth, params=params)
            response.raise_for_status()

            page_numbers = response.json()["total"] // 20 + 1
            page += 1

            languages_vacancies[language]["items"].extend(response.json()["objects"])
            languages_vacancies[language]["vacancies_found"] = response.json()["total"]

    return languages_vacancies


def get_salaries_sj(vacancies):
    salaries = []

    for vacancy in vacancies:
        currency = vacancy["currency"]
        salary_from = vacancy["payment_from"]
        salary_to = vacancy["payment_to"]

        if not salary_from and not salary_to:
            salaries.append(None)
            continue

        salaries.append({
            "currency": currency,
            "from": salary_from,
            "to": salary_to,
        })
    return salaries


def collect_vacancies_hh(languages):
    hh_url = "https://api.hh.ru/vacancies/"
    languages_vacancies = {}

    for language in languages:
        page = 0
        pages_number = 1

        languages_vacancies[language] = {
            "items": [],
            "vacancies_found": 0
        }

        while page < pages_number:
            params = {
                "text": "программист " + language,
                "period": 30,
                "area": 1,
                "page": page
            }

            response = requests.get(hh_url, params=params)
            response.raise_for_status()

            languages_vacancies[language]["items"].extend(response.json()["items"])
            languages_vacancies[language]["vacancies_found"] = response.json()["found"]

            pages_number = response.json()["pages"]
            page += 1

    return languages_vacancies


def get_salaries_hh(vacancies):
    salaries = []
    for vacancy in vacancies:
        vacancy_salary = vacancy["salary"]
        salaries.append(vacancy_salary)
    return salaries


def get_rub_average_salaries(salaries):
    average_salaries = []

    for salary in salaries:
        if not salary:
            average_salaries.append(None)
            continue

        if not salary["currency"] in ("RUR", "rub"):
            continue

        if salary["from"] and salary["to"]:
            average_salaries.append((salary["from"] + salary["to"]) / 2)

        elif not salary["from"]:
            average_salaries.append((salary["to"] * 0.8))

        elif not salary["to"]:
            average_salaries.append(salary["from"] * 1.2)

    return average_salaries


def get_average_salary(salaries):
    salaries_sum = 0
    counter = 0

    for salary in salaries:
        if salary:
            salaries_sum += salary
            counter += 1

    average = int(salaries_sum // counter)
    return average, counter


def hh_get_salary_by_language(languages):
    vacancies = collect_vacancies_hh(languages)

    salary_by_languages = {}

    for language in languages:
        vacancies_found = vacancies[language]["vacancies_found"]

        vacancies_by_language = vacancies[language]["items"]

        salaries = get_salaries_hh(vacancies_by_language)
        rub_salaries = get_rub_average_salaries(salaries)
        average_salary, vacancies_processed = get_average_salary(rub_salaries)

        salary_by_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }

    return salary_by_languages


def sj_get_salary_by_language(languages):
    vacancies = collect_vacancies_sj(languages)

    salary_by_languages = {}

    for language in languages:
        vacancies_found = vacancies[language]["vacancies_found"]

        vacancies_by_language = vacancies[language]["items"]

        salaries = get_salaries_sj(vacancies_by_language)
        rub_salaries = get_rub_average_salaries(salaries)
        average_salary, vacancies_processed = get_average_salary(rub_salaries)

        salary_by_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }

    return salary_by_languages


def create_table(title, packed_salaries, programming_languages):
    table_data = [
        ("Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата")
    ]
    for language in programming_languages:
        found, processed, salary = packed_salaries[language].values()
        format = (
            language,
            found,
            processed,
            salary
        )
        table_data.append(format)

    table_instance = AsciiTable(table_data, title)
    return table_instance.table


if __name__ == '__main__':
    load_dotenv()

    programming_languages = (
        "javascript",
        "java",
        "python",
        "ruby",
        "php",
        "c++",
        "css",
        "c#",
        "c",
        "go",
    )

    sj_programmer_salaries = sj_get_salary_by_language(programming_languages)
    hh_programmer_salaries = hh_get_salary_by_language(programming_languages)

    print(create_table("HeadHunter Moscow", hh_programmer_salaries, programming_languages))
    print()
    print(create_table("SuperJob Moscow", sj_programmer_salaries, programming_languages))
