
#### `ARCHITECTURE.md`

# Архитектура сервиса и MLOps концепты

## 1. Архитектура сервиса: Монолит vs Микросервисы

### Выбранный подход: Монолит

Для данного учебного проекта выбран **монолитный подход** к архитектуре веб-сервиса.

### Обоснование:

**Преимущества монолита для данного кейса:**
1. **Простота разработки и деплоя:** Один Docker-образ, один сервис, одна точка входа
2. **Низкая сложность:** Сервис выполняет одну задачу — скоринг кредитных заявок
3. **Быстрый старт:** Не требуется настройка service discovery, API gateway, распределённого трейсинга
4. **Учебный контекст:** Фокус на ML-инженерии, а не на распределённых системах

**Когда переходить на микросервисы:**
- При росте нагрузки до тысяч RPS
- При необходимости независимого масштабирования компонентов (Feature Store, Model Serving, Monitoring)
- При добавлении сложных пайплайнов (реал-тайм фичи, онлайн-обучение)
- При команде из 10+ разработчиков

**Архитектура текущего решения:**
```
┌─────────────────────────────────────┐
│ ML Service (Monolith) │
│ ┌─────────────────────────────┐ │
│ │ Flask API (Gunicorn) │ │
│ │ - /health │ │
│ │ - /predict (A/B routing) │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Model Loader (joblib) │ │
│ │ - model_v1.joblib │ │
│ │ - model_v2.joblib │ │
│ ─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ JSON Logger │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────────┘
```
---

## 2. Брокеры сообщений (RabbitMQ)

### Концепт использования в production

В гипотетическом сценарии масштабирования **RabbitMQ** может использоваться для:

#### 2.1. Асинхронная обработка батч-предсказаний

**Сценарий:** Банк загружает CSV с 10,000 заявок на кредит.

**Архитектура:**
```
Client → API → RabbitMQ Queue → Worker Pool → Database
↓
Async Response (Job ID)
```
**Преимущества:**
- API не блокируется на время обработки
- Возможность масштабирования воркеров независимо от API
- Гарантированная доставка сообщений (persistent queues)
- Retry механизм при ошибках

#### 2.2. Надежное логирование и мониторинг

**Сценарий:** Все предсказания логируются для анализа дрейфа модели.

**Архитектура:**

```
API → RabbitMQ (logs queue) → Logstash → Elasticsearch → Kibana
```

**Преимущества:**
- Потеря логов исключена (persistent queues)
- API не замедляется из-за записи логов
- Возможность обработки пиковых нагрузок (buffering)

#### 2.3. Реализация (опционально)

Для реализации можно использовать библиотеку `pika`:
```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='predictions')

channel.basic_publish(
    exchange='',
    routing_key='predictions',
    body=json.dumps(prediction_data)
)
```
## 3. Логирование и мониторинг
- **Формат:** Логи API формируются в структурированном формате JSON (см. `src/app.py`).
- **Сбор в Production:** Используется стек **ELK** (Elasticsearch, Logstash, Kibana) или **Prometheus + Grafana** (для метрик вроде RPS, latency, error rate). JSON-логи парсятся Logstash и индексируются в Elasticsearch для быстрого поиска аномалий.

## 4. Инструменты MLOps
- **DVC (Data Version Control):** Используется для версионирования самого датасета `UCI_Credit_Card.csv` и файлов модели, привязывая их к конкретному коммиту в Git. Гарантирует воспроизводимость обучения.
```bash
# Версионирование датасета
dvc add data/UCI_Credit_Card.csv
git add data/UCI_Credit_Card.csv.dvc
git commit -m "Add dataset v1"

# Версионирование модели
dvc add models/model_v1.joblib
git add models/model_v1.joblib.dvc
git commit -m "Add model v1"
```

- **MLflow:** Применяется для трекинга экспериментов. При обучении фиксируются гиперпараметры (n_estimators), метрики (F1-score) и артефакт модели. Позволяет сравнить `model_v1` и `model_v2` и выбрать лучшую для деплоя.

## 5. Бизнес-метрики
Помимо F1-score, для банка критически важны:
1. **Снижение ожидаемых финансовых потерь (Expected Loss Reduction):** Рассчитывается как `(Сумма кредитов, выданных новым клиентам без дефолта) - (Сумма кредитов, выданных клиентам с дефолтом)`. Модель должна максимизировать эту разницу по сравнению со случайным одобрением или старой моделью.
2. **Approval Rate при фиксированном уровне риска:** Доля одобренных заявок, при условии, что Precision (точность предсказания дефолта) не падает ниже заданного бизнесом порога (например, 85%).

## 6. ONNX-ML конвертация
**Концепт оптимизации**
Модель может быть конвертирована в формат **ONNX-ML** для:
- Ускорения инференса (оптимизированные runtime)
- Кроссплатформенности (запуск на разных устройствах)
- Интеграции с различными фреймворками
**Конвертация:**
```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

initial_type = [('float_input', FloatTensorType([None, 23]))]
onx = convert_sklearn(pipeline_v1, initial_types=initial_type)

with open("model.onnx", "wb") as f:
    f.write(onx.SerializeToString())
```
**Инференс:**
```python
import onnxruntime as rt

sess = rt.InferenceSession("model.onnx")
pred = sess.run(None, {'float_input': input_data})
```

## 7. uWSGI + NGINX в production
**Архитектура production-деплоя**
```
Internet → NGINX (reverse proxy, SSL) → uWSGI/Gunicorn (app server) → Flask App
```
### NGINX (Reverse Proxy)
**Назначение:**
- `SSL/TLS терминация`: Расшифровка HTTPS трафика
- `Load Balancing`: Распределение нагрузки между инстансами
- `Static Files`: Отдача статических файлов без участия Python
- `Security`: Защита от DDoS, rate limiting, WAF
- `Caching`: Кэширование ответов для снижения нагрузки
- 
**Конфигурация:**
```nginx
server {
    listen 443 ssl;
    server_name api.bank.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## uWSGI/Gunicorn (Application Server)
**Назначение:**
- `Process Management`: Управление пулом воркеров Python
- `Concurrency`: Обработка множества запросов параллельно
- `Graceful Reload`: Перезагрузка без downtime
- `Resource Management`: Ограничение памяти и CPU

**Запуск Gunicorn:**
```basg
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 app.api:app
```
**Параметры:**
- `--workers 4`: 4 процесса (по числу CPU)
- `--threads 2`: 2 потока на процесс
- Итого: 8 одновременных запросов
- 
**Почему не используем в учебном проекте?**
1. `Избыточная сложность` Для учебного проекта достаточно Gunicorn
2. `Фокус на ML`: Акцент на моделировании, а не на инфраструктуре
3. `Docker изоляция`: Контейнер уже обеспечивает изоляцию

**В production обязательно**: NGINX + Gunicorn/uWSGI + Docker + Kubernetes
