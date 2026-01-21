from sklearn.ensemble import RandomForestClassifier
import joblib


class PatternClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=200)

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)
