# Социальная сеть YaTube.

Социальная сеть с возможностью создания, просмотра, редактирования и удаления (CRUD) записей. Реализован механизм подписки на понравившихся авторов и отслеживание их записей. Покрытие тестами. Возможность добавления изображений.

* Инструментарий:
  * Django 2.2
  * Python 3.8
  * Django Unittest
  * Django debug toolbar
  * PostgreSQL
  * Django ORM

* Запуск:
  * Установка зависимостей:
    * `pip install -r requirements.txt`
  * Применение миграций:
    * `python manage.py makemigrations`
    * `python manage.py migrate`
  * Создание администратора:
    * `python manage.py createsuperuser`
  * Запуск приложения:
    * `python manage.py runserver`
