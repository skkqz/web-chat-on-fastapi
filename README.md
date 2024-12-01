# Веб чат в реальном времени на FastApi.



### Команды alembic 
* Команда инициализирует проект миграций с использованием Alembic для асинхронного взаимодействия с базой данных.
~~~Pathon
alembic init -t async migration
~~~
* Не забудьте настроить alembic.ini, migration/env.py
* Генерируем файлы миграции 
~~~Pyyhon
alembic revision --autogenerate -m "Initial revision"
~~~
* Применяем миграции 
~~~Pyyhon
alembic upgrade head
~~~