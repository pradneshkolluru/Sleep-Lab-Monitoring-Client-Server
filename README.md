# **Sleep Lab Monitoring System Final Project**
*Developed by Pradnesh Kolluru & Ashwin Gadiraju* | *Contact: pck14@duke.edu, avg13@duke.edu*


## Introduction

Thank you for choosing the Onion-Bobington-Win Sleep Lab Monitoring System! This repository contains the codebase for a comprehensive solution designed and implemented as the final project for our class. The system encompasses a patient-side graphical user interface (GUI) client, a monitoring-station GUI client, and a server/database infrastructure. Together, they facilitate the monitoring of patients undergoing sleep studies, allowing seamless communication, data storage, and analysis.

Final Video Link: https://www.youtube.com/watch?v=GdfcSTCFuxA&t=3s

## Features & Conventions

#### Patient-side GUI Client

The patient-side GUI serves as a representation of a CPAP machine, tracking a patient's sleep study. Key features include:

- Patient information entry, including name, medical record number (MRN), and room number.
- Input validation for CPAP pressure, ensuring it falls within the typical range of 4 to 25 cmH2O.
- Analysis of CPAP data, displaying breathing rate, apnea count, and a flow rate vs. time curve.
- RESTful API requests to upload patient information and data to the server.
- Periodic querying of the server for updated CPAP pressure commands.
- Ability to update patient information and send new data to the server.
- Reset functionality to clear entries and prepare the GUI for a new patient.

#### Monitoring-Station GUI Client

The monitoring-station GUI acts as a central hub for sleep lab technicians to monitor CPAP results and manage patient information. Its features include:

- Selection of room numbers to view corresponding patient details.
- Display of the most recent CPAP pressure, breathing rate, apnea count, and flow image for the selected patient.
- Retrieval and display of historical CPAP calculated data.
- Saving downloaded CPAP flow images locally.
- Updating CPAP pressure for a selected patient and uploading it to the server.
- Dynamic updating of information and options based on server updates.
- Periodic requests to the server for the latest information.

#### Development Conventions

Throughout the development of this project, industry-standard practices and conventions were followed, including:

- Git feature-branch workflow for collaborative development.
- Integration of continuous integration for automated testing.
- Implementation of unit tests, adhering to PEP8 standards.
- Documentation through docstrings for clear code understanding.
- Utilization of issues and milestones to track development progress.

## Usage Instructions

### <u>**Prerequisites**</u>

##### - Virtual Environment
   - The GUI is implemented in Python and requires the installation of the necessary libraries. create a new virtual environment in the folder titled 'venv' and install the necessary modules by entering the following in a new line:
     ```bash
     pip3 install -r requirements.txt
     ```

##### - Virtual Machine
   - URL for Deployed Web Server: `http://vcm-35156.vm.duke.edu:5000 `


### <u>**CPAP Patient GUI Usage Instructions**</u>

#### Overview

- The CPAP Patient GUI serves as an interface for patients undergoing sleep studies. It allows users to input their information, analyze CPAP data, and interact with the server for data upload and updates.

#### Running the GUI

1. Execute the Script
   - Open a terminal or command prompt.
   - Navigate to the directory containing the patient GUI script (`patient_client.py`).
   - Run the script using the following command:
     ```bash
     python3 patient_client.py
     ```

2. **GUI Interface**
   - Upon running the script, the GUI window titled "Patient Client Station" will appear.

3. **Input Patient Information**
   - Enter the required information, including medical record number (int) and room number (int)
   - Name(str) and and CPAP pressure (int) are optional

4. **Register New Patient**
   - Click the "Register Patient" button to register a new patient with the entered information.
   - Once registered, the MRN and room number fields will be disabled, and the "Update" button will be enabled.

5. **Browse and Analyze CPAP Data**
   - Click the "Browse Files" button to select a CPAP data file for analysis. Supported file formats include ".txt".
   - After selecting a file, click the "Calculate Metrics" button to analyze the data and display metrics.
   - The calculated metrics include breathing rate, apnea count, and a flow rate vs. time plot.

6. **Update Patient Information**
   - If needed, click the "Update Information" button to update patient information, including name and pressure.
   - The "Post Result" button will be enabled if pressure information is available; otherwise, it will be disabled.

7. **Calculate and Post Test Results**
   - After analyzing the CPAP data, the "Post Result" button becomes available.
   - Click this button to post test results, including breathing rate, apnea count, and the associated image, to the server.

8. **Clear Interface**
   - Click the "Clear Interface" button to reset the GUI, allowing the entry of information for a new patient.


### <u>**CPAP Monitoring Station GUI Usage Instructions**</u>

#### <u>Overview</u>

- The CPAP Monitoring Station GUI is designed to provide sleep lab technicians with a user-friendly interface for monitoring and managing CPAP (Continuous Positive Airway Pressure) data for patients. The GUI allows technicians to view and interact with patient information, historical test data, and make updates to the CPAP pressure settings.

#### <u>Running the GUI</u>

1. **Execute the Script**
   - Open a terminal or command prompt.
   - Navigate to the directory containing the monitoring station script (`monitoring_station_client.py`).
   - Run the script using the following command:
     ```bash
     python3 monitoring_station_client.py
     ```
2. **GUI Interface**
   - Upon running the script, the GUI window titled "CPAP Monitoring Station" will appear.

3. **Select Patient Room**
   - Use the "Patient Room #" dropdown menu to select the room number for the patient you want to monitor. This is a list of all the room numbers that have ever been added to the database, and the resultant data will show the patient that has most recently been assigned a specified room number.

4. **View Patient Information**
   - Click the "Show Records" button to display the most recent CPAP data for the selected patient. Optionaly, you can simply wait ~5 seconds and the data should automatically populate
   - Patient information, including name, medical record number (MRN), pressure, breathing rate, apnea count, and the most recent CPAP data image, will be displayed on the left side of the GUI.
   - Note: If there is no result, the results will simply say N/A for the values that do not exist

5. **Historical Test Data**
   - If available, you can select a historical test date from the "Old Test Date" dropdown menu to view historical CPAP data. These are the dates of all the tests associated with the selected patient
   - Click the "Show Old Data Plot" button to display the historical CPAP data image.
   - Note: This value may be grayed out or unavailable if there is only one test or no results exist for the chosen patient.

6. **Download Images**
   - Use the "Download Image" buttons beneath the plots to download the currently displayed images (Image 1 and Image 2) as .PNG files. This will require you to enter a name and desired filepath for the data to be stored. 
   Click 'Save' in the box that appears to download the image. 

7. **Update CPAP Pressure**
   - Enter a new CPAP pressure value in the "Input Pressure" field.
   - Click the "Upload Pressure" button to update the CPAP pressure for the selected patient.
   - This value should be between 4 and 25 and must be an integer.
   - If a prohibited value is inputted, a label will appear beneath the textbox in either red or green text indicating this.

For any issues or questions with this monitoring gui, refer to the provided documentation or contact the system administrator.

## **License Information**

MIT License

Copyright (c) 2023 Pradnesh Kolluru, Ashwin Gadiraju

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.