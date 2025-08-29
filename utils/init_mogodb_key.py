from cryptography.fernet import Fernet
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Генерация ключа
key = Fernet.generate_key().decode()

# Проверка: если .env уже существует, не перезаписываем
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        lines = f.readlines()
    if any(line.startswith("MONGO_CONFIG_KEY=") for line in lines):
        print("⚠️  Ключ уже существует в .env, новый не создавался")
        exit(0)

# Запись ключа в .env
with open(ENV_FILE, "a") as f:
    f.write(f"\nMONGO_CONFIG_KEY={key}\n")

print(f"✅ Сгенерирован и сохранён ключ в {ENV_FILE}")
print(f"🔑 Ключ: {key}")
