## Foodgram
https://foodie.hopto.org/ - это продуктовый помощник или блог для любителей готовить и вкусно поесть.
Здесь любой желающий может посмотреть рецепты интересных блюд, а зарегистрированные пользователи могут размещать свои рецепты и пользоваться полным функционалом платформы.
В репозитории представлен полностью рабочий код проекта, который загружен на удаленный сервер. Подключено автоматическое обновление проекта на сервере при внесении изменений.
Данные для авторизации в админке в файле **admin.txt** в папке `/infra`

Для тех, кто хочет расширить функционал проекта можно загрузить репозиторий к себе.
Для запуска локально

1. Cклонируйте репозиторий на свой компьютер, в командной строке введите:

```yaml
git clone git@github.com:terrazavr/foodgram-project-react.git
 ```
2. Создайте виртуальное окружение:
```yaml
python3 -m venv venv 
```
И активируйте его:
если у вас Linux/macOS:
```yaml
source venv/bin/activate
```
если у вас windows:

```yaml
source venv/scripts/activate
```

3. Для работы с контейнерами вам понадобится Docker, если он у вас еще не установлен: необходимо скачать его официального сайта `https://www.docker.com` для вашей операционной системы. После установки рекомендую сразу создать учетную запись DockerHub, чтобы иметь возможность собирать образы и хранить их удаленно.

4. Разверните контейнеры Docker:
```yaml
# Перейдите в папку проекта
cd ~/infra
# Собирите орекстр контейнеров командой
sudo docker compose -f docker-compose.yml up -d
# Если вы видите контейнеры со статусом  "Started"  - проект запущен локально 
# Далее необходимо сделать миграции. Посмотрите имя backend контейнера
docker ps | grep backend
# Выполните команду:
docker exec -it infra-backend-1 bash - infra-backend-1  # имя контейнера, может отличаться
# Выполните миграции: 
./manage.py migrate
# Создайте суперюзера: 
./manage.py createsuperuser
# Соберите статику: 
./manage.py collectstatic
```
Теперь можете заходить на сайт: `http://127.0.0.1:7000/`
Панель админитсратора находится здесь: `http://127.0.0.1:7000/admin/`
С документацией проекта можете ознакомиться по адресу: `http://127.0.0.1:7000/api/docs/redoc.html`

### Чтобы вы могли поноценно пользоваться проектом необхимо выполнить следующие операций:
##### 1. Загрузите базу ингридентов:
- в админ панели зайдите в раздел `"Ингридиенты"`
- нажмите кнопку `"import"`
- загрузите файл `ingredients.json` из папки проекта `"/data"`
- подтвердите загрузку
##### 2. Создайте несколько тегов:
- в админ панели зайдите в раздел `"Теги"`
- нажмите кнопку `"add"`
- заполните все поля и сохраните

Проект готов, теперь, зайдя на сайт, вы можете создавать рецепты.
##### Эндроинты сервиса

```yaml
POST /api/users/ - регистрация
POST /api/auth/token/login - создание токена
POST /api/auth/token/logout/ - удаление токена
GET /api/users/ - просмотр информации о пользователях

POST /api/users/set_password/ - изменение пароля
GET /api/users/{id}/subscribe/ - подписаться на пользователя
DEL /api/users/{id}/subscribe/ - отписаться от пользователя

POST /api/recipes/ - создать рецепт
GET /api/recipes/ - получить рецепты
GET /api/recipes/{id}/ - получить рецепт по id
DEL /api/recipes/{id}/ - удалить рецепт по id

GET /api/recipes/{id}/favorite/ - добавить рецепт в избранное
DEL /api/recipes/{id}/favorite/ - удалить рецепт из избранного

GET /api/users/{id}/subscribe/ - подписаться на пользователя
DEL /api/users/{id}/subscribe/ - отписаться от пользователя

GET /api/ingredients/ - получить список всех ингредиентов

GET /api/tags/ - получить список всех тегов

GET /api/recipes/{id}/shopping_cart/ - добавить рецепт в корзину
DEL /api/recipes/{id}/shopping_cart/ - удалить рецепт из корзины
```

## Загрузка проекта на удаленный сервер

Перед загрузкой на удаленный сервер нужно внести некоторые изменения:
1. Создайте файл `.env` 
```yaml
DEBUG=True
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram
POSTGRES_DB=foodgram
DB_HOST=db
DB_PORT=5432
```

В файле `backend/foodgram/settings.py` внесте изменения в поле `ALLOWED_HOSTS = ["158.160.74.8", "127.0.0.1", "localhost", "foodie.hopto.org"]`, укажите IP адрес своего сервера и доменнное имя.

Соберите свои собственные docker - образы backend, frontend, nginx:
```yaml
cd frontend  # В директории frontend...
docker build -t username/foodgram_frontend .  # ...сбилдите образ, назвите его foodgram_frontend
cd ../backend  # То же в директории backend...
docker build -t username/foodgram_backend .
cd ../gateway  # ...то же и в gateway
docker build -t username/foodgram_gateway . 
# и отправьте каждый из их на DockerHub:
docker push username/<image_name> # foodgram_frontend 
```

Внестите изменения в файле `infra/docker-compose.production` в разделы backend, frontend, nginx:
вместо команды: `build: ./backend` укажите откуда загрузить образы: image: `username/foodgram_backend:latest`

На удаленном сервере создайте папку проекта, в которой поместите 2 файла:
- .env
- docker-compose.production.yml

Настройте "внешний" nginx тут: `sudo nano /etc/nginx/sites-enabled/default`
Внеситет данные своего домена, а так же укажите свой порт, куда будете перенаправлять запросы:
```yaml
server {
    server_name my_domain.org;
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:7000;
    }
}
```

Теперь можете запустить сборку оркестра:
```yaml
sudo docker compose -f docker-compose.production.yml up -d
# провести миграции:
docker exec -it infra-backend-1 bash - infra-backend-1  # имя контейнера, может отличаться
./manage.py migrate
# создать суперюзера 
./manage.py createsuperuser
#собрать статику: 
./manage.py collectstatic
```

Если все контейнеры запутились успешно и nginx настроен правильно ваш сайт успешно запустится!
Повторите шаги с загрузкой ингридиентов и созданием тегов для полноценной работы проекта.

### Автор проекта:
#### [Диляра Юнусова](https://github.com/terrazavr)