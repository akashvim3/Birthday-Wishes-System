.PHONY: help install migrate run test clean docker-build docker-up docker-down

help:
\t@echo "Available commands:"
\t@echo "  install        Install dependencies"
\t@echo "  migrate        Run database migrations"
\t@echo "  makemigrations Create new migrations"
\t@echo "  run            Run development server"
\t@echo "  test           Run tests"
\t@echo "  clean          Remove Python cache files"
\t@echo "  superuser      Create superuser"
\t@echo "  shell          Open Django shell"
\t@echo "  docker-build   Build Docker containers"
\t@echo "  docker-up      Start Docker containers"
\t@echo "  docker-down    Stop Docker containers"

install:
\tpip install -r requirements.txt

migrate:
\tpython manage.py migrate

makemigrations:
\tpython manage.py makemigrations

run:
\tpython manage.py runserver

test:
\tpython manage.py test

clean:
\tfind . -type d -name __pycache__ -exec rm -r {} +
\tfind . -type f -name "*.pyc" -delete
\tfind . -type f -name "*.pyo" -delete

superuser:
\tpython manage.py createsuperuser

shell:
\tpython manage.py shell

collectstatic:
\tpython manage.py collectstatic --noinput

docker-build:
\tdocker-compose build

docker-up:
\tdocker-compose up -d

docker-down:
\tdocker-compose down

docker-logs:
\tdocker-compose logs -f

celery-worker:
\tcelery -A birthday_system worker -l info

celery-beat:
\tcelery -A birthday_system beat -l info
