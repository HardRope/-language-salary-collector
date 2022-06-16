import os

from dotenv import load_dotenv

import requests
from terminaltables import AsciiTable

def collect_vacancies_sj(language, app_id):
    auth = {
        "X-Api-App-Id":
            app_id,
    }
    url = "https://api.superjob.ru/2.0/vacancies/"

    page = 0
    page_numbers = 1

    language_vacancies = {
        "items": [],
        "vacancies_found": 0
    }

    while page < page_numbers:
        params = {
            "town": '4',
            "catalogue": 48,
            "keyword": f"программист {language}",
            "count": 20,
            "page": page,
        }

        response = requests.get(url, headers=auth, params=params)
        response.raise_for_status()

        vacancies = response.json()

        page_numbers = vacancies["total"] // 20 + 1
        page += 1

        language_vacancies["items"].extend(vacancies["objects"])
        language_vacancies["vacancies_found"] = vacancies["total"]

    return language_vacancies


def get_salary_sj(vacancy):
    currency = vacancy["currency"]
    salary_from = vacancy["payment_from"]
    salary_to = vacancy["payment_to"]

    if not salary_from and not salary_to:
        return None

    salary = {
        "currency": currency,
        "from": salary_from,
        "to": salary_to,
    }
    return salary


def collect_vacancies_hh(language):
    hh_url = "https://api.hh.ru/vacancies/"

    page = 0
    pages_number = 1

    languages_vacancies = {
        "items": [],
        "vacancies_found": 0
    }

    while page < pages_number:
        params = {
            "text": f"программист {language}",
            "period": 30,
            "area": 1,
            "page": page
        }

        response = requests.get(hh_url, params=params)
        response.raise_for_status()

        vacancies = response.json()

        languages_vacancies["items"].extend(vacancies["items"])
        languages_vacancies["vacancies_found"] = vacancies["found"]

        pages_number = vacancies["pages"]
        page += 1

    return languages_vacancies


def get_rub_average_salaries(salary_from, salary_to, currency):
    if currency not in ("RUR", "rub"):
        return None
    if not salary_from and not salary_to:
        return None

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2

    elif not salary_from:
        return salary_to * 0.8

    elif not salary_to:
        return salary_from * 1.2


def get_average_salary(salaries):
    salaries_sum = 0
    counter = 0

    for salary in salaries:
        if salary:
            salaries_sum += salary
            counter += 1

    average = int(salaries_sum // counter)
    return average, counter


def get_salary_by_language_hh(languages):
    vacancies = {}
    for language in languages:
        vacancies[language] = collect_vacancies_hh(language)

    salary_by_languages = {}

    for language in languages:
        vacancies_found = vacancies[language]["vacancies_found"]

        vacancies_by_language = vacancies[language]["items"]

        salaries = []
        for vacancy in vacancies_by_language:
            salaries.append(vacancy["salary"])

        rub_salaries = []
        for salary in salaries:
            if salary:
                rub_salary = get_rub_average_salaries(salary["from"], salary["to"], salary["currency"])
            else:
                rub_salary = None

            if rub_salary:
                rub_salaries.append(rub_salary)

        average_salary, vacancies_processed = get_average_salary(rub_salaries)

        salary_by_languages[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }

    return salary_by_languages


def get_salary_by_language_sj(languages, app_id):
    vacancies  = {}
    for language in languages:
        vacancies[language] = collect_vacancies_sj(language, app_id)

    salary_by_languages = {}

    for language in languages:
        vacancies_found = vacancies[language]["vacancies_found"]

        vacancies_by_language = vacancies[language]["items"]

        salaries = []
        for vacancy in vacancies_by_language:
            salaries.append(get_salary_sj(vacancy))

        rub_salaries = []
        for salary in salaries:
            if salary:
                rub_salary = get_rub_average_salaries(salary["from"], salary["to"], salary["currency"])
            else:
                rub_salary  = None

            if rub_salary:
                rub_salaries.append(rub_salary)

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

    sj_app_id = os.getenv("X-Api-App-Id")
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

    sj_programmer_salaries = get_salary_by_language_sj(programming_languages, sj_app_id)
    hh_programmer_salaries = get_salary_by_language_hh(programming_languages)

    print(create_table("HeadHunter Moscow", hh_programmer_salaries, programming_languages))
    print()
    print(create_table("SuperJob Moscow", sj_programmer_salaries, programming_languages))
