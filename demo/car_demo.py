import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from pylsl import resolve_stream
from pylsl import StreamInlet
from time import monotonic, sleep
import queue
import time
import serial

kmeans_model = None
qsize = 30
avg_thres = 0

def kmeans_f2(thres, time):
    global kmeans_model
    features = thres.reshape(-1, 1) # 2D array
    
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
    import argparse
    parser = argparse.ArgumentParser(description="CECNL BCI 2023 Car Demo")
    parser.add_argument("port_num", type=str, help="Arduino bluetooth serial port")
    args = parser.parse_args()

    ser = serial.Serial(args.port_num, 9600, timeout=1, write_timeout=1)
    
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
            print(f"time:  {end - start} ratio: {ratio}")
            if end - start > 30 and not collect_data: # 0~30s: collect data and calculate average threshold
                avg_thres = kmeans_f2(np.array(Thres), np.array(Time))
                print("Average Threshold:", avg_thres)
                collect_data = True
                

            if collect_data:
                if ratio < avg_thres and q.qsize() == qsize:
                    print("move forward", ratio)
                    ser.write(b'1')
                else:
                    print("stop ", ratio)
                    ser.write(b'0')

        time.sleep(0.2)
   
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(0)


    