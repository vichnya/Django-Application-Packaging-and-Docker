# Django Application Packaging and Docker

Учебный проект, посвящённый упаковке Django-приложения в Python-пакет и его контейнеризации с помощью Docker.

## 1. Упаковка Django-приложения

«Упакованное» Django-приложение находится в каталоге `django-polls`.

Для создания дистрибутива используется команда:

```bash
python setup.py sdist
```

Инструкция по упаковке выполнена по [туториалу Django](https://docs.djangoproject.com/en/3.2/intro/reusable-apps/).

## 2. Контейнеризация приложения

Контейнеризованный вариант приложения находится в каталоге Django-Polls-Statistics-API-main

Для сборки и запуска контейнера используется:

```bash
docker-compose up -d
```

Инструкция по контейнеризации выполнена по [туториалу](https://pythonru.com/uroki/docker-django).

## Технологии

* Python
* Django
* Docker
* Docker Compose
* setuptools
* Python Packaging

## Результат

В рамках проекта изучены базовые принципы упаковки Django-приложений в Python-дистрибутив и контейнеризации приложения с использованием Docker.
