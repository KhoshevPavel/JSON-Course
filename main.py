import json
import os
import secrets
import hashlib
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="JSON Validator")

# Создаем папки, если они не существуют
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("reference_json", exist_ok=True)

# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Функция для сравнения JSON файлов
def compare_json_files(user_json: Dict[str, Any], reference_json: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "identical": user_json == reference_json,
        "differences": [],
        "recommendations": [],
        "secret_code": None
    }
    
    # Если файлы идентичны, генерируем секретный код
    if result["identical"]:
        # Создаем секретный код на основе содержимого файла
        json_str = json.dumps(reference_json, sort_keys=True)
        hash_obj = hashlib.sha256(json_str.encode())
        # Берем первые 8 символов хеша для секретного кода
        result["secret_code"] = hash_obj.hexdigest()[:8].upper()
        return result
    
    # Проверяем различия в структуре
    def find_differences(user_obj, ref_obj, path=""):
        if isinstance(ref_obj, dict) and isinstance(user_obj, dict):
            # Проверяем отсутствующие ключи
            for key in ref_obj:
                new_path = f"{path}.{key}" if path else key
                if key not in user_obj:
                    result["differences"].append(f"Отсутствует ключ: {new_path}")
                    result["recommendations"].append(f"Добавьте ключ '{key}' в ваш JSON")
                else:
                    find_differences(user_obj[key], ref_obj[key], new_path)
            
            # Проверяем лишние ключи
            for key in user_obj:
                new_path = f"{path}.{key}" if path else key
                if key not in ref_obj:
                    result["differences"].append(f"Лишний ключ: {new_path}")
                    result["recommendations"].append(f"Удалите ключ '{key}' из вашего JSON")
        
        elif isinstance(ref_obj, list) and isinstance(user_obj, list):
            if len(ref_obj) != len(user_obj):
                result["differences"].append(f"Разное количество элементов в массиве {path}: ожидается {len(ref_obj)}, получено {len(user_obj)}")
                result["recommendations"].append(f"Массив {path} должен содержать {len(ref_obj)} элементов")
            
            # Сравниваем элементы массивов
            for i in range(min(len(ref_obj), len(user_obj))):
                find_differences(user_obj[i], ref_obj[i], f"{path}[{i}]")
        
        elif user_obj != ref_obj:
            result["differences"].append(f"Разные значения для {path}: ожидается {ref_obj}, получено {user_obj}")
            result["recommendations"].append(f"Измените значение {path} на {ref_obj}")
    
    find_differences(user_json, reference_json)
    return result

# Получение списка доступных эталонных JSON файлов
def get_reference_files() -> List[str]:
    if not os.path.exists("reference_json"):
        return []
    return [f for f in os.listdir("reference_json") if f.endswith(".json")]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    reference_files = get_reference_files()
    return templates.TemplateResponse("index.html", {"request": request, "reference_files": reference_files})

@app.post("/validate", response_class=HTMLResponse)
async def validate_json(
    request: Request,
    user_file: UploadFile = File(...),
    reference_file: str = Form(...)
):
    # Проверяем, что загруженный файл - JSON
    if not user_file.filename.endswith(".json"):
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request, 
                "error": "Загруженный файл должен быть в формате JSON"
            }
        )
    
    # Проверяем, что эталонный файл существует
    reference_path = os.path.join("reference_json", reference_file)
    if not os.path.exists(reference_path):
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request, 
                "error": "Выбранный эталонный файл не существует"
            }
        )
    
    try:
        # Читаем пользовательский JSON
        user_content = await user_file.read()
        user_json = json.loads(user_content)
        
        # Читаем эталонный JSON
        with open(reference_path, "r", encoding="utf-8") as f:
            reference_json = json.load(f)
        
        # Сравниваем файлы
        result = compare_json_files(user_json, reference_json)
        
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request,
                "result": result,
                "user_json": json.dumps(user_json, indent=2, ensure_ascii=False),
                "reference_json": json.dumps(reference_json, indent=2, ensure_ascii=False),
                "filename": user_file.filename,
                "reference_filename": reference_file
            }
        )
    
    except json.JSONDecodeError:
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request, 
                "error": "Ошибка при разборе JSON файла. Проверьте синтаксис вашего файла."
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "result.html", 
            {
                "request": request, 
                "error": f"Произошла ошибка: {str(e)}"
            }
        )

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    reference_files = get_reference_files()
    return templates.TemplateResponse("admin.html", {"request": request, "reference_files": reference_files})

@app.post("/upload-reference")
async def upload_reference(
    reference_file: UploadFile = File(...),
    file_name: str = Form(...)
):
    if not reference_file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате JSON")
    
    try:
        # Проверяем, что загруженный файл - валидный JSON
        content = await reference_file.read()
        json.loads(content)
        
        # Сохраняем файл
        file_path = os.path.join("reference_json", file_name)
        if not file_name.endswith(".json"):
            file_path += ".json"
            
        with open(file_path, "wb") as f:
            f.write(content)
            
        return {"success": True, "message": f"Файл {file_name} успешно загружен"}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Ошибка при разборе JSON файла")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
