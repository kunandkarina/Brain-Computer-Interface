from utils.decos import StreamInfo_
from utils.rtsys import SigIntercept
from utils.rtsys import BasicRecv
from utils.tools import *

from custom import PreProcessing
from custom import ChannelNorm
from custom import CLEEGNing

import prettytable as pt
from scipy.io import savemat
from scipy import signal
from scipy.integrate import simps
import numpy as np
import pylsl
import math
import time
import os

def main():
    print("looking for an EEG stream...")
    streamList = pylsl.resolve_streams()
    streamList = [StreamInfo_(s) for s in streamList]

    tb = pt.PrettyTable()
    tb.field_names = ["sid", "name", "type", "#_channel", "srate", "srcID"]
    for sid, stm in enumerate(streamList):
        sinfo = [sid, stm.name, stm.type, stm.n_chan, stm.srate, stm.ssid]
        tb.add_row(sinfo)
        # print(stm)
    print(tb)
    streamID = int(input("Select steam... "))
    selcStream = streamList[streamID]
    inlet = pylsl.StreamInlet(selcStream.lsl_stream())

    root = BasicRecv(4, selcStream.srate) #############

    # block1 = PreProcessing(2, 40, selcStream.srate, 128.0, parent=root) # 1, 40
    block1 = PreProcessing(8, 13, selcStream.srate, 128.0, parent=root)

    while True:
        pull_kwargs = {"timeout": 1, "max_samples": math.ceil(0.6 * selcStream.srate)}
        chunk, timestamps = inlet.pull_chunk(**pull_kwargs)
        chunk = np.asarray(chunk, dtype=np.float32).T
        chunk = chunk[[0,1,4,5],:]

        timestamps = np.asarray(timestamps, dtype=np.float32)
        if not len(timestamps):
            print(f"[x] Loss conection to the stream: {selcStream.name()}...")
            break # TODO: try recovery???

        root.update(chunk)
        chunk_1 = block1.step()
        block1.update(chunk_1)
        # Filter data
        # ---------------Method 1----------------
        # print("Filtered data: ")
        # min_value = np.min(chunk_1, axis=1)
        # shift_chunk = chunk_1 - min_value[:, np.newaxis]
        # alpha_power = np.mean(shift_chunk, axis=1)
        # print(f'Alpha power: {alpha_power}')
        # ---------------Method 1----------------

        # ---------------Method 2----------------
        # print("Filtered data: ")
        # shift_chunk = np.power(chunk_1, 2)
        # alpha_power = np.mean(shift_chunk, axis=1)
        # print(f'Alpha power: {alpha_power}')

        # print("Filter data: ")
        # shift_chunk = np.fft.fft(chunk_1, axis=1)
        # shift_chunk = np.power(shift_chunk, 2)
        # shift_chunk = np.mean(shift_chunk, axis=1)
        # print(f'Alpha power: {shift_chunk}')


        # ---------------Method 2----------------

        # ---------------Method 3----------------
        print("Filtered data: ")
        tmp_chunk = chunk_1[3]
        # apply Welch method
        win = 0.25 * 128
        f, psd = signal.welch(tmp_chunk, fs=128.0, nperseg=win)
        f_res = f[1] - f[0]
        # idx_alpha = np.logical_and(f >= 8, f <= 13)
        # alpha_power = simps(psd[idx_alpha], dx=f_res)
        alpha_power = simps(psd[(f >= 8) & (f <= 13)], dx=f_res)
        print(f'Alpha power: {alpha_power}')
        # ---------------Method 3----------------
        


if __name__ == "__main__":
    main()
