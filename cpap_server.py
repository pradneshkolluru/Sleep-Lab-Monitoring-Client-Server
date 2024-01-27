"""
Database is stored in MongoDB using health_db_patient.Patient as
the MongoModel class
"""

from flask import Flask, request, jsonify
from pymodm import connect
from pymodm import errors as pymodm_errors
from health_db_patient import Patient, CPAP_Result
from cpap_analyze import obtainMetrics
import ssl
import os
from typing import Optional
import ast
from datetime import datetime

date_format = "%Y-%m-%d %H:%M:%S"

connect("mongodb+srv://pradneshkolluru:bukbat-toqfum-nyVpi9"
        "@cluster0.gh4mcsl.mongodb.net/finalProjectDB"
        "?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)

app = Flask(__name__)


def generic_post_route_input_verification(in_dict, expected_keys,
                                          expected_types):
    """
    Generic function for validating an input dictionary

    This function receives the input data to a POST route and a list/tuple of
    expected keys and expected value types.  This function verifies that the
    input data is a dictionary, that it contains the keys founds in the
    expected keys, and that the values for the keys are of the expected type.
    For values that can be strings or int val types, the function checks to see
    if it can be converted to a integer, if not, an error is returned.
    If all verifications pass, a boolean value of True is returned.  If any
    verification fails, a string message explaining the failure is returned.
    Note that the list of expected value types should be in the same order as
    the expected keys.

    Args:
        in_dict (dict/any): the input sent to the POST request.  Ideally, it
                             is a dictionary, but could be any type
        expected_keys (list/tuple): a list or tuple of what keys need to be in
                                    the input dictionary
        expected_types (list/tuple): a tuple of lists of expected value types,
                                     in the same order as the expected keys

    Returns:
        bool or string:  a boolean value of True if all validations pass, a
                         string with a message if a validation fails.
    """

    if type(in_dict) is not dict:
        return "Data sent with post request must be a dictionary."
    for key in expected_keys:
        if key not in in_dict.keys():
            return "{} key is not found in the input".format(key)
    for ex_type, ex_key in zip(expected_types, expected_keys):
        if type(in_dict[ex_key]) not in ex_type:

            if len(ex_type) == 2:

                return "{} key should be of type {}".format(ex_key,
                                                            "string or int")

            else:
                return f"{ex_key} key should be of type {ex_type[0].__name__}"

        if int in ex_type and type(None) in ex_type and str in ex_type:

            if not in_dict[ex_key]:
                continue

            try:
                int(in_dict[ex_key])
            except ValueError:
                return f"{ex_key} key cannot be converted into type integer"

        if int in ex_type and str in ex_type:

            try:
                int(in_dict[ex_key])
            except ValueError:
                return f"{ex_key} key cannot be converted into type integer"

        if float in ex_type and str in ex_type:

            try:
                float(in_dict[ex_key])
            except ValueError:
                return f"{ex_key} key cannot be converted into type float"

    return True


@app.route("/new_patient", methods=["POST"])
def post_new_patient():
    """
    POST route to receive a new patient

    This "/new_patient" POST route allows for a new patient to be added to the
    database on the server.  It should receive the following dictionary as a
    JSON string:
        {
            "mrn": <int containing patient medical record #>,
            "roomNum": <int that is room number of CPAP station>,
            "name": <string or None for containing patient name>
            "pressure": <string or float or none for containing patient name>
        }
    The function then sends this dictionary to a driver function to implement
    the route and receives back an answer and status code to return to the
    requestor.

    Returns:
        string: the result of the route
        int: status code of the request
    """
    # Get the data from the request
    in_dict = request.get_json()
    # Call other functions to do the work
    answer, status = new_patient_driver(in_dict)
    # Return the results
    # print(db)
    return answer, status


def new_patient_driver(in_dict):
    """
    Implements the /new_patient POST route

    This function implements the /new_patient POST route.  It receives the
    input data to the POST route as described in the function above.  It then
    calls a generic verification function and sends it the input data as well
    as tuples of expected keys and expected types.  If the verification is not
    successful, a message and 400 status code are returned to the driver
    function.  If the verification is successful, a function is called to
    add the patient to the database and a 200 status code is then returned.

    Args:
        in_dict (dict/any): the input data received by the POST request, which
                             should be a dictionary, but could be any data type

    Returns:
        string: the result of the verification if verification fails, otherwise
                a message indicating successful patient addition
        int: status code of the request: 400 if verification fails, 200 if
             patient successfully added
    """
    expected_keys = ("mrn", "roomNum", "name", "pressure")
    expected_types = ([int], [int], [str, type(None)],
                      [int, type(None), str])
    result = generic_post_route_input_verification(in_dict,
                                                   expected_keys,
                                                   expected_types)
    if result is not True:
        return result, 400
    add_patient_to_database(in_dict)
    return "Patient Added", 200


def add_patient_to_database(in_dict):
    """
    Adds a new patient record to the database

    This function receives a dictionary containing patient information and
    adds the patient information to the database.  The input dictionary
    should have the keys 'mrn', 'roomNum', and 'name'.  These three values
    are used to initialize a Patient instance to contain the record for the
    patient.  This Patient instance is then saved to the MongoDB database using
    the `.save()` method inherited from MongoModel.

    Args:
        in_dict (dict): patient information

    Returns:
        None

    """
    new_patient = Patient(mrn=in_dict["mrn"],
                          roomNum=in_dict["roomNum"],
                          name=in_dict.get("name"),
                          pressure=in_dict.get('pressure'),
                          registered_timeStamp=datetime.now())
    new_patient.save()
    return


@app.route("/calcResults", methods=["POST"])
def calcMetrics():
    """
    POST route to receive a calculate results from CPAP data

    This "/calcResults" POST route allows the CPAP data to be analyzed. It
    should receive the following dictionary as a JSON string:
        {
            "fileName": <string containing filepath of raw CPAP data>,
        }
    The function then sends this dictionary to obtainMetrics function to
    implement the route and receives back an answer and status code to return
    to the requestor.

    Returns:
        dictionary: The Metrics obtained by cpap_analyze code
        int: status code of the request
    """
    in_dict = request.get_json()
    # Call other functions to do the work
    answer, status = calc_Metrics_driver(in_dict)

    if status == 200:
        return jsonify(answer), status
    return answer, status


def calc_Metrics_driver(in_data):
    """
    Implements the /calcResults POST route

    This function implements the /calcResults POST route.  It receives the
    input data to the POST route as described in the function above.  It then
    calls a generic verification function and sends it the input data as well
    as tuples of expected keys and expected types.  If the verification is not
    successful, a message and 400 status code are returned to the driver
    function. If verification is successful, a function is called to add obtain
    the result and a 200 code is returned.

    Args:
        in_data (dict/any): the input data received by the POST request, which
                             should be a dictionary, but could be any data type

    Returns:
        dictionary: metrics retrieved from cpap analysis
        int: status code of the request: 400 if verification fails, 200 if
             metrics successfully obtained
    """
    expected_keys = ("fileName",)
    expected_types = ([str],)
    result = generic_post_route_input_verification(in_data,
                                                   expected_keys,
                                                   expected_types)
    if result is not True:
        return result, 400

    exists = os.path.exists(in_data['fileName'])

    if not exists:
        return f"{in_data['fileName']} does not exist", 400

    placeholder, result = obtainMetrics(in_data['fileName'])

    processedResult = {"breath_rate_bpm": result['breath_rate_bpm'],
                       "apnea_count": result['apnea_count'],
                       "encoded_plot": result['encoded_plot']}

    return processedResult, 200


@app.route("/add_test", methods=["POST"])
def post_add_test():
    """
    POST route for adding a test result to an existing patient

    This "/add_test" POST route accepts information on a test result for a
    patient and adds that result to the patient's record in the database.  This
    POST request should receive a JSON string containing a dictionary as
    follows:

        {
            "mrn": <int of patient mrn>,
            "breathingRate": <float containing breathing rate metric>,
            "apneaCount": <int of number of apnea events>
            "image": <string of encoded time flow plot data>
        }
    This input is sent to a driver function to implement the route and receive
    back a message and status code which are then returned to the requestor.

    Returns:
        string: the result of the route
        int: status code of the request
    """
    in_data = request.get_json()
    answer, status = add_test_driver(in_data)
    return answer, status


def add_test_driver(in_data):
    """
    Implements the /add_test POST route

    This function implements the /add_test POST route.  It receives the
    input data to the POST route as described in the function above.  It then
    calls a generic verification function and sends it the input data as well
    as tuples of expected keys and expected types.  If the verification is not
    successful, a message and 400 status code are returned to the driver
    function.  Next, a function is called to verify that the patient id
    received exists in the database.  If not, a message and 400 status code
    are returned to the driver function.  If verification is successful, a
    function is called to add the result to the patient and a 200 status code
    is then returned.

    Args:
        in_data (dict/any): the input data received by the POST request, which
                             should be a dictionary, but could be any data type

    Returns:
        string: the result of the verification if verification fails, otherwise
                a message indicating successful patient addition
        int: status code of the request: 400 if verification fails, 200 if
             test result successfully added
    """
    expected_keys = ("mrn", "breathingRate", "apneaCount", "image")
    expected_types = ([int], [float], [int], [str])
    result = generic_post_route_input_verification(in_data,
                                                   expected_keys,
                                                   expected_types)
    if result is not True:
        return result, 400

    exists = verify_patient_in_db(in_data["mrn"])
    if exists is False:
        return ("Patient mrn {} does not exist in database"
                .format(in_data["mrn"])), 400
    result, status_code = add_test_to_patient(in_data)
    return result, status_code


def verify_patient_in_db(patient_mrn):
    """
    Verifies that the given patient mrn exists in the database

    This function receives an integer containing a patient mrn and then checks
    if that patient mrn exists in the database.  It does this by querying the
    MongoDB database through the `Patient` class.  It queries the primary key
    field of the database for the patient_id within a try/except block.  If
    the patient_id does exist, the record will be successfully returned and
    no error will be raised.  The function then returns True.  But, if the
    patient_id does not exist in the database, a PyMODM custom error called
    "DoesNotExist" will be raised.  The "except" block will capture that error,
    and have the function return "False" to indicate that the patient id does
    not exist in the database.

    Args:
        patient_mrn (int): the patient id to verify is in the database

    Returns:
        bool: True if the patient exists in the database, False otherwise

    """
    try:
        db_item = Patient.objects.raw({"_id": patient_mrn}).first()
    except pymodm_errors.DoesNotExist:
        return False
    return True


def add_test_to_patient(in_data):
    """
    Add test results to a specific patient record

    This function receives a dictionary as input.  This dictionary will contain
    the "mrn" key with a value containing the id of the patient for which to
    add the test, and various CPAP test result metrics
    The "id" value is used in a MongoDB query through the "Patient" class,
    asking for the record with a primary key matching the given "mrn" value.
    This record is known to exist as the test for its existence was previously
    done.  The test results are put into a tuple that is then
    appended to the test results list of the patient entry.  The patient entry
    is then resaved to the MongoDB database using the `.save()` method.
    A message and status code of 200 are returned.

    Args:
        in_data (dict): test result for a patient

    Returns:
        string, int:  A success message and status code

    """
    patient = Patient.objects.raw({"_id": in_data["mrn"]}).first()
    newResult = CPAP_Result(timeStamp=datetime.now(),
                            breathingRate=in_data['breathingRate'],
                            apneaCount=in_data['apneaCount'],
                            flowImg=in_data['image'])

    patient.results.append(newResult)

    patient.save()
    return "Test successfully added", 200


@app.route("/updateInfo", methods=["POST"])
def post_updateInfo():
    """
    POST route for Updating Existing Patient INformation

    This "/updateInfo" POST route accepts pressure and name values to update
    information of a specific patient MRN This POST request should receive a
    JSON string containing a dictionary as follows:

        {
            "mrn": <int of patient mrn>,
            "name": <string containing the name of the patient>,
            "pressure": <int or None or String containing pressure value>
        }
    This input is sent to a driver function to implement the route and receive
    back a message and status code which are then returned to the requestor.

    Returns:
        string: the result of the route
        int: status code of the request
    """
    in_data = request.get_json()
    answer, status = updateInfo_driver(in_data)
    return answer, status


def updateInfo_driver(in_data):
    """
    Implements the /updateInfo POST route

    This function implements the /calcResults POST route.  It receives the
    input data to the POST route as described in the function above.  It then
    calls a generic verification function and sends it the input data as well
    as tuples of expected keys and expected types.  If the verification is not
    successful, a message and 400 status code are returned to the driver
    function. If verification is successful, a function is called to add obtain
    the result and a 200 code is returned.

    Args:
        in_data (dict/any): the input data received by the POST request, which
                             should be a dictionary, but could be any data type

    Returns:
        string: the result of the verification if verification fails, otherwise
            a message indicating successful patient info update
        int: status code of the request: 400 if verification fails, 200 if
             metrics successfully obtained
    """
    expected_keys = ("mrn", "name", "pressure")
    expected_types = ([int], [str, type(None)], [str, type(None), int])
    result = generic_post_route_input_verification(in_data,
                                                   expected_keys,
                                                   expected_types)

    if result is not True:
        return result, 400

    exists = verify_patient_in_db(in_data["mrn"])
    if exists is False:
        return ("Patient mrn {} does not exist in database"
                .format(in_data["mrn"])), 400

    result, status = updateInfo(in_data)

    return result, 200


def updateInfo(in_data):
    """
    Update Information of specific patient MRN

    This function receives a dictionary as input.  This dictionary will contain
    the "id" key with a value containing the mrn of the patient for which to
    update information, the "pressure" key with a int value with the new
    updated pressure, and the "name" key with the updated name string.
    The "id" value is used in a MongoDB query through the "Patient" class,
    asking for the record with a primary key matching the given "mrn" value.
    This record is known to exist as the test for its existence was previously
    done.  The test name and test results are put into a tuple that is then
    appended to the test results list of the patient entry.  The patient entry
    is then resaved to the MongoDB database using the `.save()` method.
    A message and status code of 200 are returned.

    Args:
        in_data (dict): test result for a patient

    Returns:
        string, int:  A success message and status code

    """

    patient = Patient.objects.raw({"_id": in_data["mrn"]}).first()

    patient.pressure = in_data["pressure"]
    patient.name = in_data.get("name")

    patient.save()
    return f"Patient MRN {in_data['mrn']} Succesfully Updated", 200


def clear_db():
    """
    Resets Entire Database

    This function deletes all the Patient objects in the database

    Args:
        None

    Returns:
        None
    """
    x = Patient.objects.all()

    x.delete()


def initializeDB():
    """
    Populates Database with Dummy Data

    This function populates the Mongo Database with dummy patient data and
    CPAP results

    Args:
        None

    Returns:
        None
    """
    clear_db()

    p1 = {"mrn": 1030324,
          "roomNum": 32,
          "name": "Becky",
          "pressure": 233}
    p2 = {"mrn": 1004234,
          "roomNum": 3,
          "name": "Sid",
          "pressure": 453}
    p3 = {"mrn": 103404343,
          "roomNum": 3,
          "name": "Jimmy",
          "pressure": 112}
    p4 = {"mrn": 13042342,
          "roomNum": 9,
          "name": "James",
          "pressure": 142}
    add_patient_to_database(p1)
    add_patient_to_database(p2)
    add_patient_to_database(p3)
    add_patient_to_database(p4)

    result1 = {"mrn": 1030324, "breathingRate": 27.3, "apneaCount": 8,
               "image": "lkhlkjhlkj"}
    result2 = {"mrn": 1030324, "breathingRate": 22.3, "apneaCount": 2,
               "image": "fdafa"}
    result3 = {"mrn": 13042342, "breathingRate": 29.3, "apneaCount": 0,
               "image": "fdasadffa"}

    add_test_to_patient(result1)
    add_test_to_patient(result2)
    add_test_to_patient(result3)


@app.route("/room_nums", methods=["GET"])
def get_used_rooms():
    return get_used_rooms_driver()


def get_used_rooms_driver():
    """
    Get all room numbers that have been/are used by patients

    This function receives all the room numbers present in the list of pts in
    the MongoDB. This is done by first getting all the patients in the database
    and appending only the roomNum fields into a list called 'rooms'. This list
    is then condensed by removing duplicates. This is done by converting to a
    dictionary, which cannot have duplicate keys, and then converting back to
    a string.

    Args:
        None

    Returns:
        tuple, int: all room numbers
    """
    rooms = []
    patientdb = Patient.objects.raw({})
    for item in patientdb:
        rooms.append(int(item.roomNum))
    rooms_condensed = list(dict.fromkeys(rooms))
    return rooms_condensed


@app.route("/pt_info_fromRoom/<roomNum>", methods=["GET"])
def get_infofromroom(roomNum):
    patient_info_dict = get_infofromroom_driver(int(roomNum))
    return patient_info_dict


def get_infofromroom_driver(roomNum):
    """
    Get the most recent patient information from a Room Number

    This function takes a room number that the user selected as an input
    and returns all the information needed from the most recent pt in a
    dictionary format caleld ptinfo. This includes patient mrn, name, time of
    the latest test, breathing rate, apnea count, and an ecoded image string.

    Args:
        int: Room Number
    Returns:
        dict: dictionary of all the relevant patient values
    """
    rs = "registered_timeStamp"
    pt = Patient.objects.raw({"roomNum": roomNum}).order_by([(rs, -1)]).first()
    ptMRN = pt.mrn
    ptName = pt.name
    ptPressure = pt.pressure
    if do_results_exist(ptMRN) is True:
        ptResults = pt.results
        ResultRecent = ptResults[-1]
        test_time = ResultRecent.timeStamp
        test_breathingrate = ResultRecent.breathingRate
        test_apneas = ResultRecent.apneaCount
        ImageText = ResultRecent.flowImg
    elif do_results_exist(ptMRN) is False:
        test_time = "N/A"
        test_breathingrate = "N/A"
        test_apneas = "N/A"
        ImageText = "N/A"
    ptinfo = {"mrn": ptMRN,
              "name": ptName,
              "p": ptPressure,
              "time": test_time,
              "br": test_breathingrate,
              "ac": test_apneas,
              "img": ImageText}
    return ptinfo


def do_results_exist(mrn):
    """
    This function checks whether the patient has results

    The function returns True if able to index a test result using basic try
    except methodology. The function returns False if there is an IndexError.

    Args:
        int: Medical Record Number
    Returns:
        bool: True or False
    """
    pt = Patient.objects.raw({"_id": mrn}).first()
    try:
        ptResults = pt.results
        ResultRecent = ptResults[-1]
        return True
    except IndexError:
        return False


@app.route("/pressure_query/<mrn>", methods=["GET"])
def get_pressure_from_mrn(mrn):
    """
    GET route for retrieving pressure information of a patient by MRN

    This route accepts a patient's Medical Record Number (MRN) as a parameter
    and returns the patient's pressure information if the patient exists in
    the database. If the patient does not exist, a 400 status code and an error
    message are returned.

    Args:
        mrn (str): Medical Record Number of the patient

    Returns:
        string: pressure information of the patient
        int: status code of the request: 400 if the patient does not exist, 200
             if pressure information is successfully obtained
    """
    mrn = int(mrn)
    answer, status = get_pressure_from_mrn_driver(mrn)
    return answer, status


def get_pressure_from_mrn_driver(mrn):
    """
    Retrieve pressure information of a patient based on MRN

    This function checks if a patient with the given MRN exists in the
    database. If the patient exists, it retrieves the pressure information
    for the patient. If the patient does not exist, a 400 status code and
    an error message are returned.

    Args:
        mrn (int): Medical Record Number of the patient

    Returns:
        string: pressure information of the patient, or error if pt does not
                exist in the DB
        int: status code of the request: 400 if the patient does not exist, 200
             if pressure information is successfully obtained
    """
    exists = verify_patient_in_db(mrn)
    if exists is False:
        return ("Patient mrn {} does not exist in database"
                .format(mrn)), 400

    pressure = get_pressure_val(mrn)
    return pressure, 200


def get_pressure_val(mrn):
    """
    Retrieve pressure value of a patient from the database

    This function queries the database to retrieve the pressure value of a
    patient with the given MRN.

    Args:
        mrn (int): Medical Record Number of the patient

    Returns:
        string: pressure value of the patient
    """
    pt = Patient.objects.raw({"_id": mrn}).first()
    pressure = str(pt.pressure)
    return pressure


@app.route("/old_test_dates/<mrn>", methods=["GET"])
def get_test_dates(mrn):
    """
    Get a list of previous test dates for a patient identified by their MRN
    (Medical Record Number).

    This route retrieves the patient with the specified MRN from the MongoDB.
    It then extracts the timestamp information for all the previous test
    results associated with the patient, excluding the most recent one. The
    extracted test dates are returned as a list.

    Args:
        mrn (int): The Medical Record Number of the patient.

    Returns:
        tuple: A tuple containing a list of previous test dates and status code
    """
    mrn = int(mrn)
    prev_tests = get_test_dates_driver(mrn)
    return prev_tests


def get_test_dates_driver(mrn):
    """
    Get a list of previous test dates for a patient identified by their MRN
    (Medical Record Number).

    This driver retrieves the patient with the specified MRN from the MongoDB.
    It then extracts the timestamp information for all the previous test
    results associated with the patient, excluding the most recent one. The
    extracted test dates are returned as a list.

    Args:
        mrn (int): The Medical Record Number of the patient.

    Returns:
        tuple: A tuple containing a list of previous test dates and status code
    """
    prev_tests_list = []
    pt = Patient.objects.raw({"_id": mrn}).first()
    ptResults = pt.results
    if len(ptResults) == 1:
        return prev_tests_list
    oldResults = ptResults[:-1]  # Ignore most recent test
    for items in oldResults:
        prev_tests_list.append(items.timeStamp)
    return (prev_tests_list)


@app.route("/get_old_img/<mrn>/<dateval>", methods=["GET"])
def get_old_img(mrn, dateval):
    """
    GET route for retrieving the image of a patient's old test by MRN and date

    Calls driver function below

    Returns:
        string: image associated with the specified date for the given patient
    """
    return get_old_img_driver(mrn, dateval)


def get_old_img_driver(mrn, dateval):
    """
    Receive Image of old test driver function

    This route accepts a patient's Medical Record Number (MRN) and the date of
    the old test as parameters. It retrieves and returns the image associated
    with the specified date for the given patient if a match is found in the
    database. If no match is found, a 404 status code and an error message are
    returned.

    Args:
        mrn (str): Medical Record Number of the patient
        dateval (str): Date of the old test in the format 'Wed, 06 Dec 2023
                       22:28:27 GMT'

    Returns:
        string: image associated with the specified date for the given patient
    """
    mrn = int(mrn)
    print("dateval:", dateval)
    pt = Patient.objects.raw({"_id": mrn}).first()
    ptResults = pt.results

    for items in ptResults:
        idate = datetime.strptime(str(items.timeStamp), '%Y-%m-%d %H:%M:%S.%f')
        odate = idate.strftime('%a, %d %b %Y %H:%M:%S GMT')
        print("odate:", odate)
        if odate == dateval:
            return items.flowImg

    print("No match found for date:", dateval)
    return "No matching image found for the given date."


if __name__ == "__main__":

    app.run(host="0.0.0.0")
