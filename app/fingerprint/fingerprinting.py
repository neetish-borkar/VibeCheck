import hashlib
from operator import itemgetter
from typing import List, Tuple

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (binary_erosion,
                                      generate_binary_structure,
                                      iterate_structure)

def get_2D_peaks(arr2D: np.array, plot: bool = False, amp_min: int = 10)\
        -> List[Tuple[List[int], List[int]]]:
    struct = generate_binary_structure(2, 2)
    neighborhood = iterate_structure(struct, 10)
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)
    detected_peaks = local_max != eroded_background
    amps = arr2D[detected_peaks]
    freqs, times = np.where(detected_peaks)
    amps = amps.flatten()
    filter_idxs = np.where(amps > amp_min)
    freqs_filter = freqs[filter_idxs]
    times_filter = times[filter_idxs]

    if plot:
        # scatter of the peaks
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
        ax.imshow(arr2D)
        ax.scatter(times_filter, freqs_filter,8, 'black')
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title("Spectrogram")
        plt.gca().invert_yaxis()
        plt.show()

    return list(zip(freqs_filter, times_filter))
    
def generate_hashes(peaks: List[Tuple[int, int]], fan_value: int = 5) -> List[Tuple[str, int]]:
    idx_freq = 0
    idx_time = 1

    if True:
        peaks.sort(key=itemgetter(1))

    hashes = []
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):

                freq1 = peaks[i][idx_freq]
                freq2 = peaks[i + j][idx_freq]
                t1 = peaks[i][idx_time]
                t2 = peaks[i + j][idx_time]
                t_delta = t2 - t1

                if 0 <= t_delta <= 200:
#                     h = hashlib.sha1(f"{str(np.sqrt((freq2 - freq1)**2 + (t2 - t1)**2))}|{str(t_delta)}".encode('utf-8'))
                    h = hashlib.sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8'))

                    hashes.append((h.hexdigest()[0:20], int(t1)))

    return hashes

def fingerprint(channel_samples: List[int], Fs: int = 44100,
                wsize: int = 4096,
                wratio: float = 0.5,
                fan_value: int = 5,
                amp_min: int = 10) -> List[Tuple[str, int]]:
    arr2D = mlab.specgram(
        channel_samples,
        NFFT=wsize,
        Fs=Fs,
        window=mlab.window_hanning,
        noverlap=int(wsize * wratio))[0]
    arr2D = 10 * np.log10(arr2D, out=np.zeros_like(arr2D), where=(arr2D != 0))
    local_maxima = get_2D_peaks(arr2D, plot=False, amp_min=amp_min)
    return generate_hashes(local_maxima, fan_value=fan_value)
    