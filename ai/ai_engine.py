import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.cluster import DBSCAN

# ---------------- NLP MODEL ----------------

training_data = [
("Garbage not collected", "Sanitation"),
("Waste dumping on road", "Sanitation"),
("Pothole in road", "Infrastructure"),
("Road badly damaged", "Infrastructure"),
("Water leakage", "Water"),
("No water supply", "Water"),
("Power outage", "Electricity"),
("Street light not working", "Electricity"),
("Robbery happened", "Police"),
("Fight in street", "Police")
]

texts = [t[0] for t in training_data]
labels = [t[1] for t in training_data]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

def predict_department(text):

    vec = vectorizer.transform([text])
    dept = model.predict(vec)[0]

    return dept


# ---------------- HOTSPOT CLUSTERING ----------------

def detect_hotspots(latitudes, longitudes):

    coords = np.column_stack((latitudes, longitudes))

    clustering = DBSCAN(
        eps=0.01,
        min_samples=3
    ).fit(coords)

    return clustering.labels_