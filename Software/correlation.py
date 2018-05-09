import numpy as np
import pandas as pd
from numpy import corrcoef
from scipy.signal import butter, lfilter, welch, find_peaks_cwt


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
    print(len(resting_o1))
    assert len(resting_o1) % (2 * fs) == 0
    resting_o1 = resting_o1.values.reshape((int(len(resting_o1) / (2 * fs)), 2 * fs))
    # power list to store the power spectrum for each epoch
    freq = []
    powers = []
    for epoch in resting_o1:
        f, power = welch(epoch, nperseg=fs, noverlap=None)
        freq = f
        powers.append(power)
    powers = np.asarray(powers)
    # take the mean of power
    mean_power = np.mean(powers, axis=0)
    assert len(mean_power) == powers.shape[1]
    # get correlations between each epoch power, and mean power
    corrs = []
    for power in powers:
        corrs.append(corrcoef(power, mean_power)[0][1])

    return np.mean(corrs)


def correlation_rest_read():
    """
    Get mean of rest (2 second)

    Corr(rest_mean, read live)
    :return:
    """
    pass


def get_baseline(file_dir, low, high, fs, order=4):
    df = read_data(file_dir)
    filtered_df = high_pass(low, high, df, fs, order)
    # cut length
    o1 = filtered_df["O1"]
    o1_truncate = len(o1) % (2 * fs)
    o1 = o1.iloc[0:(len(o1) - o1_truncate)]
    return baseline(o1, fs)
