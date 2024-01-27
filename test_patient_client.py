import pytest
import os


def test_calcHealthMetrics():

    from patient_client import calcHealthMetrics

    testFile = os.path.join(os.getcwd(), "sample_data/patient_01.txt")

    answer = calcHealthMetrics(testFile)

    assert round(answer[0], 2) == 20.34

    assert answer[1] == 0
