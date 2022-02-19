release: python manage.py makemigrations quiz && python manage.py migrate quiz
web: gunicorn --pythonpath buzzquiz lets_quiz.wsgi