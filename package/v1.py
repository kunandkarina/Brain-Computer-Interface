import numpy as np
import matplotlib.pyplot as plt
from pylsl import resolve_stream
from pylsl import StreamInlet
from time import monotonic, sleep
import queue
import time
from adaptive import kmeans
# import serial

qsize = 30
kmeans_model = None
avg_thres = 0

def main():
    # import argparse
    # parser = argparse.ArgumentParser(description="CECNL BCI 2023 Car Demo")
    # parser.add_argument("port_num", type=str, help="Arduino bluetooth serial port")
    # args = parser.parse_args()
    # ser = serial.Serial(args.port_num, 9600, timeout=1, write_timeout=1)

    q = queue.Queue(maxsize=qsize)
    streams = resolve_stream('name', 'OpenViBE Stream1')
    inlet = StreamInlet(streams[0])

    # -----------------alter-----------------
    start = monotonic()
    Thres = []
    Time = []
    collect_data = False
    # ---------------------------------------

   
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
                avg_thres = kmeans(np.array(Thres), np.array(Time))
                print("Average Threshold:", avg_thres)
                collect_data = True
                
        #-----------------open eyes to move forward, closed eyes to stop----------------- 
            if collect_data:
                if ratio < avg_thres and q.qsize() == qsize:
                    print("move forward", ratio)
                    # ser.write(b'1')
                else:
                    print("stop ", ratio)
                    # ser.write(b'0')
        # ------------------------------------------------------------------------------
        time.sleep(0.2)
   
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(0)


    