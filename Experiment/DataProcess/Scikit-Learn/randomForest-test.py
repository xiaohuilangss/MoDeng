# encoding = utf-8

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

# 下载数据并整理成df格式
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)

# 随机分割训练数据和测试数据
df['is_train'] = np.random.uniform(0, 1, len(df)) <= .75
df['species'] = pd.Categorical.from_codes(iris.target, iris.target_names)
df.head()

train, test = df[df['is_train']==True], df[df['is_train']==False]

# 整理feature和label
features = df.columns[:4]
clf = RandomForestClassifier(n_jobs=2)
y, _ = pd.factorize(train['species'])
clf.fit(train[features], y)

preds = clf.predict_proba(test[features])

preds = iris.target_names[clf.predict_proba(test[features])]
pd.crosstab(test['species'], preds, rownames=['actual'], colnames=['preds'])