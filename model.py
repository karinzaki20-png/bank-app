from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier


MODEL_PATH = Path(__file__).resolve().parent / "bank_model.joblib"

# Features:
# transaction_amount
# transaction_count
# account_age_days

X = [
    [100, 2, 500],
    [200, 3, 800],
    [500, 5, 1000],
    [1000, 10, 1500],
    [5000, 30, 2000],
    [10000, 50, 100],
    [15000, 60, 50],
    [20000, 80, 30],
]

# 0 = normal
# 1 = suspicious
y = [0, 0, 0, 0, 0, 1, 1, 1]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

joblib.dump(model, MODEL_PATH)

print(f"Model created successfully at {MODEL_PATH}")
