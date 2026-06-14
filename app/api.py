from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
import random
import logging
import json
from datetime import datetime

app = Flask(__name__)

# Настройка логирования для вывода в формате JSON
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('API_Logger')

# Определение путей
MODEL_V1_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model_v1.joblib')
MODEL_V2_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model_v2.joblib')

# Попытка загрузить модели при запуске
try:
    model_v1 = joblib.load(MODEL_V1_PATH)
except FileNotFoundError:
    model_v1 = None
    print(f"Предупреждение: Модель v1 не найдена по пути {MODEL_V1_PATH}.")

try:
    model_v2 = joblib.load(MODEL_V2_PATH)
except FileNotFoundError:
    model_v2 = None
    print(f"Предупреждение: Модель v2 не найдена по пути {MODEL_V2_PATH}.")

@app.route('/health', methods=['GET'])
def health():
    """Эндпоинт проверки работоспособности, требуемый в задании"""
    return jsonify({
        'status': 'healthy', 
        'model_v1_loaded': model_v1 is not None,
        'model_v2_loaded': model_v2 is not None
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Эндпоинт предсказания для оценки дефолта по кредитной карте"""
    available_models = []
    if model_v1 is not None: available_models.append(('v1', model_v1))
    if model_v2 is not None: available_models.append(('v2', model_v2))

    if not available_models:
        return jsonify({'error': 'Модели не загружены. Пожалуйста, сначала обучите модели.'}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Входные данные не предоставлены'}), 400

        # Преобразование простого JSON-словаря в Pandas DataFrame
        if isinstance(data, dict):
            # Предполагается входной формат: {"LIMIT_BAL": 20000, "SEX": 2, ...}
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)

        # A/B тестирование: Случайный выбор модели из доступных
        selected_model_name, selected_model = random.choice(available_models)

        # Генерация предсказаний
        prediction = selected_model.predict(df)
        probability = selected_model.predict_proba(df)[:, 1]

        # Логирование предсказания в формате JSON
        from datetime import timezone
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event': 'prediction_request',
            'model_version': selected_model_name,
            'prediction': int(prediction[0]),
            'probability': float(probability[0])
        }
        logger.info(json.dumps(log_data))

        return jsonify({
            'prediction': int(prediction[0]),
            'probability': float(probability[0]),
            'model_version': selected_model_name
        })
    except Exception as e:
        from datetime import timezone
        logger.error(json.dumps({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event': 'prediction_error',
            'error_message': str(e)
        }))
        return jsonify({'error': f'Произошла ошибка при обработке запроса: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)