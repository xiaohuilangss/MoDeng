# encoding = utf-8
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
# 读取数据
save_dir = "F:/MYAI/文档资料/用于读取的文件/BasicDataWithQInfo/"

with open(save_dir + "basic_total.csv") as f:
    basic_total = pd.read_csv(f)


basic_total = basic_total[basic_total.quarter > 201603]

# features = ['gross_profit_rate', 'net_profit_ratio', 'epsg',
#             'mbrg', 'nav', 'nprg', 'seg', 'targ','stk_class_num']

features = ['gross_profit_rate', 'net_profit_ratio', 'epsg',
            'mbrg', 'nav', 'nprg', 'seg', 'targ','roe','pb','pe','stk_class_num']

clf = RandomForestClassifier(n_jobs=2,n_estimators=200)

X = basic_total.loc[:,features].values
y, target_names = pd.factorize(basic_total['ratio_class'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)


clf.fit(X_train, y_train)
probability = clf.predict_proba(X_test)
pred = clf.predict(X_test)
df_pre = pd.DataFrame(pred,columns=['pred'])
df_pre_probability = pd.DataFrame(probability)
df_pre_probability['probability'] = df_pre_probability.apply(lambda x:x.max(),axis=1)

real_df = pd.DataFrame(y_test,columns=['real'])

pred_result = pd.concat([df_pre_probability,real_df,df_pre],axis=1)

pred_filter = pred_result[pred_result.probability>0.9]

# 计算预测精度
acy = accuracy_score(pred_filter['real'], pred_filter['pred'])

end = 0
# pd.crosstab(test['species'], preds, rownames=['actual'], colnames=['preds'])