# homework_bot
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, когда статус изменен.
Технологии:
Python 3.7
python-dotenv 0.19.0
python-telegram-bot 13.7
Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке

Cоздать и активировать виртуальное окружение

Установить зависимости из файла requirements.txt:

python -m pip install --upgrade pip
pip install -r requirements.txt

Записать в переменные окружения (файл .env) необходимые ключи:

токен профиля на Яндекс.Практикуме
токен тг-бота
свой ID в тг
Запустить проект:

python homework.py
