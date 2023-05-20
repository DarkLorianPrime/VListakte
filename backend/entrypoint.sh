#!/bin/bash
python manage.py migrator migrate
python manage.py runserver