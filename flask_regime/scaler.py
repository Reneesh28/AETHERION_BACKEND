import joblib
from sklearn.preprocessing import StandardScaler


class FeatureScaler:

    def __init__(self):
        self.scaler = StandardScaler()

    def fit_transform(self, X):
        return self.scaler.fit_transform(X)

    def transform(self, X):
        return self.scaler.transform(X)

    def save(self, path):
        joblib.dump(self.scaler, path)

    def load(self, path):
        self.scaler = joblib.load(path)