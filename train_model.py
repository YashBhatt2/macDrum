import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib


df = pd.read_csv("drum_data.csv")
X = df.iloc[:, :-1].astype(float)
Y = df.iloc[:, -1]

print(f"Features shape: {X.shape}") # Should be (number_of_slaps, 120)
print(f"Labels shape: {Y.shape}")

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

print("Model training.......")
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

print("Evaluating model...")
predictions = clf.predict(X_test)
print(classification_report(y_test, predictions))

joblib.dump(clf, 'drum_model.pkl')
print("\n Model saved as 'drum_model.pkl'. You are ready to play!")