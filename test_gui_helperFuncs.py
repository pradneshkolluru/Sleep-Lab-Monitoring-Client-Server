import pytest
import base64


@pytest.mark.parametrize("count, expected", [
    (2, True),
    (1, False),
    (0, False),
    (9, True)
])
def test_dangerApnea(count, expected):

    from gui_helperFuncs import dangerApnea

    answer = dangerApnea(count)

    assert answer == expected


def test_decodeImg():
    # Arrange
    from patient_client import decodeImg

    testString = "SGVsbG8gV29ybGQhIQ=="

    # Action
    answer = decodeImg(testString)
    answer.seek(0)

    encodedPlot = base64.b64encode(answer.read()).decode('utf-8')
    assert testString == encodedPlot


@pytest.mark.parametrize("pressureVal, expected", [
    ("4", True),
    ("5", True),
    ("25", True),
    ("6", True),
    ("0", False),
    ("2", False),
    ("20.5", False),
    ("0", False),
    ("", True),
])
def test_valPressureInput(pressureVal, expected):

    from gui_helperFuncs import valPressureInput

    answer = valPressureInput(pressureVal)

    assert answer == expected
