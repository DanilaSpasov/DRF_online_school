# DRF Online School

**drf_online_school** - Django-проект с REST API для онлайн-школы. Проект включает работу с базой данных PostgreSQL, использование Django REST Framework, полноценный CRUD для курсов и уроков, подписки на курсы, пользовательскую модель авторизации, документацию API, оплату курсов через Stripe, фоновые задачи Celery и email-уведомления.

---

# Технологии и стек

* **Фреймворк:** Django 6
* **API Framework:** Django REST Framework 3.17
* **Язык программирования:** Python 3.14
* **СУБД:** PostgreSQL
* **ORM:** Django ORM
* **Брокер сообщений:** Redis 7.2
* **Python-клиент Redis:** redis-py 6.4
* **Фоновые задачи:** Celery 5.6
* **Периодические задачи:** django-celery-beat 2.9
* **Контроль версий:** Git / GitHub
* **Аутентификация:** JWT (JSON Web Tokens)
* **Документация API:** drf-spectacular 0.30 (Swagger UI / ReDoc)
* **Платежный сервис:** Stripe SDK 15.4 / Stripe Checkout
* **Отправка писем:** SMTP Яндекса
* **Пользовательская модель:** AbstractUser
* **Менеджер зависимостей:** Poetry

---

# База данных

Проект использует PostgreSQL.

Настройки подключения задаются в файле `settings.py` через переменные окружения.

Для работы необходимо:

1. установить зависимости проекта;
2. создать файл `.env` по примеру `.env_example`;
3. заполнить параметры подключения к базе данных, `SECRET_KEY`, настройки Stripe, Redis и почты.


---

# Структура проекта

Проект состоит из двух приложений:

* **lms** - управление курсами и уроками;
* **users** - приложение для работы с пользователями и аутентификацией.

---

# Функциональность

## Управление курсами

Реализовано:

- Отображение списка курсов
- Создание курса
- Просмотр детальной информации о курсе
- Редактирование курса
- Удаление курса
- Загрузка превью изображения курса
- Связь уроков с курсами
- Цена курса
- Дата последнего обновления курса
- Пагинация списка курсов

Используется `ModelViewSet` для полного CRUD операций через REST API.

---

## Управление уроками

Реализовано:

- Отображение списка уроков
- Создание урока
- Просмотр детальной информации об уроке
- Редактирование урока
- Удаление урока
- Загрузка превью изображения урока
- Ссылка на видео урока
- Привязка урока к курсу
- Проверка, что ссылка на видео ведет на YouTube
- Пагинация списка уроков

Используются `ListCreateAPIView` и `RetrieveUpdateDestroyAPIView` для работы с уроками.

---

## Подписки

Реализовано добавление и удаление подписки пользователя на курс. Повторный POST-запрос для того же курса переключает состояние подписки.

В данных курса возвращается поле `is_subscribed`, которое показывает, подписан ли текущий пользователь.

При обновлении курса в контроллере вызывается фоновая Celery-задача. Письмо об изменении курса отправляется пользователям, подписанным именно на этот курс.

---

## Платежи

Реализовано:

- Отображение списка платежей
- Фильтрация по курсу, уроку и способу оплаты
- Сортировка по дате оплаты (возрастание/убывание)
- Создание платежа за выбранный курс
- Создание продукта, цены и платежной сессии в Stripe
- Сохранение и возврат ссылки Stripe Checkout

Для списка используется `ListAPIView` с фильтрацией через `DjangoFilterBackend` и сортировкой через `OrderingFilter`. Взаимодействие со Stripe вынесено в сервисные функции.

---

## Фоновые и периодические задачи

Реализовано:

- Отправка писем подписчикам после обновления курса
- Передача фоновых задач через брокер Redis
- Хранение результатов выполнения задач в Redis
- Автоматический поиск задач Celery в приложениях Django
- Ежедневная проверка пользователей по полю `last_login`
- Блокировка пользователей, которые не заходили более 30 дней, через флаг `is_active`
- Планирование периодической задачи через `django-celery-beat`

Для Django и Celery используется единый часовой пояс `UTC`.

---

# Пользователи и аутентификация

Для работы с пользователями создано отдельное приложение `users`.

Реализована собственная модель пользователя на основе `AbstractUser`.

## JWT-авторизация

Проект использует JWT (JSON Web Tokens) для аутентификации пользователей через `rest_framework_simplejwt`.

Настройки токенов:
- **Access Token:** 15 минут
- **Refresh Token:** 1 день

При получении новой пары токенов обновляется поле пользователя `last_login`. Это значение используется периодической Celery-задачей для проверки активности пользователей.

Все API endpoints защищены авторизацией, кроме:
- `/users/register/` - регистрация пользователя
- `/users/token/` - получение токена
- `/users/token/refresh/` - обновление токена
- `/api/schema/` - OpenAPI-схема
- `/api/schema/swagger-ui/` - Swagger UI
- `/api/schema/redoc/` - ReDoc

Для авторизации необходимо включить JWT токен в заголовок запроса:
```
Authorization: Bearer <access_token>
```

## Регистрация пользователей

Реализован endpoint для регистрации пользователей через POST запрос на `/users/register/`.

Поля для регистрации:
- `email` - электронная почта (обязательно, уникально)
- `password` - пароль (обязательно)
- `phone` - номер телефона (опционально)
- `city` - город (опционально)
- `avatar` - изображение профиля (опционально)

## Управление профилем

Для авторизованных пользователей реализованы получение, обновление и удаление
профиля. Пользователь может работать только со своей учетной записью и не имеет
доступа к профилям других пользователей.

При обновлении пароля используется метод `set_password()`, поэтому пароль
сохраняется в базе данных в виде хеша и не возвращается в ответах API.

## Дополнительные поля пользователя

- `avatar` - изображение профиля;
- `phone` - номер телефона;
- `city` - город пользователя.

В качестве основного поля авторизации используется электронная почта. Поле `username` отключено.

---

# Модели

## Course

Поля:

* `title` - название курса;
* `preview` - изображение превью курса;
* `description` - описание курса;
* `owner` - владелец курса (`ForeignKey` к User);
* `price` - цена курса (`DecimalField`);
* `updated_at` - дата и время последнего обновления курса (`DateTimeField`).

---

## Lesson

Поля:

* `title` - название урока;
* `description` - описание урока;
* `preview` - изображение превью урока;
* `video_url` - ссылка на видео;
* `course` - курс (`ForeignKey`);
* `owner` - владелец урока (`ForeignKey` к User).

---

## User

Пользовательская модель создана на основе `AbstractUser`.

Поля:

* `email` - электронная почта пользователя (используется для авторизации);
* `password` - пароль пользователя;
* `avatar` - изображение профиля;
* `phone` - номер телефона;
* `city` - город пользователя.

---

## Payment

Модель для хранения информации о платежах пользователей.

Поля:

* `user` - пользователь, совершивший платеж (`ForeignKey`);
* `payment_date` - дата оплаты (`DateTimeField`);
* `course` - оплаченный курс (`ForeignKey`, nullable);
* `lesson` - оплаченный урок (`ForeignKey`, nullable);
* `amount` - сумма оплаты (`DecimalField`);
* `payment_method` - способ оплаты (choices: наличные/перевод/Stripe);
* `payment_url` - ссылка на страницу оплаты Stripe Checkout.

---

## Subscription

Модель хранит подписку пользователя на курс.

Поля:

* `user` - подписанный пользователь (`ForeignKey`);
* `course` - курс, на который оформлена подписка (`ForeignKey`).

---

# API Endpoints

## Курсы

* `GET /api/courses/` - список курсов, доступных текущему пользователю
* `POST /api/courses/` - создание нового курса
* `GET /api/courses/{id}/` - просмотр курса
* `PUT /api/courses/{id}/` - редактирование курса
* `PATCH /api/courses/{id}/` - частичное редактирование курса
* `DELETE /api/courses/{id}/` - удаление курса

---

## Уроки

* `GET /api/lessons/` - список уроков, доступных текущему пользователю
* `POST /api/lessons/` - создание нового урока
* `GET /api/lessons/{id}/` - просмотр урока
* `PUT /api/lessons/{id}/` - редактирование урока
* `PATCH /api/lessons/{id}/` - частичное редактирование урока
* `DELETE /api/lessons/{id}/` - удаление урока

---

## Подписки

* `POST /api/subscriptions/` - добавить или удалить подписку на курс

Тело запроса:

```
{
  "course_id": 1
}
```

---

## Пользователи и авторизация

* `POST /users/register/` - регистрация нового пользователя (доступно без авторизации)
* `POST /users/token/` - получение JWT токена (доступно без авторизации)
* `POST /users/token/refresh/` - обновление JWT токена (доступно без авторизации)
* `GET /users/` - получение списка, содержащего профиль текущего пользователя
* `GET /users/{id}/` - получение профиля текущего пользователя
* `PUT /users/{id}/` - полное обновление профиля текущего пользователя
* `PATCH /users/{id}/` - частичное обновление профиля текущего пользователя
* `DELETE /users/{id}/` - удаление профиля текущего пользователя

Все операции с профилем, кроме регистрации, доступны только после
JWT-авторизации. Получение, изменение и удаление чужого профиля запрещены.

## Платежи

* `GET /users/payments/` - список всех платежей с фильтрацией и сортировкой
* `POST /users/payments/create/` - создание платежа за курс и получение ссылки Stripe Checkout

Для создания платежа необходимо передать только идентификатор курса:

```
{
  "course": 1
}
```

Пользователь определяется по JWT-токену, сумма берется из цены курса, а способ оплаты и ссылка Stripe заполняются сервером. В ответ возвращаются данные созданного платежа, включая `payment_url`.

Параметры фильтрации:
* `course` - фильтрация по курсу
* `lesson` - фильтрация по уроку
* `payment_method` - фильтрация по способу оплаты

Параметры сортировки:
* `ordering=payment_date` - сортировка по дате оплаты по возрастанию
* `ordering=-payment_date` - сортировка по дате оплаты в обратном порядке

---

# Документация API

Документация формируется с помощью `drf-spectacular`.

После запуска проекта доступны:

* `/api/schema/` - OpenAPI-схема
* `/api/schema/swagger-ui/` - Swagger UI
* `/api/schema/redoc/` - ReDoc

Для выполнения защищенных запросов в Swagger необходимо получить JWT-токен и передать access-токен через кнопку **Authorize**.

Проверить корректность OpenAPI-схемы:

```
poetry run python manage.py spectacular --file schema.yml --validate
```

---


# Запуск проекта через Docker Compose

Установить Docker, запустить Docker Desktop и создать `.env`:

```
cp .env_example .env
```

Заполнить переменные по примеру. Значения `POSTGRES_DB`, `POSTGRES_USER` и
`POSTGRES_PASSWORD` должны совпадать с соответствующими данными.

При первом запуске собрать образ, поднять инфраструктуру, применить миграции,
собрать статические файлы и запустить все сервисы:

```
docker compose build
docker compose up -d db redis
docker compose run --rm web poetry run python manage.py migrate --noinput
docker compose run --rm web poetry run python manage.py collectstatic --noinput
docker compose up -d
```

Для обычного повторного запуска уже собранной версии:

```
docker compose up -d
```

При обновлении версии приложения нужно заново собрать образ, применить новые
миграции, обновить статические файлы и пересоздать контейнеры:

```
docker compose build
docker compose run --rm web poetry run python manage.py migrate --noinput
docker compose run --rm web poetry run python manage.py collectstatic --noinput
docker compose up -d --remove-orphans
```

Проверить состояние контейнеров и ответ приложения:

```
docker compose ps
curl --fail http://127.0.0.1:8000/api/schema/
```

Порт Gunicorn доступен только на `127.0.0.1:8000`. PostgreSQL и Redis
доступны только сервисам внутри Docker-сети.

Gunicorn не раздает каталоги `staticfiles` и `media`. На удаленном сервере
их обслуживает Nginx.

Остановить контейнеры:

```
docker compose down
```

Данные PostgreSQL и Redis сохраняются в volumes. Команда
`docker compose down -v` удаляет их вместе с данными.

---

# Деплой и CI/CD

## Подготовка удаленного сервера

На сервере с Ubuntu 24.04 установить необходимые программы:

```
sudo apt update
sudo apt install -y git docker.io docker-compose-v2 nginx
sudo systemctl enable --now docker nginx
sudo usermod -aG docker ubuntu
```

Переподключиться по SSH, затем клонировать проект и создать серверный `.env`:

```
git clone https://github.com/DanilaSpasov/DRF_online_school.git
cd DRF_online_school
cp .env_example .env
chmod 600 .env
```

В `.env` установить `DEBUG=False`, указать IP или домен в `ALLOWED_HOSTS` и
`CSRF_TRUSTED_ORIGINS`, заполнить остальные значения. Пароли
`DATABASE_PASSWORD` и `POSTGRES_PASSWORD` должны совпадать. Первый запуск
выполняется командами из раздела «Запуск проекта через Docker Compose».

## Настройка Nginx

Создать `/etc/nginx/sites-available/drf-online-school`, заменив `<SERVER_IP>`:

```
server {
    listen 80;
    server_name <SERVER_IP>;

    location /static/ {
        alias /home/ubuntu/DRF_online_school/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/DRF_online_school/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

Включить конфигурацию и применить её:

```
chmod 711 /home/ubuntu
sudo ln -s /etc/nginx/sites-available/drf-online-school \
  /etc/nginx/sites-enabled/drf-online-school
sudo unlink /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

В Yandex Cloud и UFW открыть только `22` для SSH и `80` для HTTP. Порты
`8000`, `5432` и `6379` наружу не открывать:

```
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
sudo ufw default deny incoming
sudo ufw enable
```

## GitHub Actions

Workflow `.github/workflows/ci-cd.yml` запускается при `push` и
`pull_request`:

```
lint → test → build → deploy
```

Этапы проверяют Black, Django, миграции и тесты, затем собирают Docker-образ.
При ошибке pipeline останавливается. Деплой выполняется только после успешного
`push` в `master`; для других веток и Pull Request он пропускается.

Для автоматического подключения к серверу в настройках репозитория
`Settings → Secrets and variables → Actions` создать Secrets: `SSH_KEY` —
закрытый ключ, `SSH_USER` — пользователь сервера, `SERVER_IP` — статический IP.

Для деплоя используется отдельная пара SSH-ключей: открытая часть добавляется
на сервер, закрытая сохраняется в `SSH_KEY`. Workflow обновляет `master`,
применяет миграции, собирает статику, запускает контейнеры и проверяет Django.

Проверка приложения:

```
http://<SERVER_IP>/api/schema/swagger-ui/
http://<SERVER_IP>/api/schema/redoc/
```

---

# Локальный запуск без Docker

Установить зависимости:

```
poetry install
```

Создать файл `.env` по примеру `.env_example` и заполнить параметры:

```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
DATABASE_NAME=lms_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
POSTGRES_DB=lms_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
STRIPE_API_KEY=sk_test_...
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/
STRIPE_CANCEL_URL=http://127.0.0.1:8000/
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
EMAIL_HOST_USER=your_email@yandex.ru
EMAIL_HOST_PASSWORD=your_app_password
```

База Redis `/0` используется как брокер задач, а `/1` - для хранения результатов выполнения.

Перед применением миграций PostgreSQL должен быть запущен, а база данных из `.env` должна быть создана.

Применить миграции:

```
poetry run python manage.py migrate
```

Команда применяет миграции проекта, включая таблицы `django-celery-beat` для периодических задач.

Загрузить фикстуру групп пользователей:

```
poetry run python manage.py loaddata users/fixtures/groups.json
```

При необходимости создать локальные демонстрационные платежи (команда не обращается к Stripe):

```
poetry run python manage.py create_payments
```

Если Redis еще не установлен, установить его через Homebrew:

```
brew install redis
```

Запустить Redis и проверить подключение:

```
brew services start redis
redis-cli ping
```

При успешном подключении Redis вернет `PONG`.

Запустить сервер:

```
poetry run python manage.py runserver
```

В отдельном терминале запустить Celery worker:

```
poetry run celery -A config worker --loglevel=info
```

В другом терминале запустить celery-beat:

```
poetry run celery -A config beat --loglevel=info
```

Для работы фоновых и периодических задач Redis, Django-сервер, Celery worker и celery-beat должны быть запущены одновременно.

Запустить тесты:

```
poetry run python manage.py test
```

---

# Проверка рассылки Celery

Для проверки отправки письма об обновлении курса необходимо:

1. Запустить Redis, Django-сервер и Celery worker.
2. Получить access-токен через `POST /users/token/`.
3. Оформить подписку через `POST /api/subscriptions/`.
4. Обновить курс через `PATCH /api/courses/{id}/`.
5. Проверить получение задачи и ее успешное выполнение в терминале Celery worker.
6. Проверить получение письма на почте подписанного пользователя.

В терминале worker должны появиться сообщения `received` и `succeeded` для задачи `lms.tasks.send_course_update_email`.

---

# Доступные страницы

После запуска проекта доступны маршруты:

* `/admin/` - панель администратора Django
* `/api/` - API endpoints для курсов и уроков
* `/users/` - API endpoints для пользователей и платежей
* `/api/schema/` - OpenAPI-схема
* `/api/schema/swagger-ui/` - интерактивная документация Swagger UI
* `/api/schema/redoc/` - документация ReDoc

---

# Тестирование оплаты Stripe

Оплата проверяется в тестовом режиме Stripe. После создания платежа endpoint возвращает `payment_url`, которую необходимо открыть в браузере.

Порядок проверки:

1. Получить access-токен через `POST /users/token/`.
2. Авторизоваться в Swagger UI.
3. Выбрать существующий курс с ценой больше нуля.
4. Выполнить `POST /users/payments/create/` с идентификатором курса.
5. Открыть полученную `payment_url` и заполнить тестовые данные карты.
6. Проверить созданную запись через `GET /users/payments/`.

Для успешной тестовой оплаты можно использовать:

* номер карты: `4242 4242 4242 4242`;
* срок действия: любая будущая дата;
* CVC: любые три цифры;
* остальные данные: любые допустимые значения.

После оплаты Stripe перенаправляет пользователя на адрес из `STRIPE_SUCCESS_URL`. Проверка и сохранение статуса платежа в проекте не реализованы.

---

# Система прав доступа и разрешений

## Группы пользователей

В проекте реализована система групп для разграничения прав доступа:

- **moderators** - группа модераторов с ограниченными правами на курсы и уроки

Фикстура для загрузки группы модераторов находится в `users/fixtures/groups.json`.

## Классы разрешений

В `users/permissions.py` реализованы следующие классы разрешений:

- **IsModer** - проверяет, является ли пользователь модератором (входит в группу "moderators")
- **IsOwner** - проверяет, является ли пользователь владельцем объекта
- Права можно объединять операторами `|` (ИЛИ) и `~` (отрицание), например
  `IsModer | IsOwner` и `~IsModer`

## Права доступа для курсов

**CourseViewSet:**
- **list** - требует авторизации (IsAuthenticated). Модераторы видят все курсы, обычные пользователи - только свои
- **create** - доступен только авторизованным пользователям, которые не входят в группу модераторов. Создатель автоматически назначается владельцем через `perform_create()`
- **retrieve** - доступен модератору или владельцу курса (`IsModer | IsOwner`)
- **update/partial_update** - доступен модератору или владельцу курса (`IsModer | IsOwner`)
- **destroy** - доступен только владельцу, который не является модератором (`~IsModer` и `IsOwner`)

## Права доступа для уроков

**LessonListAPIView:**
- **list** - требует авторизации. Модераторы видят все уроки, обычные пользователи - только свои
- **create** - доступен только авторизованным пользователям, которые не входят в группу модераторов. Создатель автоматически назначается владельцем через `perform_create()`

**LessonRetrieveAPIView:**
- **retrieve** - доступен модератору или владельцу урока (`IsModer | IsOwner`)
- **update/partial_update** - доступен модератору или владельцу урока (`IsModer | IsOwner`)
- **destroy** - доступен только владельцу, который не является модератором (`~IsModer` и `IsOwner`)

## Ограничения для модераторов

Модераторы имеют следующие ограничения:
- Могут просматривать любые курсы и уроки
- Могут редактировать любые курсы и уроки
- **НЕ могут создавать** новые курсы и уроки
- **НЕ могут удалять** курсы и уроки

## Ограничения для обычных пользователей

Обычные пользователи (не модераторы):
- Могут просматривать только свои курсы и уроки
- Могут редактировать только свои курсы и уроки
- Могут удалять только свои курсы и уроки
- Могут создавать новые курсы и уроки (автоматически становятся владельцами)

## Управление группами

Группы назначаются пользователям через административную панель Django (`/admin/`).

Для загрузки группы модераторов в базу данных используйте фикстуру:
```
poetry run python manage.py loaddata users/fixtures/groups.json
```

# Используемые возможности Django и DRF

В проекте используются:

* Django REST Framework;
* JWT-авторизация через `rest_framework_simplejwt`;
* документация OpenAPI через `drf-spectacular`;
* Swagger UI и ReDoc;
* создание платежных сессий через Stripe Checkout;
* сервисные функции для взаимодействия со Stripe API;
* ViewSets (`ModelViewSet`, `GenericViewSet`) и mixins для CRUD пользователей;
* Generic Views (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`, `ListAPIView`, `CreateAPIView`);
* Routers для автоматической генерации URL;
* Django ORM;
* миграции;
* административная панель;
* работа с PostgreSQL;
* работа с изображениями (`ImageField`);
* загрузка медиафайлов;
* Django Authentication System;
* создание собственной модели пользователя через `AbstractUser`;
* настройка кастомного поля авторизации (`USERNAME_FIELD`);
* `SerializerMethodField` для вычисляемых полей в сериализаторах;
* вложенные сериализаторы для связанных моделей;
* ручное описание операций через `extend_schema`;
* отдельные сериализаторы запроса и ответа для документации;
* фильтрация через `DjangoFilterBackend`;
* сортировка через `OrderingFilter`;
* кастомные management-команды для заполнения данными;
* кастомные классы разрешений (`BasePermission`);
* метод `get_permissions()` для динамического управления правами в ViewSets;
* метод `perform_create()` для автоматической привязки объектов к пользователям;
* логические операторы для комбинирования разрешений (`&`, `|`, `~`);
* система групп Django для разграничения прав доступа;
* фикстуры для загрузки начальных данных (группы пользователей);
* фоновые задачи через Celery;
* Redis как брокер сообщений и backend результатов;
* периодические задачи через `django-celery-beat`;
* декоратор `shared_task` для регистрации задач;
* отправка писем через SMTP Яндекса;
* массовое обновление пользователей через Django QuerySet;
* синхронизация часовых поясов Django и Celery.

---

# Контакты

Email: **spasov2000@mail.ru**
