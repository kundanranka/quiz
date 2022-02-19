release: python buzzquiz/manage.py makemigrations quiz && python buzzquiz/manage.py migrate quiz
web: gunicorn --pythonpath buzzquiz lets_quiz.wsgi