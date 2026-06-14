# Сервис прогнозирования дефолта по кредитным картам

## Описание проекта
Production-ready ML-сервис для прогнозирования вероятности дефолта клиента по кредитной карте в следующем месяце. Проект охватывает полный цикл внедрения ML-модели: от обучения до контейнеризации и A/B-тестирования.

**Домен:** Финансы / Кредитный скоринг  
**Датасет:** Default of Credit Card Clients Dataset (UCI ML Repository)  
**Модели:** Random Forest (v1) и Logistic Regression (v2) для A/B-тестирования

## Структура репозитория
```
credit-default-ml/
├── src/
│   └── app/
│       ├── __init__.py
│       └── api.py                 # Flask веб-сервис с эндпоинтами /predict и /health
├── models/
│   ├── train_model.py             # Скрипт обучения моделей
│   ├── model_v1.joblib            # Обученная модель Random Forest
│   └── model_v2.joblib            # Обученная модель Logistic Regression
├── data/
│   └── UCI_Credit_Card.csv        # Исходный датасет
├── tests/
│   └── test_api.py                # Тесты API
├── Dockerfile                     # Контейнеризация
├── docker-compose.yml             # Оркестрация с мониторингом
├── requirements.txt               # Зависимости Python
├── .gitignore
├── ARCHITECTURE.md                # Архитектурные решения и MLOps концепты
└── AB_TEST_PLAN.md                # План A/B-тестирования
```
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
   
## Примеры запросов к API
## Health check (проверка работоспособности)

**Запрос:**
   ```bash
   curl http://localhost:5000/health
   ```
**Ответ**
```json
{
  "status": "healthy",
  "model_v1_loaded": true,
  "model_v2_loaded": true
} 
```
## Получение прогноза

**Запрос:**
   ```bash
   curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @test_request.json
   ```
**Пример данных (test_request.json):**
```json
{
  "LIMIT_BAL": 20000,
  "SEX": 2,
  "EDUCATION": 2,
  "MARRIAGE": 1,
  "AGE": 24,
  "PAY_0": 2,
  "PAY_2": 2,
  "PAY_3": -1,
  "PAY_4": -1,
  "PAY_5": -2,
  "PAY_6": -2,
  "BILL_AMT1": 3913,
  "BILL_AMT2": 3102,
  "BILL_AMT3": 689,
  "BILL_AMT4": 0,
  "BILL_AMT5": 0,
  "BILL_AMT6": 0,
  "PAY_AMT1": 0,
  "PAY_AMT2": 689,
  "PAY_AMT3": 0,
  "PAY_AMT4": 0,
  "PAY_AMT5": 0,
  "PAY_AMT6": 0
}
```
**Ответ**
```json
{
  "prediction": 0,
  "probability": 0.05,
  "model_version": "v1"
}
```
**Поля ответа:**
- `prediction`: 0 (не дефолт) или 1 (дефолт)
- `probability`: вероятность дефолта от 0 до 1
- `model_version`: версия модели (v1 или v2), выбрана случайно для A/B-теста

## Docker Hub

- Образ собран локально и протестирован. Для загрузки в Docker Hub требуется авторизация. В моем случае произошла ошибка:

<img width="1319" height="1038" alt="авторизация docker - неудачно" src="https://github.com/user-attachments/assets/ce5fe7e5-36d2-46c0-a55e-0c63c31cedd1" />


**Команды для загрузки:**
```bash
docker login
docker tag credit-default-ml:v1 YOUR_USERNAME/credit-default-ml:v1
docker push YOUR_USERNAME/credit-default-ml:v1
```

## A/B-тестирование

Сервис реализует A/B-тестирование двух моделей:
- **v1**: Random Forest Classifier
- **v2**: Logistic Regression
Подробный план A/B-теста: **AB_TEST_PLAN.md**

## Архитектура и MLOps

Подробное описание архитектурных решений, концептов MLOps (DVC, MLflow, RabbitMQ, ELK) и бизнес-метрик: **ARCHITECTURE.md**

### Бизнес-метрики
1. **Снижение ожидаемых финансовых потерь (Expected Loss Reduction):**
   - Рассчитывается как разница между суммой выданных кредитов без дефолта и с дефолтом
   - Модель должна максимизировать эту разницу
2. **Approval Rate при фиксированном уровне риска:**
   - Доля одобренных заявок при условии, что Precision не падает ниже заданного порога (например, 85%)

### Дополнительная информация

***ONNX-ML конвертация***
- Модель может быть конвертирована в формат ONNX с помощью библиотеки skl2onnx для оптимизации инференса и кроссплатформенности.

***uWSGI + NGINX***
- В production-среде Gunicorn/Flask располагается за обратным прокси (NGINX) для SSL-терминации и защиты от медленных атак, а uWSGI/Gunicorn управляет пулом воркеров Python.
