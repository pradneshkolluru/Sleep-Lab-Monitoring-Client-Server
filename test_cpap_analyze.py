import pytest
import numpy as np
import copy
from testfixtures import LogCapture
import os


@pytest.mark.parametrize("testFile, numLines, checkLogging", [
    (os.path.join(os.getcwd(), "sample_data/patient_01.txt"), 17999, True),
    (os.path.join(os.getcwd(), "sample_data/patient_01 copy.txt"),
     17996,
     False)])
def test_importData(testFile, numLines, checkLogging):

    from cpap_analyze import importData

    with LogCapture() as log_c:
        answer = importData(testFile)
    if checkLogging:
        log_c.check(("root", "INFO",
                    f"Starting Analysis of: {testFile}"))

    assert len(answer) == numLines
    for i in answer:
        assert i.dtype == np.dtype("float")
        assert len(i) == 7


@pytest.mark.parametrize("arr, errorMsg, expected", [
    (np.array([1, "A", 6, 7, 8, 9, 10]),
     "Non-Numerical Entry", False),
    (np.array([1, 3, 6, 7, 8, 9, 10]),
     None, True),
    (np.array([3, 3, "NaN", 7, 8, 9, 10]),
     "Non-Numerical Entry", False),
    (np.array([2, 3.5, 6, 8, 9, 10]),
     "Missing Data", False)])
def test_valInput(arr, errorMsg, expected):

    from cpap_analyze import valInput

    if errorMsg:
        with LogCapture() as log_c:
            answer = valInput(arr)
        log_c.check(("root", "ERROR", errorMsg))

        assert answer == expected


def test_adcToPressure():

    from cpap_analyze import adcToPressure
    testInput = [np.array([2.685e+00,
                           5.018e+03,
                           1.638e+03,
                           5.039e+03,
                           5.276e+03,
                           5.276e+03,
                           1.638e+03])]

    answer = adcToPressure(copy.deepcopy(testInput))

    groundTruth = [np.array([[2.685,
                              6.55008774,
                              0,
                              6.59078355,
                              7.05006485,
                              7.05006485,
                              0]])]

    for i in range(len(testInput)):
        assert np.allclose(answer[i], groundTruth[i])


def test_calcFlows():

    from cpap_analyze import calcFlows

    answer = calcFlows(10.0, 3.0)

    print(answer)
    assert np.isclose(answer, 4.980741048784845)


def test_flowTimeSeries():

    from cpap_analyze import flowTimeSeries

    testInput = [np.array([2.685,
                           6.55008774,
                           0,
                           6.59078355,
                           7.05006485,
                           7.05006485,
                           0]),
                 np.array([2.695,
                           6.6140383,
                           6.65279622,
                           0,
                           6.98999008,
                           6.98999008,
                           0])]

    x, y, span = flowTimeSeries(testInput)

    assert (x, y) == ([2.685, 2.695],
                      [-0.379769245383582, 0.37061686159445306])

    assert np.isclose(0.01, span)


def test_findPeaks():

    from cpap_analyze import findPeaks

    x = np.linspace(0, 8 * np.pi, 10000)
    y = np.sin(x)

    peak_x, encodedPlot = findPeaks(x, y)

    assert len(peak_x) == 4


def test_breathAnalysis():

    from cpap_analyze import breathAnalysis

    breaths, bpm, apnea_ctr = breathAnalysis([10, 15, 16, 27, 28, 30, 42], 80)

    assert breaths == 7
    assert bpm == 5.25
    assert apnea_ctr == 2


@pytest.mark.parametrize("t, f, leakageAns, checkLogging", [
    ([0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6],
     [0, 0, 0, 3, 3, 0, 0, -4, -4, 0, 0], -1, True),
    ([0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6],
     [0, 0, 0, 3, 3, 0, 0, 4, 4, 0, 0], 7, False)])
def test_calc_leakage(t, f, leakageAns, checkLogging):

    from cpap_analyze import calc_leakage

    with LogCapture() as log_c:
        leakage = calc_leakage(t, f)

    if checkLogging:
        log_c.check(("root", "WARNING", "Negative Leakage"))

    assert leakage == leakageAns


def test_obtainMetrics():

    from cpap_analyze import obtainMetrics

    file = os.path.join(os.getcwd(), "sample_data/patient_01.txt")
    patient, metrics = obtainMetrics(file)

    assert metrics['duration'] == 179.98
    assert metrics['breaths'] == 61
    assert np.isclose(metrics['breath_rate_bpm'], 20.33559)
    assert len(metrics['breath_times']) == metrics['breaths']
    assert metrics['apnea_count'] == 0
    assert np.isclose(metrics['leakage'], 14.247281)
