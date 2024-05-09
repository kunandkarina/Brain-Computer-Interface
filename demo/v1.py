import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

kmeans_model = None

def plot(time, thres):
    # 標記10~15秒和20~25秒的索引範圍
    index_10_15 = np.where((time >= 10) & (time <= 15))[0]
    index_20_25 = np.where((time >= 20) & (time <= 25))[0]

    # 繪製圖形
    plt.plot(time, thres, color='blue', label='Threshold vs Time')

    # 在指定的時間範圍內繪製紅色的連接線段
    plt.plot(time[index_10_15], thres[index_10_15], color='red', label='10-15s')
    plt.plot(time[index_20_25], thres[index_20_25], color='red', label='20-25s')

    # 顯示圖例
    plt.legend()

    # 顯示圖形
    plt.xlabel('Time')
    plt.ylabel('Threshold')
    plt.title('Threshold vs Time')
    # plt.savefig('dataset1_c2.png')
    plt.show()

def adjust_labels(labels, time):
    # 將 0~10s 和 21~30s 的樣本標記為相同的標籤（例如 0）
    for i, t in enumerate(time):
        if t <= 10 or t >= 21:
            labels[i] = 0
    return labels

def kmeans_f1(time, thres):
    global kmeans_model
    # features = np.column_stack((time, thres))

    features = thres.reshape(-1, 1)
    # print(features)

    k = 2
    # 使用 KMeans 演算法進行分群
    kmeans_model = KMeans(n_clusters=k, random_state=42).fit(features)
    labels = kmeans_model.labels_
    print(labels)
    # adjusted_labels = adjust_labels(labels, time)
    
    plt.scatter(time, thres, c=labels)
    # plt.scatter(time, thres, c=adjusted_labels)
    # 顯示圖形
    plt.xlabel('Time')
    # plt.xlabel('Threshold')
    plt.ylabel('Threshold')
    plt.title('K-Means Clustering of Alpha Band Power')

    # 顯示圖例
    plt.colorbar(label='Cluster')
    # plt.savefig('kmeans_data1_c3_feature2.png')
    plt.show()

def kmeans_f2(thres, time):
    global kmeans_model
    # features = np.column_stack((time, thres))

    features = thres.reshape(-1, 1)
    # print(features)

    k = 2
    # 使用 KMeans 演算法進行分群
    kmeans_model = KMeans(n_clusters=k, random_state=42).fit(features)
    labels = kmeans_model.labels_
    print(labels)
    
    plt.scatter(time, thres, c=labels, cmap='viridis', edgecolor='k', s=50, alpha=0.7)
    # 顯示圖形
    plt.xlabel('Time')
    plt.ylabel('Threshold')
    plt.title('K-Means Clustering of Alpha Band Power')

    # 顯示圖例
    plt.colorbar(label='Cluster')
    plt.savefig('kmeans_feature.png')
    plt.show()

def DBSCAN_model(thres):
    # features = np.column_stack((time, thres))

    features = thres.reshape(-1, 1)
    # print(features)

    # 使用 DBSCAN 演算法進行分群
    dbscan_model = DBSCAN(eps=0.01, min_samples=5).fit(features)
    labels = dbscan_model.labels_
    print(labels)
    
    # plt.scatter(thres, thres, c=labels, cmap='viridis', edgecolor='k', s=50, alpha=0.7)
    plt.scatter(time, thres, c=labels)
    # 顯示圖形
    plt.xlabel('Time')
    # plt.xlabel('Threshold')
    plt.ylabel('Threshold')
    plt.title('DBSCAN Clustering of Alpha Band Power')

    # 顯示圖例
    plt.colorbar(label='Cluster')
    plt.show()



if __name__ == '__main__':
    time = []
    thres = []
    add_val = 0

    path = 'dataset/dataset1.txt'
    with open(path) as f:
        for line in f.readlines():
            if line.strip() == '-----------------------------':
                add_val += 10
                continue
            parts = line.split()
            if parts[0] == 'stop' and add_val < 30:
                thres.append(float(parts[1]))
            elif parts[0] == 'move' and parts[1] == 'forward' and add_val < 30:
                thres.append(float(parts[2]))
            else:
                if add_val < 30:
                    if float(parts[0]) > 10:
                        parts[0] = str(float(parts[0]) - 10)
                    time.append(float(parts[0]) + add_val)

    time = np.array(time)
    thres = np.array(thres)

# -------------kmeans-------------- #
    # kmeans_f1(time, thres)
    kmeans_f2(thres, time)

    # if kmeans_model is not None:
    #     new_data = np.array([[0.5]])
    #     predicted_label = kmeans_model.predict(new_data)
    #     print("Predicted Label:", predicted_label[0])
    # else:
    #     print("KMeans model is not defined.")
# -------------kmeans-------------- #


# -------------DBSCAN-------------- #
    # DBSCAN_model(thres)