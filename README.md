# Сервис прогнозирования дефолта по кредитным картам

## Описание проекта
Production-ready ML-сервис для прогнозирования вероятности дефолта клиента по кредитной карте в следующем месяце. Проект охватывает полный цикл внедрения ML-модели: от обучения до контейнеризации и A/B-тестирования.

**Домен:** Финансы / Кредитный скоринг  
**Датасет:** Default of Credit Card Clients Dataset (UCI ML Repository)  
**Модели:** Random Forest (v1) и Logistic Regression (v2) для A/B-тестирования

## Структура репозитория
credit-default-ml/
├── src/
│ └── app/
│ ├── init.py
│ └── api.py # Flask веб-сервис с эндпоинтами /predict и /health
── models/
│ ├── train_model.py # Скрипт обучения моделей
│ ├── model_v1.joblib # Обученная модель Random Forest
│ └── model_v2.joblib # Обученная модель Logistic Regression
├── data/
│ └── UCI_Credit_Card.csv # Исходный датасет
├── tests/
│ └── test_api.py # Тесты API
├── notebooks/ # Jupyter notebooks (для EDA)
── Dockerfile # Контейнеризация
├── docker-compose.yml # Оркестрация с мониторингом
├── requirements.txt # Зависимости Python
├── .gitignore
├── ARCHITECTURE.md # Архитектурные решения и MLOps концепты
└── AB_TEST_PLAN.md # План A/B-тестирования

**Примечание:** Структура адаптирована под требования задания. Папка `src/app/` содержит веб-сервис, что соответствует модульной организации кода.

## Инструкция по запуску

### Локальный запуск (Python venv)

1. **Создать виртуальное окружение:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   
2. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt 

3. **Обучить модели:**
   ```bash
   python models/train_model.py

Скрипт обучит две модели (Random Forest v1 и Logistic Regression v2) и сохранит их в папке models/.

4. **Запустить сервис:**
   ```bash
   python src/app/api.py

   Сервис запустится на порту 5000.

### Docker

1. **Сборка образа:**
   ```bash
   docker build -t credit-default-ml:v1 .
   
2. **Запуск контейнера:**
   ```bash
   docker run -p 5000:5000 --name ml-service credit-default-ml:v1
   
3. **Или через Docker Compose (с мониторингом):**
   ```bash

## Примеры запросов к API
## Health check (проверка работоспособности)

**Запрос:**
   ```bash
   curl http://localhost:5000/health

**Ответ**
   ```json
   {
  "status": "healthy",
  "model_v1_loaded": true,
  "model_v2_loaded": true
   }
