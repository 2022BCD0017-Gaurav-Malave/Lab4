import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import json
import os

def load_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    df = pd.read_csv(url, sep=';')
    return df

def train_model():
    print("Loading data...")
    df = load_data()
    
    X = df.drop('quality', axis=1)
    y = df['quality']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        random_state=42,
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  MSE: {mse:.4f}")
    print(f"  R2 Score: {r2:.4f}")
    
    # Create app/artifacts directory (as required by lab)
    os.makedirs('app/artifacts', exist_ok=True)
    
    # Save model to app/artifacts
    with open('app/artifacts/wine_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model saved to app/artifacts/wine_model.pkl")
    
    # Save metrics with 'accuracy' key (using r2_score as accuracy measure)
    # For regression, R2 score can be used as an accuracy metric
    metrics = {
        "accuracy": float(r2),  # Use r2_score as accuracy
        "mse": float(mse),
        "r2_score": float(r2)
    }
    
    # Save to app/artifacts/metrics.json (as required by lab)
    with open('app/artifacts/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print("Metrics saved to app/artifacts/metrics.json")
    
    return metrics

if __name__ == "__main__":
    metrics = train_model()
    print(f"\nFinal metrics: {metrics}")