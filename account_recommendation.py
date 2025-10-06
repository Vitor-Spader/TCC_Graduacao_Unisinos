import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split

# Número de usuários e produtos
n_users = 5
n_products = 20

# Criando combinações usuário-produto
data = []
for user in range(n_users):
    for product in range(n_products):
        # Features simuladas: histórico, preço normalizado, similaridade
        feature1 = np.random.rand()   # histórico do usuário com produtos da mesma categoria
        feature2 = np.random.rand()   # preço normalizado
        feature3 = np.random.rand()   # similaridade com compras passadas
        
        # Rótulo: comprou (1) ou não (0)
        label = np.random.choice([0, 1], p=[0.9, 0.1])  # poucos positivos
        
        data.append([user, product, feature1, feature2, feature3, label])

df = pd.DataFrame(data, columns=["user_id", "product_id", "f1", "f2", "f3", "label"])
print(df.head())

X = df[["f1", "f2", "f3"]]
y = df["label"]
groups = df.groupby("user_id").size().to_list()  # tamanho do grupo por usuário

train_data = lgb.Dataset(X, label=y, group=groups)

params = {
    "objective": "lambdarank",   # Ranking
    "metric": "ndcg",            # Avaliação por ranking
    "ndcg_eval_at": [5],         # Avaliação no top-5
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_data_in_leaf": 10
}

model = lgb.train(params, train_data, num_boost_round=50)

# Simulação de features para um novo usuário com 10 produtos candidatos
new_products = 10
X_new = np.random.rand(new_products, 3)  # f1, f2, f3
product_ids = list(range(new_products))

# Predição
scores = model.predict(X_new)

# Ordenando por relevância
ranking = sorted(zip(product_ids, scores), key=lambda x: x[1], reverse=True)

print("Ranking de produtos recomendados:")
for prod, score in ranking:
    print(f"Produto {prod} - score {score:.4f}")

