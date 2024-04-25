# blogicum на FASTAPI

Подключаем и настраиваем алембик:

$ alembic init migration
В файле alembic.ini указываем адрес базы:

[alembic]
...
sqlalchemy.url = postgresql://romblin@localhost/db
В файле migration/env.py импортируем все модели и указываем target_metadata:

from db import *
target_metadata = Base.metadata


alembic revision --autogenerate -m 'initial'
alembic upgrade head