# modeling/lstm_model.py
# -----------------------------------------------------------------------------
# Ce script définit et entraîne un modèle LSTM sur les séquences générées.
# Il effectue un split train/test, l'entraînement, puis affiche la précision.
# -----------------------------------------------------------------------------

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Chargement des données
X = np.load("data/lstm/X.npy")
y = np.load("data/lstm/y.npy")

# Reshape pour LSTM : (samples, time steps, features)
n_features = 2  # goals_home, goals_away
X = X.reshape((X.shape[0], -1, n_features))

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Modèle LSTM simple
model = Sequential()
model.add(LSTM(64, input_shape=(X.shape[1], n_features)))
model.add(Dropout(0.3))
model.add(Dense(3, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

# Prédiction et évaluation
y_pred = np.argmax(model.predict(X_test), axis=1)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Précision sur le jeu de test : {acc:.2f}")
