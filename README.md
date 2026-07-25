[![Foodgram Workflow](https://github.com/polinakobzareva/foodgram/actions/workflows/main.yaml/badge.svg)](https://github.com/polinakobzareva/foodgram/actions/workflows/main.yaml)

# Foodgram

Фудграм - это сайт, где вы можете публиковать свои рецепты, добавлять чужие рецепты в избранное, подписываться на авторов и собирать автоматически корзину покупок и сохранять ее в виде файла.

## Основные возможности
- Регистрация пользователей.
- Просмотр списка рецептов.
- Создание, редактирование и удаление ваших рецептов.
- Добавление рецептов в избранное и корзину покупок.
- Подписка и просмотр других авторов.
- Возможность установить аватарку.

## Стек технологий
- Python
- Django
- DRF
- Djoser
- POstgresql
- Docker

## Развернуть проект локально:
Клонируйте репозиторий командой git clone. 

Создайте и активируйте виртуальное окружение
```
python -m venv venv
source venv/bin/activate
```

выполните 
```
pip install -r requirements.txt
```

Перейдите в дирeкторию cd backend

Сделайте миграции
```
python manage.py makemigrations
python manage.py migrate
```
Загрузите ингридиенты

```
python manage.py load_ingredients
```
Создайте админа

```
python manage.py createsuperuser
``` 
Запустите сервер

```
python manage.py runserver
```


## Развернуть проект в контейнере:

Создайте в корне проекта папку .env ссо следующими переменными:
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DB_HOST=db
DB_PORT=5432
SECRET_KEY=
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1,ваш_домен

Запустите контейнеры из корня проекта:

```
docker compose -f docker-compose.production.yml up -d
```

Выполните миграции 
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Соберите статику
```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```


Загрузите ингридиенты:
```
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
```

Создайте админа:
```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Документация апи:
http://158.160.180.237:8000/api/docs/

## Ссылка на развернутый проект:
http://158.160.180.237:8000

### Автор проекта: Кобзарева Полина
GitHub: https://github.com/polinakobzareva/foodgram/
Почта: polinakobzarevapolina@mail.ru