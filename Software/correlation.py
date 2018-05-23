import numpy as np
import pandas as pd
from numpy import corrcoef
from scipy.signal import butter, lfilter, welch


def read_data(file_dir):
    """
    Read csv file
    :param file_dir: file path
    :return: DataFrame object
    """
    return pd.read_csv(file_dir, encoding='ascii')


def high_pass(low, high, df, fs, order=4):
    """
    High pass filter on raw EEG data

    :param low: low threshold
    :param high: high threshold
    :param df: raw EEG dataframe
    :param fs: sampling rate
    :param order: order dim
    :return: filtered EEG data
    """
    nyq = 0.5 * fs
    b, a = butter(order, [low / nyq, high / nyq], btype='band')
    # filtered dataframe
    fil_df = pd.DataFrame(dtype="float64")
    for i, col in enumerate(df):
        fil_df[df.columns[i]] = lfilter(b, a, df[col])

    return fil_df


def baseline(resting_o1, fs):
    """
    Using resting data to calculate baseline. For now, using channle O1

    params:
        resting_cz: Resting data from CZ with length divisible by 2 * fs
        fs: sampling rate

    returns:
        value of the baseline
    """
    assert len(resting_o1) % fs == 0
    resting_o1 = resting_o1.values.reshape((int(len(resting_o1) / fs), fs))
    # power list to store the power spectrum for each epoch
    freq = []
    powers = []
    for epoch in resting_o1:
        print(len(epoch))
        f, power = welch(epoch, nperseg=fs, noverlap=None)
        freq = f
        powers.append(power)
        print(len(power))
    powers = np.asarray(powers)
    # take the mean of power
    mean_power = np.mean(powers, axis=0)
    assert len(mean_power) == powers.shape[1]
    # get correlations between each epoch power, and mean power
    corrs = []
    for power in powers:
        corrs.append(corrcoef(power, mean_power)[0][1])

    return mean_power, np.mean(corrs)


def get_baseline(file_dir, low, high, fs, order=4):
    """
    Get baseline value from EEG resting data

    :param file_dir: file path of resting data
    :param low: low pass filter
    :param high: high pass filter
    :param fs: sampling rate
    :param order: order of filter
    :return: baseline value
    """
    df = read_data(file_dir)
    filtered_df = high_pass(low, high, df, fs, order)
    # cut length
    o1 = filtered_df["O1"]
    o1_truncate = len(o1) % fs
    o1 = o1.iloc[0:(len(o1) - o1_truncate)]
    return baseline(o1, fs)


def live_power(eeg, fs, mean_power, baseline, verbose=False):
    """
    Compares one-second EEG data to baseline correlation.

    :param eeg: eeg streamer
    :param fs: sampling rate
    :param mean_power: the mean power calculated from resting
    :param baseline: the baseline calculated from resting
    :param verbose:
    :return: True if one-second EEG has correlation with mean power over baseline
    """
    eeg.out_buffer_queue.queue.clear()
    data = np.zeros(fs)
    for i in range(fs):
        data[i] = eeg.out_buffer_queue.get()[7]
    f, power = welch(data, nperseg=fs, noverlap=None)
    # correlation of  mean power and new power
    length = min(len(mean_power), len(power))
    mean_power = mean_power[:length]
    power = power[:length]
    c = corrcoef(mean_power, power)[0][1]
    if verbose:
        print('correlation: %s' % c)
        print('baseline: %s' % baseline)
    return c >= baseline

