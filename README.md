# NotiHub

```
ngrok http http://localhost:8888

docker build -t notihub_img .


docker run --name notihub_redis ^
    --network notihub_net ^ 
    -p 7379:6379 ^ 
    -d --rm redis


docker run --name notihub_postgres ^
    -p 6432:5432 ^
    -e POSTGRES_USER=notihub_admin ^
    -e POSTGRES_PASSWORD=qweasdzxc ^
    -e POSTGRES_DB=notihub_db ^
    --network=notihub_net ^
    --volume pg_notihub_db_data:/var/lib/postgresql/data ^
    -d --rm postgres:17


docker run --name notihub_nginx ^
    -p 80:80 ^
    --volume ./nginx.conf:/etc/nginx/nginx.conf ^
    --network=notihub_net ^
    -d --rm nginx


docker run --name notihub_api ^
    -p 8888:8888 ^
    --network notihub_net ^
    -d --rm notihub_img


docker run --name notihub_celery_beat ^
    -p 8888:8888 ^
    --network notihub_net ^
    -d --rm notihub_img ^
    poetry run celery --app=src.tasks.app:celery_app beat -l INFO


docker run --name notihub_celery_worker ^
    -p 8888:8888 ^
    --network notihub_net ^
    -d --rm notihub_img ^
    poetry run celery --app=src.tasks.app:celery_app worker -l INFO
```