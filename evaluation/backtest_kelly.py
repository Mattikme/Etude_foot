# evaluation/backtest_kelly.py
# -----------------------------------------------------------------------------
# Ce script réalise un backtest du modèle de prédiction en simulant des paris
# en appliquant le critère de Kelly à des probabilités prédites et aux cotes.
# -----------------------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelBinarizer

# ⚠️ Suppose que tu as déjà les prédictions softmax (probas) + labels vrais + odds
# À adapter selon ton format exact
predicted_probas = np.load("data/lstm/y_pred_proba.npy")  # shape: (n, 3)
y_true = np.load("data/lstm/y.npy")[-len(predicted_probas):]
odds = pd.read_csv("data/odds.csv")  # contient columns: home_odds, draw_odds, away_odds

# Encodage binaire des cibles : 1=home win, 0=draw, -1=away win → classes = [0, 1, 2]
lb = LabelBinarizer()
lb.fit([1, 0, -1])
y_true_onehot = lb.transform(y_true)

# Kelly bet computation
bankroll = 1000
kelly_history = []

for i in range(len(predicted_probas)):
    probs = predicted_probas[i]
    true = y_true[i]
    o = odds.iloc[i]
    p = probs
    b = [o.home_odds, o.draw_odds, o.away_odds]
    k = [((b[j] * p[j] - 1) / (b[j] - 1)) for j in range(3)]  # Kelly formula
    k = [max(0, min(x, 1)) for x in k]  # clamp between 0 and 1
    bet_index = np.argmax(k)
    stake = k[bet_index] * bankroll * 0.05  # fractional sizing

    won = (bet_index == np.argmax(y_true_onehot[i]))
    profit = (b[bet_index] - 1) * stake if won else -stake
    bankroll += profit
    kelly_history.append(bankroll)

# Résultat final
print(f"💰 Bankroll finale après backtest Kelly : {bankroll:.2f}€")
