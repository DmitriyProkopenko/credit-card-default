import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os

# Конфигурация
# Определение пути к датасету в зависимости от структуры вашего рабочего пространства
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'UCI_Credit_Card.csv')
MODEL_DIR = os.path.dirname(__file__)
MODEL_V1_PATH = os.path.join(MODEL_DIR, 'model_v1.joblib')
MODEL_V2_PATH = os.path.join(MODEL_DIR, 'model_v2.joblib')

def train():
    if not os.path.exists(DATA_PATH):
        print(f"Ошибка: Датасет не найден по пути {DATA_PATH}")
        return

    print("Загрузка датасета...")
    df = pd.read_csv(DATA_PATH)
    
    # Предобработка
    # В датасете обычно есть столбец ID. его следует удалить из признаков
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])
    
    # Проверка целевого столбца
    target_col = 'default.payment.next.month'
    if target_col not in df.columns:
        print(f"Ошибка: Целевой столбец '{target_col}' не найден.")
        return

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Разделение датасета
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    # Обучение модели V1 (Случайный лес)
    print("Обучение пайплайна модели Случайного леса (v1)...")
    pipeline_v1 = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    pipeline_v1.fit(X_train, y_train)
    score_v1 = pipeline_v1.score(X_test, y_test)
    print(f"Точность модели v1 (Случайный лес) на тестовой выборке: {score_v1:.4f}")
    
    joblib.dump(pipeline_v1, MODEL_V1_PATH)
    print(f"Модель v1 сохранена в {MODEL_V1_PATH}")

    # Обучение модели V2 (Логистическая регрессия)
    print("Обучение пайплайна модели Логистической регрессии (v2)...")
    pipeline_v2 = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])

    pipeline_v2.fit(X_train, y_train)
    score_v2 = pipeline_v2.score(X_test, y_test)
    print(f"Точность модели v2 (Логистическая регрессия) на тестовой выборке: {score_v2:.4f}")
    
    joblib.dump(pipeline_v2, MODEL_V2_PATH)
    print(f"Модель v2 сохранена в {MODEL_V2_PATH}")

if __name__ == '__main__':
    train()