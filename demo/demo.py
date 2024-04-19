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
    
def main():
  
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
    Thres = []
    Time = []
    collect_data = False
    while True:
        sample, timestamp = inlet.pull_chunk()
        if timestamp:
            sample = sample[0][0]
            while q.qsize() >= qsize:
               _ = q.get()
            q.put(sample)

            ratio = sum(list(q.queue)) / q.qsize()
            end = monotonic()
            if not collect_data:
                Thres.append(ratio)
                Time.append(end - start)
            if end - start > 30 and not collect_data:
                avg_thres = kmeans_f2(np.array(Thres), ap.array(Time))
                print("Average Threshold:", avg_thres)
                collect_data = True

            if collect_data:
                if ratio > avg_thres and q.qsize() == qsize:
                    print("move forward", ratio)
                else:
                    print("stop ", ratio)

        time.sleep(0.2)
   
    # thres = np.array(thres)
    # time = np.array(time)
    # avg_thres = kmeans_f2(thres, time)
    # print(avg_thres)

    # while True:
    #     sample, timestamp = inlet.pull_chunk()
    #     if timestamp:
    #         sample = sample[0][0]
    #         # print(sample)  # find fish
    #         while q.qsize() >= qsize:
    #             _ = q.get()
    #         q.put(sample)

    #         ratio = sum(list(q.queue)) / q.qsize()
            
    #         if ratio > avg_thres and q.qsize() == qsize:
    #             print("move forward", ratio)
    #         else:
    #             print("stop ", ratio)
    #     time.sleep(0.2)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(0)


    

