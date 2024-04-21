from utils.decos import StreamInfo_
from utils.rtsys import SigIntercept
from utils.rtsys import BasicRecv
from utils.tools import *

from custom import PreProcessing
from custom import ChannelNorm
from custom import CLEEGNing

import prettytable as pt
from scipy.io import savemat
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

    # block2 = ChannelNorm(128.0, parent=block1)
    # block3 = CLEEGNing(
    #     ".temp/biosemi.pth", sfreq_OS=128.0, parent=block2
    # )
    # cleegn_ssvep_2023/S011.pth models/BCI-ERN_test.pth
    # models/valid-0.pth

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
        print("Filtered data: ")
        print(chunk_1)
        alpha_power = np.mean(chunk_1, axis=1)
        print(f'Alpha power: {alpha_power}')

        mean_alpha_power = np.mean(alpha_power)
        print(f'Mean alpha power: {mean_alpha_power}')

if __name__ == "__main__":
    main()
