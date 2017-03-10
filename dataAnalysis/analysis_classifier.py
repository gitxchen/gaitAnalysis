import os.path as path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA, KernelPCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

from utils import OUT_FOLDER

analysis_file = path.join(OUT_FOLDER, 'analysis.csv')
data = pd.read_csv(analysis_file, sep=';')

Y = data['class'].values
X = data.drop(['class', 'patient', 'file'], axis=1).as_matrix()

# Fix for infinite values (only one actually)
infinites = ~np.isfinite(X)
X[infinites] = np.max(X[~infinites])

pca = PCA(n_components=15)
kpca_poly = KernelPCA(n_components=15, kernel='poly')
kpca_poly5 = KernelPCA(n_components=15, kernel='poly', degree=5)
kpca_rbf = KernelPCA(n_components=15, kernel='rbf')

X_pca = pca.fit_transform(X, Y)
X_kpca_poly = kpca_poly.fit_transform(X, Y)
X_kpca_poly5 = kpca_poly5.fit_transform(X, Y)
X_kpca_rbf = kpca_rbf.fit_transform(X, Y)

Xs = {
    'full': X,
    'pca': X_pca,
    'kpca_poly': X_kpca_poly,
    'kpca_poly5': X_kpca_poly5,
    'kpca_rbf': X_kpca_rbf
}

cfs = {
    'RF_gini': RandomForestClassifier(criterion='gini'),
    'RF_entropy': RandomForestClassifier(criterion='entropy'),
    'SVM': SVC()
}

results = []

for X_name, X in Xs.iteritems():
    for cf_name, cf in cfs.iteritems():
        Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.3, stratify=Y)
        cf.fit(Xtrain, Ytrain)

        acc_train = cf.score(Xtrain, Ytrain)
        acc_test = cf.score(Xtest, Ytest)

        scores_cv = cross_val_score(cf, X, Y, cv=10)

        cv_acc_mean = scores_cv.mean()
        cv_acc_std = scores_cv.std()

        results.append([
            X_name,
            cf_name,
            acc_train,
            acc_test,
            cv_acc_mean,
            cv_acc_std
        ])

df_results = pd.DataFrame(results, columns=[
    'dataset', 'classifier',
    'acc_train', 'acc_test',
    'cv_acc_mean', 'cv_acc_std'
]).sort('cv_acc_mean', ascending=False)

results_file = path.join(OUT_FOLDER, 'results.csv')
df_results.to_csv(results_file, sep=';', index=False)
