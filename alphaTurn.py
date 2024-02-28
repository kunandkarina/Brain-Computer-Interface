from pylsl import resolve_stream
from pylsl import StreamInlet
# import numpy as np
import serial
import queue
import time

thres = 0.09  # threshold
qsize = 30   # max queue size

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CECNL BCI 2023 Car Demo")
    parser.add_argument("port_num", type=str, help="Arduino bluetooth serial port")
    args = parser.parse_args()

    ser = serial.Serial(args.port_num, 9600, timeout=1, write_timeout=1)

    q = queue.Queue(maxsize=qsize)

    streams = resolve_stream('name', 'OpenViBE Stream1')
    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    t = 0
    rest = 8
    lasting = 0.5
    total = (rest + lasting) * 3
    while True:
        sample, timestamp = inlet.pull_chunk()
        t += 0.2
        if(t >= total):
            t -= total
        if timestamp:
            if(t % total >= rest and t % total < rest + lasting):
                write = b'1'
                print("collecting forward")
            elif(t % total >= rest * 2 + lasting and t % total < rest * 2 + lasting * 2):
                write = b'3'
                print("collecting left")
            elif(t % total >= rest * 3 + lasting * 2 and t % total < rest * 3 + lasting * 3):
                write = b'4'
                print("collecting right")
            else:
                write = b'0'
                if(t % total < rest):
                    print("stop collecting, next : forward")
                elif(t % total > rest * 2 + lasting * 2):
                    print("stop collecting, next : right")
                else:
                    print("stop collecting, next : left")
            
            sample = sample[0][0]
            # print(sample)  # find fish
            while q.qsize() >= qsize:
                _ = q.get()
            q.put(sample)

            ratio = sum(list(q.queue)) / q.qsize()

            if ratio > thres and q.qsize() == qsize:
                print("action triggered", ratio)
                ser.write(write)
            else:
                print("stop ", ratio)
                ser.write(b'0')
        time.sleep(0.2)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(0)