import sys
import numpy as np
import copy
import matplotlib
import matplotlib.pyplot as plt
import logging
import json
from scipy.interpolate import make_interp_spline
from scipy.signal import find_peaks
import io
import base64

matplotlib.use('Agg')


def importData(file):
    """Read Patient CPAP measurements from txt file

    Iterates through each line if of the input data file. The function skips
    the first line as it contains information on what information is contained
    on each line of the txt file. For the rest of the lines, the lines are
    split into a one dimensional numpy array with the comma deliminator. The
    new line character is then stripped off at the end of the line and the
    strings in array are converted to floats. The processed array is then
    passed into valInput() function to be validated. If the data is valid, the
    numpy arrays are then appended to the list called data.

    :param file: filepath for Patient CPAP txt data file

    :returns: List containing patient time dependant CPAP metric data
    """

    logging.basicConfig(filename="cpapAnalyis.log", filemode="w",
                        level=logging.INFO)

    logging.info(f"Starting Analysis of: {file}")

    data = []

    filepath = file

    with open(filepath, "r") as in_file:

        in_file.readline()

        for line in in_file:

            split = np.array(line.split(','))
            split[-1] = split[-1].strip("\n")

            if valInput(split):
                data.append(np.asfarray(split, dtype=float))

    return data


def valInput(dataPoint):
    """Validates if Data At TimePoint is Valid

    If the data point array does not contain 7 values, some data is missing and
    am the error is logged with the assosciated time point. The function then
    returns False. If every element in the arary is numeric, an error is logged
    with the assoscaited time point and the funtion returns False. If the
    function has 7 elements and its contents are all numeric, the function
    returns True.

    :param datapoint: Numpy Array of ADC values for a single time point

    :returns: Boolean expressing if data is valid or not
    """

    if len(dataPoint) != 7:
        logging.error(f"Missing Data")
        return False
    for i in dataPoint:

        try:
            float(i)
        except ValueError:
            logging.error("Non-Numerical Entry")
            return False

        if i == "NaN":
            logging.error("Non-Numerical Entry")
            return False
    return True


def adcToPressure(raw):
    """Converts ADC Values to Pressure Readings

    This function takes in the raw data and for each time point, the ADC values
    is converted to a pressure values of units cm-h20 via the following formula
    Pressure (cm-H2O) = [(25.4) / (14745 - 1638)] * (ADC_value - 1638)

    :param raw: List of numpy arrays containing adc values for each time point

    :returns: List of numpy arrays containing pressure values for each time
    point
    """

    pressures = copy.deepcopy(raw)

    for i in range(len(pressures)):

        ptr = pressures[i]
        ptr[1:] = ((25.4) / (14745 - 1638)) * (ptr[1:] - 1638)

    return pressures


def calcFlows(p1, p2):
    """Calculates Volumetric Flow Rate in Venturi Tubes

    This function takes in the upstream pressure and constriction pressure and
    calculates the volumetric flow rate through tube. The density is set to
    1.199 kg/m^3, d1 is 15mm, and d2 is 12mm. The pressures are converted into
    pascals and the cross sectional areas (a1, a2) are calculated using the
    diameters. The following Equation was used to calculate flow rate
    a1 * np.sqrt((2 / p) * ((p1 - p2) / ((a1 / a2) ** 2 - 1)))

    :param p1: upstream pressure in cm-h20
    :param p2: pressue at constriction in cm-h20

    :returns: volumetric flow rate in L/sec
    """

    p = 1.199  # kg/m^3
    d1 = 15  # mm
    d2 = 12  # mm

    a1 = np.pi * ((d1 / 2) / 1000) ** 2  # m^2
    a2 = np.pi * ((d2 / 2) / 1000) ** 2  # m^2

    p1 = p1 * 98.0665  # pascals
    p2 = p2 * 98.0665  # pascals

    q = a1 * np.sqrt((2 / p) * ((p1 - p2) / ((a1 / a2) ** 2 - 1)))  # m^3/s

    return q * 1000  # L/sec


def flowTimeSeries(pressures):
    """Calculates Flow Rate for Each Time

    The function iterates through the pressures data and for each time point
    the inspiratory p1 pressure (ins) is compared to expiratory
    p1 pressure (exp). The time point is appened to the time list (t) and if
    ins is greater than or equal to exp, the flow is calculated with p1 as ins
    and p2 as p2. If ins is less than exp, the flow is calculate with p1 as
    exp and p2 as p2 and is negated to reflect expiration. This calculated flow
    value is appended to the q list.

    :param pressures: List of numpy arrays containing pressure values within
    venturi tubes at each time points

    :returns t: list of time values in seconds and q for
    :returns q: list of flow values in L/sec
    """
    t = []
    q = []

    for dp in pressures:

        ins = dp[2]
        exp = dp[3]
        p2 = dp[1]
        t.append(dp[0])

        if ins >= exp:
            q.append(calcFlows(ins, p2))
        else:
            q.append(-1 * calcFlows(exp, p2))

    totalTime = max(t) - min(t)
    return t, q, totalTime


def findPeaks(x, y):
    """Obtains Peaks from a CPAP signal

    The lists x and y are converted into numpy arrays and a spline is applied
    at a .027 sample rate to get a smoothened curve. Then a peak finiding
    scipy algorithm was applied with a height limit of .05 and a width of 2 to
    obtain the indixes of the peaks. The times and values of the peaks are
    returned as lists. Additionally the data with a smoothed curve and peaks
    marked is saved as curveFitting.png to perform quality control.

    :param x: time array
    :param y: volumetric flow rate array

    :returns: list of times of peak occurences
    """

    x = np.array(x)
    y = np.array(y)
    X_Y_Spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), int(len(x) * .027))
    Y_ = X_Y_Spline(X_)
    peaks, _ = find_peaks(Y_, .05, prominence=0.18)

    plt.plot(X_, Y_)
    plt.plot(X_[peaks], Y_[peaks], 'x', c='black', markersize=4)
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Flow (Liters/ Second)")
    plt.plot(np.zeros_like(X_), "--", color="gray")

    plt.xlim(min(x), max(x))

    buff = io.BytesIO()
    plt.savefig(buff, format='png')
    buff.seek(0)

    encodedPlot = base64.b64encode(buff.read()).decode('utf-8')

    plt.clf()

    return (X_[peaks], encodedPlot)


def breathAnalysis(t_breaths, tRecorded):
    """Obtains key Breath Metrics from breathing data

    The number of breaths is calculated by taking the length of the t_breaths
    array. The breaths per minute is calculated by dividing the number of
    breaths by the total recording time which is taken in as a parameter and
    coverted to minutes. To calculate the number of apnea events, there is a
    for loop that iterates every element in the t_breaths array to detect if
    the time between breaths is >10 seconds. If it is, the apnea counter is
    incremented. The number of breaths, breath per minute, and number of apnea
    events are returned.

    :param t_breaths: Array of times where a breath occured
    :param tRecorded: The total length of time of the breading test recording

    :returns numBreaths: Number of recorded breaths
    :returns bpm: Breaths per minute
    :returns apnea_ctr: Total Number of Apnea Events
    """

    numBreaths = len(t_breaths)
    tRecorded_min = tRecorded / 60

    bpm = numBreaths / tRecorded_min

    apnea_ctr = 0

    for i in range(len(t_breaths) - 1):

        j = i + 1

        if t_breaths[j] > t_breaths[i] + 10:

            apnea_ctr = apnea_ctr + 1

    return numBreaths, bpm, apnea_ctr


def calc_leakage(t, f):
    """Calculates Leakage from Venturi 1

    Taking in the time array and volumetric flow array, I calculated the
    integral via np.trapz formed by the curve. This integral is the leakage.
    If the leakage is negative, a warning is logged saying there is a negative
    leakage.

    :param x: time array
    :param y: volumetric flow rate array

    :returns: Leakage in Liters
    """
    t_arr = np.array(t)
    f_arr = np.array(f)

    leakage = np.trapz(f_arr, t_arr)

    if leakage < 0:
        logging.warning(f"Negative Leakage")

    return leakage


def obtainMetrics(file):
    """Computes Patient Name and Collects CPAP Metrics

    This function is essentially a driver function. The patient name is
    computed from the input file name and a output file path is generated for
    the results. The file is the imported by importData function to collect raw
    data. The raw data is then converted from adc into pressure readings. From
    these pressure, readings, a time array, flow array, and time range is
    computed. The findPeaks algorithm then takes in the time and flow array to
    identify peaks and return the times of peak occurences. The breath analysis
    code returns the number of breaths, breaths per minute, and number of apnea
    events given the t array of peak occurences and the recording time range.
    The leakage is calculated with the time and flow data. All these metrics
    are compiled and stored in a dictionary variable called metrics. The
    patient name, and metrics dictionary is returned

    :param file: filename of data that needs to be analyzed

    :returns patient_file_results: Results Output File Path for Patient
    :returns metrics: Dictionary of CPAP measurements for patient. Includes
    duration, breaths, breath_rate_bp, breath_times, apnea_count, and leakage
    """

    patient_file_results = ""

    adc = importData(file)
    pressures = adcToPressure(adc)
    t, f, range = flowTimeSeries(pressures)
    tPeaks, encodedPlot = findPeaks(t, f)
    numBreaths, bpm, apnea_ctr = breathAnalysis(tPeaks, range)
    leakage = calc_leakage(t, f)

    metrics = {"duration": range,
               "breaths": numBreaths,
               "breath_rate_bpm": bpm,
               "breath_times": tPeaks.tolist(),
               "apnea_count": apnea_ctr,
               "leakage": leakage,
               "encoded_plot": encodedPlot}

    return patient_file_results, metrics


def outputResults(output_file, metrics):
    """Output CPAP Results in Seperate JSON File

    Store content in metrics dictionary in a jsonfile specified by the output
    file

    :param output_file: Output file path for the json containing the patient
    test results
    :param output_file: Dictionary containing metrics from CPAP test results
    """
    out_file = open(output_file, "w")
    json.dump(metrics, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":

    pass
