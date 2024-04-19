# Проект парсинга pep

## Описание
Программа позволяет парсить данные о статусе всех руководств PEP и обновлениях Python. Кроме того, доступна загрузка последней версии.
Полученную информацию можно вывести в консоль текстом или в виде таблицы, а также сохранить в формате .csv.

## Технологии
attrs==21.4.0
beautifulsoup4==4.9.3
certifi==2021.10.8
chardet==4.0.0
charset-normalizer==2.0.12
flake8==4.0.1
idna==2.10
importlib-metadata==4.2.0
iniconfig==1.1.1
itsdangerous==2.1.1
lxml==4.6.3
mccabe==0.6.1
packaging==21.3
pluggy==1.0.0
prettytable==2.1.0
py==1.11.0
pycodestyle==2.8.0
pyflakes==2.4.0
pyparsing==3.0.7
pytest==7.1.0
requests==2.27.1
requests-cache==1.0.0
requests-mock==1.9.3
six==1.16.0
soupsieve==2.3.1
tomli==2.0.1
tqdm==4.61.0
typing_extensions==4.1.1
url-normalize==1.4.3
urllib3==1.26.8
wcwidth==0.2.5
zipp==3.7.0

## Как использовать

Запуск производится из консоли:

```
cd bs4_parser_pep/src
python main.py -h
```

Обязательным является параметр, определяющий режим работы:

```
python main.py whats-new         # Cсылки на описание последних обновлений и автор/редактор
python main.py latest-versions   # Ссылки на последние версии и их статус
python main.py download          # Загрузка последней версии
python main.py pep               # Общее количество руководств PEP и разбивка по статусам
```

Загруженная версия сохраняется в папке
```
cd bs4_parser_pep/src/downloads/
```

По умолчанию, данные выводятся текстом в консоль.
Опциональные параметры позволяют очистить кэш и определить формат вывода данных:

```
python main.py whats-new --clear-cache     # Очистка кэша
python main.py whats-new --output pretty   # Вывод данных в виде таблицы
python main.py whats-new --output file     # Сохранение данных в csv-файле
```

В случае сохранения данных в csv-файле, файл можно найти в папке
```
cd bs4_parser_pep/src/results/
```

## Автор

Vsevolod25: https://github.com/Vsevolod25
