FROM python:3.9-slim

WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Создаем необходимые директории, если они не существуют
RUN mkdir -p static templates reference_json

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение с помощью Gunicorn и Uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"] 