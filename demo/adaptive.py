import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def kmeans(thres, time):
    global kmeans_model
    features = thres.reshape(-1, 1)
    
    k = 2
    kmeans_model = KMeans(n_clusters=k, random_state=42)
    window = 15
    window_features = []
    for i in range(window, len(features)):
        window_features.append(features[i-window:i])
    window_features = np.array(window_features)
    window_features = window_features.reshape(-1, window)
    kmeans_model.fit(window_features)
    labels = kmeans_model.labels_
 
    # plt.scatter(time[:len(labels)], thres[:len(labels)], c=labels)
    # plt.xlabel("Time")
    # plt.ylabel("Threshold")
    # plt.title('KMeans clustering using 2 seconds window as features')


    thres_sum = 0
    cnt = 0
    for i in range(len(labels)-1):
        if labels[i] != labels[i+1]:
            thres_sum += thres[i]
            cnt += 1
            print("Time: ", time[i])
    avg_thres = thres_sum / cnt
    # plt.show()
    return avg_thres   