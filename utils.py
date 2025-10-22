import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def calc_line_params(x1, y1, x2, y2):
    """Calculate line parameters (slope and intercept)"""
    a = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
    b = y1 - a * x1
    return a, b

def distance_to_line(a, b, x, y):
    """Calculate vertical distance from point to line"""
    return y - (a * x + b)

def fit_resistance_from_maxima(max_series, close_series=None, tolerance=0.01):
    """Fit resistance line from local maxima"""
    if len(max_series) < 2:
        raise ValueError("At least two points are required to draw a line.")

    max_series = max_series.dropna()
    y = max_series.values
    x = np.arange(len(y))

    def check_fit_resistance(x1_idx, x2_idx):
        a, b = calc_line_params(x[x1_idx], y[x1_idx], x[x2_idx], y[x2_idx])
        n_touches = 0

        for i in range(len(x)):
            if i in (x1_idx, x2_idx):
                continue
            y_line = a * x[i] + b
            delta = y[i] - y_line

            if delta > y_line * tolerance:
                return None
            elif abs(delta) <= y_line * tolerance:
                n_touches += 1

        return {'a': a, 'b': b, 'x1_idx': x1_idx, 'x2_idx': x2_idx}
    
    for start_idx in range(len(x) - 2):
        result = check_fit_resistance(start_idx, len(x) - 1)
        if result:
            sub_series = max_series.iloc[result['x1_idx']:result['x2_idx'] + 1]
            return result['a'], result['b'], sub_series
    
    raise ValueError("Unable to find a valid resistance.")

def fit_support_from_minimum(min_series, close_series=None, tolerance=0.01):
    """Fit support line from local minima"""
    if len(min_series) < 2:
        raise ValueError("At least two points are required to draw a line.")

    min_series = min_series.dropna()
    y = min_series.values
    x = np.arange(len(y))

    def check_fit_support(x1_idx, x2_idx):
        a, b = calc_line_params(x[x1_idx], y[x1_idx], x[x2_idx], y[x2_idx])
        n_touches = 0

        for i in range(len(x)):
            if i in (x1_idx, x2_idx):
                continue
            y_line = a * x[i] + b
            delta = y[i] - y_line

            if delta < -abs(y_line * tolerance):
                return None
            elif abs(delta) <= abs(y_line * tolerance):
                n_touches += 1
        
        return {'a': a, 'b': b, 'x1_idx': x1_idx, 'x2_idx': x2_idx}
    
    for start_idx in range(len(x) - 2):
        result = check_fit_support(start_idx, len(x) - 1)
        if result:
            sub_series = min_series.iloc[result['x1_idx']:result['x2_idx'] + 1]
            return result['a'], result['b'], sub_series
    
    raise ValueError("Unable to find a valid support.")

def find_trend_index(moyenne_mobile):
    """Find the index of the last trend in moving average"""
    for i in range(1, len(moyenne_mobile) + 1):
        sign = np.sign(moyenne_mobile[-i])
        count = 0
        for j in range(len(moyenne_mobile) - i):
            tmp = 0
            if np.sign(moyenne_mobile[-1 - i - j]) == sign:
                count += 1
            elif (tmp == 0) and (abs(-2 - i - j) <= len(moyenne_mobile)):
                if np.sign(moyenne_mobile[-2 - i - j]) == sign:
                    count += 1
                else:
                    break
            else:
                break
        if count >= 2:
            break
    return len(moyenne_mobile) - (i), count + 1

def find_trend(moyenne_mobile, max_mobile, min_mobile):
    """Extract the last trend from moving averages"""
    index, frame = find_trend_index(moyenne_mobile.diff())
    if frame < 2:
        raise ValueError("At least 3 periods are required for a trend.")
    
    moyenne_mobile = moyenne_mobile[index - frame:index + 1]
    max_mobile = max_mobile[index - frame:index + 1]
    min_mobile = min_mobile[index - frame:index + 1]
    
    return moyenne_mobile, max_mobile, min_mobile, frame, index

def define_resistance(new_max_mobile, df):
    """Define resistance line in dataframe"""
    target_start = new_max_mobile.index[0]
    start_index_resistance = df[(df['periode'] == target_start) & (df['High'] == new_max_mobile[0])].index[0]
    target_end = new_max_mobile.index[-1]
    end_index_resistance = df[(df['periode'] == target_end) & (df['High'] == new_max_mobile[-1])].index[0]
    
    x0 = start_index_resistance
    x1 = end_index_resistance
    y0 = new_max_mobile[0]
    y1 = new_max_mobile[-1]

    a, b = calc_line_params(x0, y0, x1, y1)
    resistance = np.zeros(df.shape[0])
    x_range = np.arange(x0, x1 + 1)
    resistance[x0:x1 + 1] = a * x_range + b

    return resistance

def define_support(new_min_mobile, df):
    """Define support line in dataframe"""
    target_start = new_min_mobile.index[0]
    start_index_support = df[(df['periode'] == target_start) & (df['Low'] == new_min_mobile[0])].index[0]
    target_end = new_min_mobile.index[-1]
    end_index_support = df[(df['periode'] == target_end) & (df['Low'] == new_min_mobile[-1])].index[0]
    
    x0 = start_index_support
    x1 = end_index_support
    y0 = new_min_mobile[0]
    y1 = new_min_mobile[-1]

    a, b = calc_line_params(x0, y0, x1, y1)
    support = np.zeros(df.shape[0])
    x_range = np.arange(x0, x1 + 1)
    support[x0:x1 + 1] = a * x_range + b

    return support

def find_psychological_levels(df, nb_seuil, cutting=100, tolerance=0.001):
    """Find psychological price levels"""
    max_price = df['High'].max()
    min_price = df['Low'].min()
    result = {}

    variance_high = df['High'].var()
    variance_low = df['Low'].var()
    variance_total = variance_high + variance_low
    pas = np.sqrt(variance_total)

    for val in np.linspace(min_price, max_price, cutting):
        abs_tolerance = val * tolerance
        count = df[((df['High'] >= val - abs_tolerance) & (df['High'] <= val + abs_tolerance)) |
                   ((df['Low'] >= val - abs_tolerance) & (df['Low'] <= val + abs_tolerance))].shape[0]
        result[val] = count
    
    filtered_thresholds = {k: v for k, v in result.items() if v >= 3}
    current_interval_start = min_price
    selected_thresholds = []

    while current_interval_start <= max_price:
        current_interval_end = current_interval_start + pas
        candidates = [(val, count) for val, count in filtered_thresholds.items()
                      if current_interval_start <= val < current_interval_end]
        if candidates:
            best_candidate = max(candidates, key=lambda x: x[1])
            selected_thresholds.append(best_candidate)
            for candidate in candidates:
                filtered_thresholds.pop(candidate[0], None)
        current_interval_start = current_interval_end

    best_psycho_threshold = sorted(selected_thresholds, key=lambda x: x[1], reverse=True)[:nb_seuil]
    return best_psycho_threshold

def score_resistance(resist, data_, min_touch_dist=0.001):
    """Score resistance line quality"""
    score_test = 0
    tol = 0.01
    touches = 0
    n = len(data_)

    for i in range(n):
        if data_[i] != 0:
            diff = data_[i] - resist[i]
            if diff > resist[i] * tol:
                return -np.inf
            if abs(diff) <= min_touch_dist:
                touches += 1
            score_test += 1 / (1 + abs(diff))
 
    touch_bonus = 1 + touches / n
    return score_test * touch_bonus * (n ** 2)

def score_support(support, data_, min_touch_dist=0.001):
    """Score support line quality"""
    score_test = 0
    tol = 0.01
    touches = 0
    n = len(data_)

    for i in range(n):
        if data_[i] != 0:
            diff = support[i] - data_[i]
            if diff > support[i] * tol:
                return -np.inf
            if abs(diff) <= min_touch_dist:
                touches += 1
            score_test += 1 / (1 + abs(diff))

    touch_bonus = 1 + touches / n
    return score_test * touch_bonus * (n ** 2)

def test_resistance_glob(y1, start, y2, end, df, max_peaks, first=None, last=None, find=None):
    """Test global resistance line"""
    a, b = calc_line_params(start, y1, end, y2)
    resistance_glob = np.zeros(df.shape[0])
    x_range = np.arange(start, end + 1)
    resistance_glob[start:end + 1] = a * x_range + b

    if find is not None:
        return resistance_glob
    
    benchmark = np.zeros(df.shape[0])
    for i in range(first, last + 1):
        benchmark[max_peaks[i]] = df['High'].iloc[max_peaks[i]]

    return score_resistance(resistance_glob[start:end + 1], benchmark[start:end + 1])

def test_support_glob(y1, start, y2, end, df, min_peaks, first=None, last=None, find=None):
    """Test global support line"""
    a, b = calc_line_params(start, y1, end, y2)
    support_glob = np.zeros(df.shape[0])
    x_range = np.arange(start, end + 1)
    support_glob[start:end + 1] = a * x_range + b

    if find is not None:
        return support_glob
    
    benchmark = np.zeros(df.shape[0])
    for i in range(first, last + 1):
        benchmark[min_peaks[i]] = df['Low'].iloc[min_peaks[i]]

    return score_support(support_glob[start:end + 1], benchmark[start:end + 1])

def global_trend(df, learning_rate):
    """Detect global trend lines"""
    variance_high = df['High'].var()
    variance_low = df['Low'].var()
    variance_total = variance_high + variance_low
    pas = np.sqrt(variance_total)

    max_peaks, _ = find_peaks(df['High'], prominence=pas * learning_rate)
    min_peaks, _ = find_peaks(-df['Low'], prominence=pas * learning_rate)

    if len(max_peaks) < 2:
        raise ValueError("Not enough peaks to detect global resistance.")
    if len(min_peaks) < 2:
        raise ValueError("Not enough peaks to detect global support.")

    score_resistance_dict = {"score": -np.inf, "First_peak": 0, "Last_peak": 0}
    score_support_dict = {"score": -np.inf, "First_peak": 0, "Last_peak": 0}
    
    for i in range(len(max_peaks)):
        for peak in range(i + 1, max_peaks.shape[0]):
            tmp = test_resistance_glob(df['High'].iloc[max_peaks[i]], max_peaks[i],
                                      df['High'].iloc[max_peaks[peak]], max_peaks[peak],
                                      df, max_peaks, i, peak)
            if tmp > score_resistance_dict["score"]:
                score_resistance_dict["score"] = tmp
                score_resistance_dict["First_peak"] = max_peaks[i]
                score_resistance_dict["Last_peak"] = max_peaks[peak]

    for i in range(len(min_peaks)):
        for peak in range(i + 1, min_peaks.shape[0]):
            tmp = test_support_glob(df['Low'].iloc[min_peaks[i]], min_peaks[i],
                                   df['Low'].iloc[min_peaks[peak]], min_peaks[peak],
                                   df, min_peaks, i, peak)
            if tmp > score_support_dict["score"]:
                score_support_dict["score"] = tmp
                score_support_dict["First_peak"] = min_peaks[i]
                score_support_dict["Last_peak"] = min_peaks[peak]
    
    resistance_globale = test_resistance_glob(df['High'].iloc[score_resistance_dict["First_peak"]],
                                             score_resistance_dict["First_peak"],
                                             df['High'].iloc[score_resistance_dict["Last_peak"]],
                                             score_resistance_dict["Last_peak"],
                                             df, max_peaks, find=True)

    support_globale = test_support_glob(df['Low'].iloc[score_support_dict["First_peak"]],
                                       score_support_dict["First_peak"],
                                       df['Low'].iloc[score_support_dict["Last_peak"]],
                                       score_support_dict["Last_peak"],
                                       df, min_peaks, find=True)

    return resistance_globale, support_globale, max_peaks
