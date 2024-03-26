# hohotach-salute-backend
## хихи хаха
## Запуск
0. Нужен [docker](!https://docs.docker.com/engine/install/)
1. Установить библиотеки
```
pip install -r requirements.txt
```
2. Запустить контейнер:
```
docker-compose -f docker-compose-local.yaml up -d
```
3. Миграции 
```
alembic init -t async migarions
```
- В alembic.ini нужно задать адрес базы данных, в которую будем катать миграции.
- Дальше идём в папку с миграциями и открываем env.py, там вносим изменения в блок, где написано 

```
from myapp import mymodel
```

- Вводим для создания миграции: 
```
alembic revision --autogenerate -m "comment"
``` 

- Вводим:
```
alembic upgrade heads
```
