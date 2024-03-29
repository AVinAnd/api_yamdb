# API_YamDB

REST API для сервиса YaMDb — базы отзывов о фильмах, книгах и музыке.

Проект YaMDb собирает отзывы пользователей на произведения, 
сами произведения в YaMDb не хранятся. Каждому произведению
можно поставить рейтинг, и оставить отзыв.

## Технологии и запуск проекта

Проект написан на языке python, с использованием django
и django REST framework. Необходимые для работы проекта
зависимости описаны в файле requirements.txt

Документация проекта доступна по адресу 
http://0.0.0.0:8000/redoc/

Для запуска проекта:
- Клонируйте репозиторий
``` 
- git clone https://github.com/AVinAnd/api_yamdb.git 
```
- Активируйте виртуальное окружение 

```
python -m venv venv
source venv/scripts/activate
```
- Установите зависимости

``` 
pip install -r requirements.txt
```
- Выполните миграции 
```
python manage.py makemigrations
python manage.py migrate
```
- Запустите проект
```
python manage.py runserver
```

Проект доступен по адресу http://127.0.0.1:8000/

## Ресурсы API YaMDb
- api/v1/auth : аутентификация.

- api/v1/users: пользователи.

- api/v1/titles: произведения, к которым пишут отзывы.

- api/v1/categories: категории произведений.

- api/v1/genres: жанры произведений. 

- api/v1/reviews: отзывы на произведения. 

- api/v1/comments: комментарии к отзывам. 

Каждый ресурс описан в документации.

## Регистрация пользователей
### Самостоятельная регистрация новых пользователей
- Пользователь отправляет POST-запрос с параметрами 
email и username на эндпоинт /api/v1/auth/signup/.
- Сервис YaMDB отправляет письмо с кодом подтверждения
на указанный адрес email.
- Пользователь отправляет POST-запрос с параметрами 
username и confirmation_code на эндпоинт /api/v1/auth/token/,
в ответе на запрос ему приходит JWT-токен.

После регистрации и получения токена пользователь 
может отправить PATCH-запрос на эндпоинт 
/api/v1/users/me/ и заполнить поля в своём профайле.
### Создание пользователя администратором
- Пользователей создаёт администратор — 
через админ-зону сайта или через POST-запрос на 
специальный эндпоинт api/v1/users/.
- После этого пользователь должен самостоятельно 
отправить свой email и username на эндпоинт 
/api/v1/auth/signup/ , в ответ ему должно прийти 
письмо с кодом подтверждения.
- Далее пользователь отправляет POST-запрос 
с параметрами username и confirmation_code на 
эндпоинт /api/v1/auth/token/, в ответе на запрос 
ему приходит JWT-токен, как и при самостоятельной 
регистрации.

### Об авторе
Андрей Виноградов - python-developer, выпускник Яндекс Практикума по курсу Python-разработчик
