import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from pylsl import resolve_stream
from pylsl import StreamInlet
from time import monotonic, sleep
import queue
import time

kmeans_model = None
qsize = 30
avg_thres = 0

def dataset(time, thres, add_val):
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

def kmeans_f2(thres, time):
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
    # print(window_features)
    kmeans_model.fit(window_features)
    labels = kmeans_model.labels_

    thres_sum = 0
    cnt = 0
    for i in range(len(labels)-1):
        if labels[i] != labels[i+1]:
            thres_sum += thres[i]
            cnt += 1
    avg_thres = thres_sum / cnt
    return avg_thres   
    
    # plt.scatter(time[:len(labels)], thres[:len(labels)], c=labels, cmap='viridis', edgecolor='k', s=50, alpha=0.7)
    # plt.scatter(time[:len(labels)], [avg_thres]*len(labels), color='red', s=5, marker='o', label='Average Threshold') 
    # plt.xlabel('Time')
    # plt.ylabel('Threshold')
    # plt.title('K-Means Clustering of Alpha Band Power')
    # plt.colorbar(label='Cluster')
    # plt.show()



def main():

    time = []
    thres = []
    add_val = 0
    dataset(time, thres, add_val)
    # time = np.array(time)
    # thres = np.array(thres)
    
    # kmeans_f2(thres, time)
    
    # ----------------- Test -----------------
    # test = thres[70:85].reshape(1, -1)
    # if kmeans_model is not None:
    #     new_data = np.array(test)
    #     predicted_label = kmeans_model.predict(new_data)
    #     print("Predicted Label:", predicted_label[0])
    # else:
    #     print("KMeans model is not defined.")
    # ----------------- Test -----------------

    q = queue.Queue(maxsize=qsize)
    streams = resolve_stream('name', 'OpenViBE Stream1')
    inlet = StreamInlet(streams[0])
    start = monotonic()
    thres = []
    time = []
    while True:
        sample, timestamp = inlet.pull_chunk()
        if timestamp:
            sample = sample[0][0]
            while q.qsize() >= qsize:
               _ = q.get()
            q.put(sample)

            ratio = sum(list(q.queue)) / q.qsize()
            thres.append(ratio)
            end = monotonic()
            time.append(end - start)
            if end - start > 30:
                q.queue.clear()
                break
   
    thres = np.array(thres)
    time = np.array(time)
    avg_thres = kmeans_f2(thres, time)
    print(avg_thres)

    while True:
        sample, timestamp = inlet.pull_chunk()
        if timestamp:
            sample = sample[0][0]
            # print(sample)  # find fish
            while q.qsize() >= qsize:
                _ = q.get()
            q.put(sample)

            ratio = sum(list(q.queue)) / q.qsize()
            
            if ratio > avg_thres and q.qsize() == qsize:
                print("move forward", ratio)
            else:
                print("stop ", ratio)
        time.sleep(0.2)




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(0)


    

