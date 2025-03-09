# Инструкция по развертыванию JSON Validator

В этом документе описаны различные способы развертывания приложения JSON Validator для доступа из интернета.

## Содержание
1. [Развертывание на VPS/выделенном сервере](#развертывание-на-vpsвыделенном-сервере)
2. [Развертывание с использованием Docker](#развертывание-с-использованием-docker)
3. [Временное решение с использованием ngrok](#временное-решение-с-использованием-ngrok)
4. [Развертывание на облачных платформах](#развертывание-на-облачных-платформах)

## Развертывание на VPS/выделенном сервере

### Предварительные требования
- VPS или выделенный сервер с Ubuntu 20.04/22.04
- Доменное имя (опционально)
- Базовые знания Linux и командной строки

### Шаг 1: Подготовка сервера
```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите необходимые пакеты
sudo apt install -y python3-pip python3-venv nginx curl

# Создайте пользователя для приложения (опционально)
sudo useradd -m -s /bin/bash jsonapp
sudo su - jsonapp
```

### Шаг 2: Клонирование репозитория и настройка окружения
```bash
# Клонируйте репозиторий или загрузите файлы
git clone https://github.com/ваш-репозиторий/JSON-Course.git
# или загрузите файлы через SFTP/SCP

cd JSON-Course

# Создайте виртуальное окружение и установите зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 3: Настройка Gunicorn как службы systemd
```bash
# Отредактируйте файл jsonvalidator.service, указав правильные пути
sudo nano jsonvalidator.service

# Скопируйте файл в директорию systemd
sudo cp jsonvalidator.service /etc/systemd/system/

# Активируйте и запустите службу
sudo systemctl daemon-reload
sudo systemctl enable jsonvalidator
sudo systemctl start jsonvalidator
sudo systemctl status jsonvalidator
```

### Шаг 4: Настройка Nginx как прокси-сервера
```bash
# Отредактируйте файл nginx.conf, указав ваш домен или IP-адрес
sudo nano nginx.conf

# Скопируйте файл в директорию Nginx
sudo cp nginx.conf /etc/nginx/sites-available/jsonvalidator

# Создайте символическую ссылку
sudo ln -s /etc/nginx/sites-available/jsonvalidator /etc/nginx/sites-enabled/

# Проверьте конфигурацию и перезапустите Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 5: Настройка брандмауэра
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Шаг 6: Настройка SSL (опционально, но рекомендуется)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.ru
```

## Развертывание с использованием Docker

### Предварительные требования
- Установленные Docker и Docker Compose
- Доменное имя (опционально)

### Шаг 1: Подготовка проекта
```bash
# Клонируйте репозиторий или загрузите файлы
git clone https://github.com/ваш-репозиторий/JSON-Course.git
cd JSON-Course
```

### Шаг 2: Запуск с помощью Docker Compose
```bash
# Запустите приложение
docker-compose up -d

# Проверьте статус
docker-compose ps
```

### Шаг 3: Настройка Nginx как прокси-сервера (опционально)
Если вы хотите использовать Nginx перед Docker-контейнером:

```bash
# Отредактируйте файл nginx.conf, изменив proxy_pass на http://localhost:8000
sudo nano nginx.conf

# Установите и настройте Nginx
sudo apt install -y nginx
sudo cp nginx.conf /etc/nginx/sites-available/jsonvalidator
sudo ln -s /etc/nginx/sites-available/jsonvalidator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Временное решение с использованием ngrok

### Предварительные требования
- Установленный Python и зависимости проекта
- Аккаунт на ngrok.com

### Шаг 1: Запуск приложения локально
```bash
cd JSON-Course
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Шаг 2: Установка и запуск ngrok
```bash
# Установите ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
./ngrok config add-authtoken YOUR_AUTH_TOKEN

# Запустите ngrok
./ngrok http 8000
```

Ngrok предоставит вам публичный URL, который будет перенаправлять трафик на ваш локальный сервер.

## Развертывание на облачных платформах

### Heroku

1. Создайте аккаунт на [Heroku](https://heroku.com)
2. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Выполните следующие команды:
   ```bash
   heroku login
   heroku create json-validator-app
   git push heroku main
   ```

### Render

1. Создайте аккаунт на [Render](https://render.com)
2. Создайте новый Web Service
3. Подключите ваш GitHub репозиторий
4. Настройте:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -k uvicorn.workers.UvicornWorker main:app`

### Railway

1. Создайте аккаунт на [Railway](https://railway.app)
2. Создайте новый проект из GitHub репозитория
3. Настройте переменные окружения и команду запуска

## Рекомендации по безопасности

1. **Всегда используйте HTTPS** - настройте SSL-сертификат с помощью Let's Encrypt
2. **Ограничьте доступ** - если нужно, добавьте базовую аутентификацию
3. **Регулярно обновляйте зависимости** - следите за обновлениями безопасности
4. **Настройте резервное копирование** - особенно для файлов в папке reference_json
5. **Мониторинг** - настройте мониторинг доступности и производительности

## Дополнительные рекомендации

1. Если вы планируете активное использование, рассмотрите возможность добавления кэширования
2. Для более высокой нагрузки рассмотрите использование балансировщика нагрузки
3. Добавьте логирование для отслеживания ошибок и использования
4. Настройте автоматическое обновление из репозитория при внесении изменений 