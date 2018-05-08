import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter, welch, find_peaks_cwt


def read_data(file_dir):
    """
    Read csv file
    :param file_dir: file path
    :return: DataFrame object
    """
    return pd.read_csv(file_dir)


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


def baseline(resting_cz, fs):
    """
    Using resting data to calculate baseline. For now, using channle CZ

    params:
        resting_cz: Resting data from CZ with length divisible by 2 * fs
        fs: sampling rate

    returns:
        value of the baseline
    """
    assert len(resting_cz) % (2 * fs) == 0
    resting_cz = resting_cz.values.reshape((int(len(resting_cz) / (2 * fs)), 2 * fs))
    # power list to store the power spectrum for each epoch
    freq = []
    powers = []
    for epoch in resting_cz:
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
    # baseline is the mean of correlations
    return np.mean(corrs)