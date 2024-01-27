import requests

server = "http://127.0.0.1:5000"

# out_dict = {"mrn": 2,
#             "roomNum": 15,
#             "name": "Pradnesh",
#             "pressure": 3}

# r = requests.post(server + "/new_patient", json=out_dict)
# print(r.text)
# print(r.status_code)

# out_dict = {"fileName": "patient_01.txt"}
# r = requests.post(server + "/calcResults", json=out_dict)
# print(r.text)
# print(r.json()['breath_rate_bpm'])
# print(r.status_code)ti

# out_dict = {"mrn": 2,
#             "breathingRate": 22.3,
#             "apneaCount": 2}

# r = requests.post(server + "/add_test", json=out_dict)
# print(r.text)
# print(r.status_code)

# r = requests.get(server + "/room_nums")
# print(r.text)
# print(r.status_code)

# out_dict = {"mrn": 2,
#             "roomNum": 3,
#             "name": "Pradnesh",
#             "pressure": 3.0}

# r = requests.post(server + "/new_patient", json=out_dict)
# print(r.text)
# print(r.status_code)

# r = requests.get(server + "/pt_info_fromRoom/32")
# print(r.text)
# print(r.status_code)

# r = requests.get(server + "/pressure_query/1304")
# print(r.text)
# print(r.status_code)

# r = requests.get(server + "/old_test_dates/1234")
# print(r.text)
# print(r.status_code)


out_dict = {"mrn": 3,
            "name": "vineeth",
            "pressure": 3}

r = requests.post(server + "/updateInfo", json=out_dict)
