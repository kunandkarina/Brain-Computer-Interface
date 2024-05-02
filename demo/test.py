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
    window_features.append(df['thresholds'][i-window:i].values)
window_features = np.array(window_features)
# print(window_features)
# fit the model
kmeans.fit(window_features)
# get the cluster centers
centers = kmeans.cluster_centers_
# get the cluster labels
labels = kmeans.labels_
# plot the data
plt.scatter(df['time'][:len(labels)], df['thresholds'][:len(labels)], c=labels)
plt.xlabel('time')
plt.ylabel('thresholds')
plt.title('windowSize = 15 ')
# print the time that the thresholds is classified change


thres_sum = 0
cnt = 0
for i in range(len(labels)-1):
    if labels[i] != labels[i+1]:
        print(df['time'][i])
        thres_sum += df['thresholds'][i]
        cnt += 1
avg_thres = thres_sum / cnt
print(avg_thres)
# plot avg_thres line
plt.axhline(y=avg_thres, color='r', linestyle='--')
plt.savefig('windows15.png')
plt.show()
