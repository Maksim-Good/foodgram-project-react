# Фудграм

https://maksgramm.myftp.org/
admin_login = admin@admin.re
admin_pass = adminadmin

## Описание:

Сайт на котором пользователи могут читать рецепты. Авторизованные пользователи могут быть автором своих рецептов, подписываться на других авторов, добавлять рецепты в избранное, добавлять рецепты в корзину и скачивать ингредиенты для них, а также фильтровать рецепты по тегам, избранному и автору.

### Рецепт состоит из 6 полей:
- название рецепта
- теги
- ингредиенты
- время приготовления
- описание рецепта
- фото

## Как запустить проект локально на компьютере:

1. Необходимо скачать, установить и запустить Docker: https://www.docker.com/

2. В консоли перейти в папку foodgram-project-react/infra/ и выполнить команды:
- cp .env.example .env
- docker compose up -d
- docker exec -it infra-backend-1 bash
- python manage.py migrate
- python manage.py load_data
- python manage.py collectstatic
- cp -r /app/collected_static/. /backend_static/static/
- python manage.py createsuperuser

3. Проект будет доступен по адресу:
- http://127.0.0.1:8080 - основной сайт
- http://127.0.0.1:8080/admin/ - администрирование
- http://127.0.0.1:8080/api/docs/redoc.html - документация по API 

4. Необходимо войти за суперюзера в админку и создать теги. Без тегов создавать рецепты нельзя.

## Для удаленного запуска на сервере:

1. Настроить порт внешнего нгинкса 
- sudo nano /etc/nginx/sites-enabled/default
- вставить:

`

    server {
        server_name <ваш айпи> <ваш домен>;'
        
        server_tokens off;
        location / {
            proxy_set_header Host $http_host;
            proxy_pass http://127.0.0.1:8080;
        }
    }


2. повторить все тоже что при локальном развертывании


## Авторы бекенда:
Максим

