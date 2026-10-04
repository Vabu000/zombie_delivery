# Zombie Night Delivery Aggregator

Система динамічної маршрутизації для нічного полювання.

## Запуск Sandbox (Тестове середовище)
1. Встановіть залежності: `pip install -r requirements.txt`
2. Запуск:
   ```bash
   export ENV=sandbox   # Для Windows PowerShell: $env:ENV="sandbox"
   uvicorn src.main:app --reload