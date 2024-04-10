# hohotach-salute-backend

## Генератор анекдотов
### Основная идея
Приложение позволяет выводить пользователю на экран анекдоты с помощью графического интерфейса или голосового помощника. Анекдоты загружаются с открытых API. Пользователь может сохранять анекдоты в избранное.

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
4. Запускаем саму программу
