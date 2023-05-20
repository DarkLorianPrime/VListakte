# Blogs service "ВЛистакте"
## About project
Сервис, предоставляющий возможности полноценного блога, с использованием `fastapi` и `sqlalchemy`
## Built with
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

## RoadMap
- [x] Начать проект
- [x] Написать кастомный мигратор
- [x] Сделать основной функционал
- [x] Написать unittest
- [x] Написать ReadMe
- [x] Переписать ORM с нуля
- [x] Написать OpenApi спецификацию
- [ ] Написать полноценную документацию для проекта

## Examples
В этом разделе мы рассмотрим несколько основных примеров использования API, созданного с использованием FastAPI в рамках этого проекта.
### Регистрация пользователя
POST /api/v1/registration/
```json
{
    "username": "darklorian",
    "password": "baselorian_password"
}
```
В случае успеха ответ будет:

HTTP/1.1 201 Created
```json
{
    "access_token": "5f77ac60-0e7b-42ba-bbaf-73739d1fec9a"
}
```
### Создание блога
POST /api/v1/

authorization: token 5f77ac60-0e7b-42ba-bbaf-73739d1fec9a
```JSON
{
    "title": "FastAPI Education",
    "description": "Блог, в котором я хвастаюсь своими достижениями в IT",
    "authors": "2, 5, 100, 202"
}
```
В случае успеха ответ будет:

HTTP/1.1 201 Created
```json
{
    "id": "bdf477c5-1f56-429a-b6d9-1d47c3f6b54a",
    "title": "FastAPI Education",
    "description": "Блог, в котором я хвастаюсь своими достижениями в IT",
    "created_at": "2023-05-20T19:51:49.766519",
    "updated_at": "2023-05-20T19:51:49.766519",
    "owner_id": 1,
    "authors": []
}
```
* authors пустой, потому что пользователей с переданными ID не существует
* часть примеров описана в tests, но не все.

## Install
#### Предполагается, что docker, compose, nginx и их зависимости уже установлены
Клонируем репозиторий
```bash
$ git clone https://github.com/DarkLorianPrime/vlistakte
$ cd fastapi_blog
$ tree
.
├── backend
│   ├── app
│   │   ├── extras
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   └── values_helper.py
│   │   ├── libraries
│   │   │   ├── database
│   │   │   │   ├── __init__.py
│   │   │   │   └── migrator.py
│   │   │   ├── examples
│   │   │   │   ├── __init__.py
│   │   │   │   ├── migration_example_001.py
│   │   │   │   └── migration_example.py
│   │   │   ├── __init__.py
│   │   │   ├── orm
│   │   │   │   ├── core.py
│   │   │   │   ├── database.py
│   │   │   │   └── fields.py
│   │   │   └── utils
│   │   │       ├── exceptions.py
│   │   │       ├── files.py
│   │   │       ├── __init__.py
│   │   │       ├── pydantic_base.py
│   │   │       └── tests.py
│   │   ├── main.py
│   │   ├── manage.py
│   │   ├── migrations
│   │   │   ├── 001_initial-2022-03-11-20-07-06.py
│   │   │   ├── 002_user-2022-03-11-22-26-57.py
│   │   │   ├── 003_user_add_usertoken-2022-03-11-22-52-48.py
│   │   │   ├── 004_user_roles_mtm-2022-03-12-18-44-31.py
│   │   │   ├── 005_create_blog-2022-04-07-18-47-09.py
│   │   │   ├── 006_create_posts-2022-06-14-03-13-39.py
│   │   │   ├── 007_post_views-2022-06-14-14-47-18.py
│   │   │   ├── 008_post_likes-2022-06-14-14-47-24.py
│   │   │   ├── 009_commentaries-2022-06-14-14-47-34.py
│   │   │   └── 010_comment_likes-2022-06-23-10-24-16.py
│   │   ├── poetry.lock
│   │   ├── pyproject.toml
│   │   ├── routers
│   │   │   ├── authserver
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py
│   │   │   │   ├── pydantic_models.py
│   │   │   │   ├── repositories.py
│   │   │   │   ├── responses.py
│   │   │   │   └── routers.py
│   │   │   ├── blogs
│   │   │   │   ├── blogs.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py
│   │   │   │   ├── pydantic_models.py
│   │   │   │   ├── repositories.py
│   │   │   │   └── responses.py
│   │   │   ├── __init__.py
│   │   │   └── posts
│   │   │       ├── __init__.py
│   │   │       ├── models.py
│   │   │       ├── posts.py
│   │   │       ├── pydantic_models.py
│   │   │       ├── repositories.py
│   │   │       └── responses.py
│   │   └── tests.py
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yaml
└── README.md
```
- устанавливаем ENV
```bash
$ mv .example.env .env
$ nano .env

--.env--
POSTGRES_USER=      ->  troot
POSTGRES_PASSWORD=  ->  troot_password
POSTGRES_NAME=      ->  troot # PG_NAME=PG_USER
POSTGRES_HOST=      ->  database #compose_database_name
SECURITY_TOKEN=   -> blabla123_please_save_yes_save_my_passwords
--------
```
- Запускаем docker-compose
```bash
$ docker-compose up -d --build
```
Вы должны увидеть надписи
```
Creating fastapi_blog_backend_1  ... done
Creating fastapi_blog_database_1 ... done
```

Сервис запущен и готов к работе. Можно подключать к nginx и зарабатывать миллионы лисобаксов.

# Contacts
Grand developer - [@darklorianprime](https://vk.com/darklorianprime) - kasimov.alexander.ul@gmail.com