# Referral API Service

## Описание
Простой RESTful API сервис для реферальной системы, который позволяет пользователям регистрироваться, аутентифицироваться, создавать и использовать реферальные коды. Проект построен с использованием современных технологий и фокуса на чистоту, читаемость кода и устойчивость к неправильным действиям пользователя.

## Функциональные возможности

### Основные функции:
- **Регистрация и аутентификация пользователя** (JWT, OAuth 2.0)
- **Управление реферальным кодом**: аутентифицированный пользователь может создать или удалить свой реферальный код. В один момент времени активен только один код. При создании кода обязательно указывается срок его действия.
- **Запрос реферального кода по email реферера**
- **Регистрация по реферальному коду**: пользователи могут зарегистрироваться с использованием реферального кода, становясь рефералами.
- **Получение информации о рефералах** по `id` реферера


## Структура API
- **POST /api/user/new**: Регистрация нового пользователя c возможностью отправить реферальный код.
- **POST /api/user/referral**: Создание нового реферального кода (требует аутентификации)
- **DELETE /api/user/referral**: Удаление текущего реферального кода пользователя (требует аутентификации)
- **GET /api/user/referral?user_id=id**: Получение информации о рефералах по id реферера
- **GET /api/user/referral/email**: Получение реферального кода по email реферера

- **POST /api/auth/login**: Аутентификация пользователя и получение токена JWT
- **POST /api/auth/token**: Обновление токена JWT по refresh JWT
- **POST /api/auth/logout**: Удаление refresh JWT из куков.


## Как Запустить?

#### Получаем исходники:
```shell
git clone https://github.com/Miron-Anosov/ReferAPI.git
```

#### Создаем приватный ключ необходимый для JWT
```shell
openssl genrsa -out jwt-private.pem 2048
```

#### Теперь создаем на его основании публичный ключ.

```shell
openssl rsa  -in src/certs/jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

####  Применяем .env.template

- Создаем `.env`
- Вписываем чувствительные данные в `.env` по шаблону `.env.template`
- В том числе сгенерированные ключи в соответсвующее поля.

#### Запускаем докер:
```shell
cd ./.;
docker compose up -d
```

####  Проверяем по адресу Swagger:
http://your-url:80/api/docs


