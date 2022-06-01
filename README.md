# -language-salary-collector
 
This script created to collect programmer vacancies from [SuperJob](http://SuperJob.ru) and [HeadHunter](http://hh.ru) 
and return table with average salaries, separated by programming languages

Returned table looks like:

```commandline
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| javascript            | 3106             | 792                 | 192262           |
| java                  | 2355             | 375                 | 227316           |
...
| go                    | 663              | 139                 | 261191           |
+-----------------------+------------------+---------------------+------------------+
```

## How to install

Download files from repository and install needed libs from `requirements.txt`

```commandline
pip install -r requirements.txt
```

For script correct working, you must create `.env` file and get SJ-Api-Key here -> 
[SJ-Api](https://api.superjob.ru/)

After registration you get "Secret Key", looks like `v3.r.13665..."a lot of letters and nums"`

Add this to `.env` file

```
X-Api-App-Id="your_secret_key_here"
```

Programm is ready to work. Open console, run programm and get_result!

```commandline
C:\Users\...\python language_salary.py
```

## Project Goals

The code is written for educational purposes on online-course for web-developers dvmn.org.