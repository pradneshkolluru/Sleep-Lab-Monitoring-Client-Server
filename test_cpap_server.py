import sys
import pytest
from pymodm import connect
from health_db_patient import Patient
from datetime import datetime
import ssl
import os
import ast

good_patient = {"mrn": 10304, "roomNum": 32, "name": "Becky", "pressure": 3}
good_patient2 = {"mrn": 804, "roomNum": 301, "name": "UnitTestz",
                 "pressure": 43}
good_patient3 = {"mrn": 120, "roomNum": 402, "name": "UnitTestz",
                 "pressure": 12}
good_patient4 = {"mrn": 900, "roomNum": 302, "name": "UnitTestz",
                 "pressure": 14}
good_patient5 = {"mrn": 720, "roomNum": 401, "name": "UnitTestz",
                 "pressure": 19}
result1 = {"mrn": 804, "breathingRate": 27.3, "apneaCount": 8,
           "image": "abcd"}
result2 = {"mrn": 804, "breathingRate": 22.3, "apneaCount": 2,
           "image": "efghij"}
result3 = {"mrn": 120, "breathingRate": 29.3, "apneaCount": 0,
           "image": "jklmno"}
result4 = {"mrn": 900, "breathingRate": 97.6, "apneaCount": 8,
           "image": "pqrstu"}


@pytest.mark.parametrize("in_dict, expected_keys, expected_types, expected", [
    ({"a": 1, "b": "two"}, ("a", "b"), ([int], [str]), True),
    ({"a": 1, "b": None}, ("a", "b"), ([int], [float, type(None)]), True),
    ({"a": 1, "b": "two"}, ("head",), ([int],),
        "head key is not found in the input"),
    ({"a": 1, "b": "two", "c": False}, ("a", "b"), ([int], [str]), True),
    ("string", ("a", "b"), ([int], [str]),
        "Data sent with post request must be a dictionary."),
    (["a", "b"], ("a", "b"), ([int], [str]),
        "Data sent with post request must be a dictionary."),
    ({"b": "two"}, ("a", "b"), ([int], [str]),
        "a key is not found in the input"),
    ({"a": 1, "c": "two"}, ("a", "b"), ([int], [str]),
        "b key is not found in the input"),
    ({"a": "1", "b": "two"}, ("a", "b"), ([int], [str]),
        "a key should be of type int"),
    ({"a": 1, "b": 2}, ("a", "b"), ([int], [str]),
        "b key should be of type str"),
    ({"a": "1a", "b": "two", "c": False}, ("a", "b"), ([int, str], [str]),
        "a key cannot be converted into type integer"),
    ({"a": float(3), "b": "two", "c": False}, ("a", "b"), ([int, str], [str]),
        "a key should be of type string or int"),
    ({"a": 1, "b": "2", "c": False}, ("a", "b"), ([int], [int, str]), True),
    ({"email": "dukelabs@hospital.com"}, ("email",), ([str],), True)
])
def test_generic_post_route_input_verification(in_dict, expected_keys,
                                               expected_types, expected):
    # Arrange
    from cpap_server import generic_post_route_input_verification
    # Act
    answer = generic_post_route_input_verification(in_dict, expected_keys,
                                                   expected_types)
    # Assert
    assert answer == expected


def test_add_patient_to_database():
    # Arrange
    from cpap_server import add_patient_to_database
    out_dict = good_patient
    # Act
    add_patient_to_database(out_dict)
    # Assert
    #   Get the new entry made in the database
    patient = Patient.objects.raw({"_id": good_patient["mrn"]}).first()
    patient.delete()
    #   Check that the id is in the keys
    assert patient.mrn == good_patient["mrn"]
    #   Check that the patient record has the correct information
    assert patient.name == good_patient["name"]
    assert patient.roomNum == good_patient["roomNum"]


@pytest.mark.parametrize("in_dict, expected", [
    ({"mrn": 10240, "roomNum": 32,
      "name": "Billy", "pressure": 4}, ("Patient Added", 200)),
    ({"mrn": 10240, "roomNum": 32,
      "name": "Billy", "pressure": None}, ("Patient Added", 200)),
    ({"mrn": 10240, "roomNum": 32,
      "name": None, "pressure": None}, ("Patient Added", 200)),
    ({"mrn": 10240, "roomNum": 32,
      "name": None, "pressure": "43"}, ("Patient Added", 200)),
    ({}, ("mrn key is not found in the input", 400)),
    ("string", ("Data sent with post request must be a dictionary.", 400)),
    ({"mrn": "1024a", "roomNum": 32,
      "name": "Bob", "pressure": 3},
     ("mrn key should be of type int", 400))
])
def test_new_patient_driver(in_dict, expected):
    """
    For the new_patient_driver function, I see it can have four different
    outcomes:
    a) it can successfully add a patient, return a status code of 200
    b) it can return a 400 status code due to a bad/missing key
    c) it can return a 400 status code due to the input not being a dictionary
    d) it can return a 400 status code due to a bad value type
    So, one test is written for each of those cases.
    In addition to checking the return from the new_patient_driver function,
    the presence or absence of the patient record in the database is also
    checked.
    """
    # Arrange
    from cpap_server import new_patient_driver
    # Act
    answer, status_code = new_patient_driver(in_dict)
    # Assert
    assert (answer, status_code) == expected
    if status_code == 200:
        db_answer = Patient.objects.raw({"_id": 10240}).first()
        db_answer.delete()
        assert db_answer.roomNum == 32


@pytest.mark.parametrize("in_dict, expected", [
    ({"fileName": os.path.join(os.getcwd(), "sample_data/patient_01.txt")},
     (200,)),
    ({}, ("fileName key is not found in the input", 400)),
    ({"fileName": "patient_001.txt"}, ("patient_001.txt does not exist", 400)),
    ("string", ("Data sent with post request must be a dictionary.", 400)),
])
def test_calc_Metrics_driver(in_dict, expected):

    # Arrange
    from cpap_server import calc_Metrics_driver
    # Act
    answer, status_code = calc_Metrics_driver(in_dict)
    # Assert
    if len(expected) > 1:
        assert (answer, status_code) == expected
    else:
        assert status_code == expected[0]


@pytest.mark.parametrize("id_to_find, expected", [
    (good_patient["mrn"], True),
    (good_patient["mrn"] + 1, False)
])
def test_verify_patient_in_db(id_to_find, expected):
    # Arrange
    from cpap_server import verify_patient_in_db, add_patient_to_database
    add_patient_to_database(good_patient)
    # Action
    answer = verify_patient_in_db(id_to_find)
    assert answer == expected
    # Clear Database
    db_answer = Patient.objects.raw({"_id": 10304}).first()
    db_answer.delete()


def test_add_test_to_patient():
    from cpap_server import add_test_to_patient, add_patient_to_database
    # Arrange
    add_patient_to_database(good_patient)
    out_data = {"mrn": 10304,
                "pressure": 5,
                "breathingRate": 22.3,
                "apneaCount": 2,
                "image": "fdafjalkdf"}
    # Action
    answer = add_test_to_patient(out_data)
    # Get database entry and clear
    db_answer = Patient.objects.raw({"_id": 10304}).first()
    db_answer.delete()
    # Assert
    assert answer == ("Test successfully added", 200)
    assert len(db_answer.results) == 1


@pytest.mark.parametrize("in_data, expected", [
    ({"mrn": 10304, "pressure": 5, "breathingRate": 22.3, "apneaCount": 2,
      "image": "fdafa"},
     ("Test successfully added", 200)),
    ({"pressure": 5, "breathingRate": 22.3, "apneaCount": 2, "image": "12af"},
     ("mrn key is not found in the input", 400)),
    ({"mrn": 10305, "pressure": 5, "breathingRate": 22.3, "apneaCount": 2,
      "image": "test"},
     ("Patient mrn 10305 does not exist in database", 400)),
])
def test_add_test_driver(in_data, expected):
    # Arrange
    from cpap_server import add_patient_to_database, add_test_driver
    add_patient_to_database(good_patient)
    # Act
    answer, status_code = add_test_driver(in_data)
    # Get data from and clean database
    patient = Patient.objects.raw({"_id": 10304}).first()
    patient.delete()
    # Assert
    assert (answer, status_code) == expected
    if status_code == 200:
        assert len(patient.results) == 1


def test_updateInfo():
    from cpap_server import updateInfo, add_patient_to_database
    # Arrange
    add_patient_to_database(good_patient)
    out_data = {"mrn": 10304,
                "pressure": 5,
                "name": "billy"}
    # Action
    answer = updateInfo(out_data)
    # Get database entry and clear
    db_answer = Patient.objects.raw({"_id": 10304}).first()
    db_answer.delete()
    # Assert
    assert answer == ('Patient MRN 10304 Succesfully Updated', 200)
    assert db_answer.pressure == 5
    assert db_answer.name == "billy"


@pytest.mark.parametrize("in_data, expected", [
    ({"mrn": 10304, "pressure": 5, "name": 'billy'},
     ("Patient MRN 10304 Succesfully Updated", 200)),
    ({"mrn": 10304, "pressure": 5, "name": None},
     ("Patient MRN 10304 Succesfully Updated", 200)),
    ({"mrn": 10304, "pressure": None, "name": None},
     ("Patient MRN 10304 Succesfully Updated", 200)),
    ({"mrn": 10304, "pressure": None, "name": "billy"},
     ("Patient MRN 10304 Succesfully Updated", 200)),
    ({"mrn": 10304, "pressure": 5, "name": 'billy'},
     ("Patient MRN 10304 Succesfully Updated", 200)),
    ({"pressure": 5, "breathingRate": 22.3, "apneaCount": 2, "image": "12af"},
     ("mrn key is not found in the input", 400)),
    ({"mrn": 10305, "pressure": 5, "name": "bob"},
     ("Patient mrn 10305 does not exist in database", 400)),
])
def test_updateInfo_driver(in_data, expected):
    # Arrange
    from cpap_server import add_patient_to_database, updateInfo_driver
    add_patient_to_database(good_patient)
    # Act
    answer, status_code = updateInfo_driver(in_data)
    # Get data from and clean database
    patient = Patient.objects.raw({"_id": 10304}).first()
    patient.delete()
    # Assert
    assert (answer, status_code) == expected


def test_get_used_rooms_driver():
    from cpap_server import add_patient_to_database, add_test_to_patient
    from cpap_server import get_used_rooms_driver
    # Arrange
    add_patient_to_database(good_patient2)
    add_patient_to_database(good_patient3)
    add_patient_to_database(good_patient4)
    add_test_to_patient(result1)
    add_test_to_patient(result2)
    add_test_to_patient(result3)
    add_test_to_patient(result4)
    # Act
    print(get_used_rooms_driver())
    all_rooms = list(get_used_rooms_driver())
    rooms_to_check = [301, 302, 402]
    rel_vals = sum(1 for room in all_rooms if room in rooms_to_check)
    print(rel_vals)
    # Assert
    assert rel_vals == 3
    # Clean database
    pt1_to_delete = Patient.objects.raw({"_id": 804}).first()
    pt1_to_delete.delete()
    pt2_to_delete = Patient.objects.raw({"_id": 120}).first()
    pt2_to_delete.delete()
    pt3_to_delete = Patient.objects.raw({"_id": 900}).first()
    pt3_to_delete.delete()


@pytest.mark.parametrize("roomnum, expected", [
    (301,
     {'mrn': 804, 'name': 'UnitTestz', 'p': 43,
      'br': 22.3, 'ac': 2, 'img': 'efghij'}),
    (302,
     {'mrn': 900, 'name': 'UnitTestz', 'p': 14,
      'br': 97.6, 'ac': 8, 'img': 'pqrstu'}),
    (402,
     {'mrn': 120, 'name': 'UnitTestz', 'p': 12,
      'br': 29.3, 'ac': 0, 'img': 'jklmno'}),
    (401,
     {'mrn': 720, 'name': 'UnitTestz', 'p': 19,
      'br': 'N/A', 'ac': 'N/A', 'img': 'N/A'})])
def test_get_infofromroom_driver(roomnum, expected):
    from cpap_server import add_patient_to_database, add_test_to_patient
    from cpap_server import get_infofromroom_driver
    # Arrange
    add_patient_to_database(good_patient2)
    add_patient_to_database(good_patient3)
    add_patient_to_database(good_patient4)
    add_patient_to_database(good_patient5)
    add_test_to_patient(result1)
    add_test_to_patient(result2)
    add_test_to_patient(result3)
    add_test_to_patient(result4)
    # Act
    notimedict = get_infofromroom_driver(roomnum)
    if 'time' in notimedict:
        del notimedict['time']
    answer = notimedict
    print(answer)
    # Assert
    assert answer == expected
    # Clean database
    pt1_to_delete = Patient.objects.raw({"_id": 804}).first()
    pt1_to_delete.delete()
    pt2_to_delete = Patient.objects.raw({"_id": 120}).first()
    pt2_to_delete.delete()
    pt3_to_delete = Patient.objects.raw({"_id": 900}).first()
    pt3_to_delete.delete()
    pt4_to_delete = Patient.objects.raw({"_id": 720}).first()
    pt4_to_delete.delete()


@pytest.mark.parametrize("mrn, expected", [
    (804, True),
    (120, True),
    (900, True),
    (720, False)])
def test_do_results_exist(mrn, expected):
    from cpap_server import add_patient_to_database, add_test_to_patient
    from cpap_server import do_results_exist
    # Arrange
    add_patient_to_database(good_patient2)
    add_patient_to_database(good_patient3)
    add_patient_to_database(good_patient4)
    add_patient_to_database(good_patient5)
    add_test_to_patient(result1)
    add_test_to_patient(result2)
    add_test_to_patient(result3)
    add_test_to_patient(result4)
    # Act
    trueorfalse = do_results_exist(mrn)
    # Assert
    assert trueorfalse == expected
    # Clean database
    pt1_to_delete = Patient.objects.raw({"_id": 804}).first()
    pt1_to_delete.delete()
    pt2_to_delete = Patient.objects.raw({"_id": 120}).first()
    pt2_to_delete.delete()
    pt3_to_delete = Patient.objects.raw({"_id": 900}).first()
    pt3_to_delete.delete()
    pt4_to_delete = Patient.objects.raw({"_id": 720}).first()
    pt4_to_delete.delete()


@pytest.mark.parametrize("mrn, expected", [
    (804, ('43', 200)),
    (120, ('12', 200)),
    (900, ('14', 200)),
    (720, ('19', 200)),
    (146, ('Patient mrn 146 does not exist in database', 400))])
def test_get_pressure_from_mrn_driver(mrn, expected):
    from cpap_server import add_patient_to_database, add_test_to_patient
    from cpap_server import get_pressure_from_mrn_driver
    # Arrange
    add_patient_to_database(good_patient2)
    add_patient_to_database(good_patient3)
    add_patient_to_database(good_patient4)
    add_patient_to_database(good_patient5)
    add_test_to_patient(result1)
    add_test_to_patient(result2)
    add_test_to_patient(result3)
    add_test_to_patient(result4)
    # Act
    assert get_pressure_from_mrn_driver(mrn) == expected
    # Clean database
    pt1_to_delete = Patient.objects.raw({"_id": 804}).first()
    pt1_to_delete.delete()
    pt2_to_delete = Patient.objects.raw({"_id": 120}).first()
    pt2_to_delete.delete()
    pt3_to_delete = Patient.objects.raw({"_id": 900}).first()
    pt3_to_delete.delete()
    pt4_to_delete = Patient.objects.raw({"_id": 720}).first()
    pt4_to_delete.delete()


@pytest.mark.parametrize("mrn, expected", [
    (804, 1),
    (120, 0),
    (900, 0)])
def test_get_test_dates_driver(mrn, expected):
    from cpap_server import add_patient_to_database, add_test_to_patient
    from cpap_server import get_test_dates_driver
    # Arrange
    add_patient_to_database(good_patient2)
    add_patient_to_database(good_patient3)
    add_patient_to_database(good_patient4)
    add_test_to_patient(result1)
    add_test_to_patient(result2)
    add_test_to_patient(result3)
    add_test_to_patient(result4)
    # Act
    prevtests = get_test_dates_driver(mrn)
    print(len(prevtests))
    assert len(prevtests) == expected
    # Clean database
    pt1_to_delete = Patient.objects.raw({"_id": 804}).first()
    pt1_to_delete.delete()
    pt2_to_delete = Patient.objects.raw({"_id": 120}).first()
    pt2_to_delete.delete()
    pt3_to_delete = Patient.objects.raw({"_id": 900}).first()
    pt3_to_delete.delete()


"""
test_get_old_img_driver() statement:

I don't believe it is worth performing unit testing on get_old_img_driver.
The datetime input makes it nearly impossible to test on the dummy variables
being created to run the tests above, since these values are constantly
updating and would change even if run at different points within the same func.

I have run the gui and showed that it is able to convert from a dataeval and
mrn back to an image, (the image succesfully displays)
"""
