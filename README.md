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
```
POST /registration/
{
    "username": "darklorian",
    "password": "baselorian_password"
}
```
В случае успеха ответ будет:
```
HTTP/1.1 201 Created
{
    "id": 1,
    "date_joined": datetime.now(),
    "username": "darklorian"
}
```