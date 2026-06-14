import pytest
from app.api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'model_v1_loaded' in data
    assert 'model_v2_loaded' in data

def test_predict_no_data(client):
    response = client.post('/predict', json={})
    # Если модель не обучена/не загружена, мы ожидаем 503. 
    # Если обучена, но отправлены пустые данные, мы ожидаем 400.
    assert response.status_code in [400, 503]

def test_predict_valid_data(client):
    valid_payload = {
        "LIMIT_BAL": 20000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 24,
        "PAY_0": 2, "PAY_2": 2, "PAY_3": -1, "PAY_4": -1, "PAY_5": -2, "PAY_6": -2,
        "BILL_AMT1": 3913, "BILL_AMT2": 3102, "BILL_AMT3": 689, "BILL_AMT4": 0,
        "BILL_AMT5": 0, "BILL_AMT6": 0, "PAY_AMT1": 0, "PAY_AMT2": 689,
        "PAY_AMT3": 0, "PAY_AMT4": 0, "PAY_AMT5": 0, "PAY_AMT6": 0
    }
    
    import json
    response = client.post('/predict', data=json.dumps(valid_payload), content_type='application/json')
    
    if response.status_code == 503:
        pytest.skip("Модели не обучены/не загружены, пропускаем тест предсказания.")
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'prediction' in data
    assert 'probability' in data
    assert 'model_version' in data
    assert data['model_version'] in ['v1', 'v2']