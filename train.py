import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib

def train_model():
    print("Training SVM Model...")
    # Load data
    try:
        df = pd.read_csv('smart data.csv')
    except FileNotFoundError:
        print("Error: 'smart data.csv' not found.")
        return

    X = df.drop('Depression_risk', axis=1)
    y = df['Depression_risk']

    # Train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    svm_model = SVC(kernel='rbf', probability=True, random_state=42)
    svm_model.fit(X_train, y_train)

    # Save
    joblib.dump(svm_model, 'svm_model.pkl')
    print("Model saved as 'svm_model.pkl'!")

if __name__ == "__main__":
    train_model()