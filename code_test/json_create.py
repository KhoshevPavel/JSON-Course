import json
from datetime import datetime, timedelta
import random

# Списки для генерации данных
titles = [
    "-Fix bug in", "*Update", "/Refactor", ".Add new", "0Test", "9Deploy", "*Review", "&Optimize", "&Document"
]
descriptions = [
    "!the authentication module", "@user profile page", "#payment processing", "$database queries", 
    "%API endpoints", "^frontend UI", "&backend logic", "`security features"
]
statuses = ["+++completed", "++in_progress", "++pending"]
priorities = ["---low", "--medium", "-high"]

# Генерация 150 объектов
tasks = []
for i in range(1, 151):
    created_at = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
    updated_at = created_at + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None
    
    task = {
        "id": i,
        "title": f"{random.choice(titles)} {random.choice(descriptions)}",
        "description": f"Task to {random.choice(titles).lower()} {random.choice(descriptions)}",
        "status": random.choice(statuses),
        "priority": random.choice(priorities),
        "created_at": created_at.isoformat() + "Z",
        "updated_at": updated_at.isoformat() + "Z" if updated_at else None
    }
    tasks.append(task)

# Сохранение в файл
with open("tasks.json", "w", encoding="utf-8") as f:
    json.dump(tasks, f, indent=4)

print("JSON с 150 объектами сгенерирован и сохранен в 'tasks.json'")
