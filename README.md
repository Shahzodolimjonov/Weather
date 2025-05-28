# Weather Project

## Функциональность

В проекте реализованы следующие функции:

- Получение данных о погоде по названию города через API  
- Сохранение истории поисков (по IP и пользователю)  
- Кэширование погодных данных с использованием Redis  
- Предоставление статистики поисковых запросов  
- Создание REST API на базе Django REST Framework  
- Контейнеризация приложения с помощью Docker и Docker Compose  
- Написание и выполнение unit-тестов с использованием pytest  

## Используемые технологии

- Python 3.10  
- Django 5.0.6  
- Django REST Framework  
- Redis (для кэширования)  
- Docker и Docker Compose  
- pytest (для тестирования)  

## Запуск проекта

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone <URL-репозитория>
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

2. Запустите Docker-контейнеры:
   
```bash
docker-compose up -d
```
3. Для запуска тестов выполните:
   
```bash
docker-compose run test
```
