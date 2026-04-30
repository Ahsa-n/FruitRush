import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

def train_and_export_model(dataset_path="data/dataset.csv", model_path="data/model.pkl"):
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Run dataset_generator.py first.")
        return

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} samples.")
    
    X = df[['obstacle_density', 'euclidean_distance', 'turning_points']]
    y = df['complexity']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Decision Tree Classifier
    dt_classifier = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt_classifier.fit(X_train_scaled, y_train)
    
    y_pred = dt_classifier.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Decision Tree Accuracy: {acc * 100:.2f}%")
    
    if acc < 0.8:
        print("Warning: Accuracy is below 80%. Consider increasing dataset size or tuning parameters.")
    
    # Save the model and scaler
    model_data = {
        'model': dt_classifier,
        'scaler': scaler
    }
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model_data, model_path)
    print(f"Model and scaler saved to {model_path}.")

if __name__ == "__main__":
    train_and_export_model()