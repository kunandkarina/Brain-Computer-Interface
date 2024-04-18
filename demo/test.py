import os,sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Read the data from csv file
df = pd.read_csv('data1.csv')
df.head()
print(len(df))

k = 2
# KMeans clustering using 2 seconds window as features
kmeans = KMeans(n_clusters=k)
# calculate the window features
window = 15
window_features = []
for i in range(window, len(df)):
    window_features.append(df['value'][i-window:i].values)
window_features = np.array(window_features)
print(window_features)
# fit the model
kmeans.fit(window_features)
# get the cluster centers
centers = kmeans.cluster_centers_
# get the cluster labels
labels = kmeans.labels_
# plot the data
plt.scatter(df['time'][:len(labels)], df['value'][:len(labels)], c=labels)
plt.xlabel('time')
plt.ylabel('value')
plt.title('KMeans clustering using 2 seconds window as features')
# print the time that the value is classified change
for i in range(len(labels)-1):
    if labels[i] != labels[i+1]:
        print(df['time'][i])
plt.show()