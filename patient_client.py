import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import glob
import requests
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from cpap_analyze import obtainMetrics
from tkinter import filedialog
import os
from gui_helperFuncs import dangerApnea, decodeImg, valPressureInput

# server = "http://127.0.0.1:5000"
server = "http://vcm-35156.vm.duke.edu:5000"

imageSize = (475, 350)


def calcHealthMetrics(filename):
    """
    Calculate CPAP Metrics given a filename/

    This function processes a CPAP data file to obtain metrics and an image of
    flow vs. time plot

    Args:
        filename (str): The path to the file containing relevant data.

    Returns:
        tuple: A tuple containing:
            - breath_rate_bpm (float): The breathing rate in breaths per
            minute.
            - apnea_count (int): The count of apnea occurrences.
            - encoded_plot (str): The encoded plot of health metrics.
    """
    placeholder, r = obtainMetrics(filename)

    return r['breath_rate_bpm'], r['apnea_count'], r['encoded_plot']


def registerPatient(out_dict):
    """
    Register a new patient with the provided information.

    This function registers a new patient to the Mongo DB.
    Calls /new_patient POST request

    Args:
        out_dict (dict): A dictionary containing patient information including:
            - 'mrn' (int): Medical Record Number.
            - 'roomNum' (int): Room number.
            - 'name' (str/ None): Patient's name.
            - 'pressure' (int/ None): Pressure information.

    Returns:
        None
    """
    r = requests.post(server + "/new_patient", json=out_dict)

    print(r.text, r.status_code)


def addResult(out_dict):
    """
    Add test results using the provided dictionary.

    This function adds test results to the system.
    Calls /add_test POST request

    Args:
        out_dict (dict): A dictionary containing test result information
        including:
            - 'mrn' (int): Medical Record Number.
            - 'breathingRate' (float): Breathing rate.
            - 'apneaCount' (int): Apnea count.
            - 'image' (str): Encoded image of the test.

    Returns:
        None
    """
    r = requests.post(server + "/add_test", json=out_dict)

    print(r.text, r.status_code)


def updateInfo(out_dict):
    """
    Update patient name and pressure with following dictionary.

    This function updates patient information in the Mongo Database.
    Calls /updateInfo POST Route

    Args:
        out_dict (dict): A dictionary containing updated patient
        information including:
            - 'mrn' (int): Medical Record Number.
            - 'name' (str/ None): Updated patient name.
            - 'pressure' (int/ None): Updated pressure information.

    Returns:
        None
    """
    r = requests.post(server + "/updateInfo", json=out_dict)

    print(r.text, r.status_code)


def getPressure(mrn):
    """
    Get pressure value for a given patient's MRN.

    This function retrieves pressure information for a specific patient via a
    /pressure_query/<mrn> GET Request

    Args:
        mrn (int): Patient's Medical Record Number (MRN).

    Returns:
        str: Pressure information.
    """

    r = requests.get(server + f"/pressure_query/{mrn}")

    return r.text


fullDataFilePath = ""
encodedImageGlobal = ""
postBool = False


def main_window():
    """
    Patient GUI Main Window Function

    Sets up GUI layout with buttons, labels, and image placeholder. COntains
    GUI specific functions and commands.

    """
    root = tk.Tk()

    # Create a centered title label using grid
    title_label = ttk.Label(root,
                            text="Patient Client Station",
                            font=("Helvetica", 20))
    title_label.grid(row=0, column=0, columnspan=3, pady=(20, 10))

    # Create labels for content headers

    patient_mrn_label = ttk.Label(root, text="Patient MRN:")
    patient_mrn_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

    patient_name_label = ttk.Label(root, text="Patient Name:")
    patient_name_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)

    room_num_label = ttk.Label(root, text="Room Number:")
    room_num_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.E)

    pressure_label = ttk.Label(root, text="Pressure (cmH2O):")
    pressure_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)

    breath_label_text = "Breathing Rate (Breaths/ Minute):"
    breathing_rate_label = ttk.Label(root, text=breath_label_text,
                                     wraplength=110)
    breathing_rate_label.grid(row=9, column=0, padx=10, pady=5, sticky=tk.E)

    apnea_count_label = ttk.Label(root, text="Apnea Count:")
    apnea_count_label.grid(row=10, column=0, padx=10, pady=5, sticky=tk.E)

    # Create String Entry Boxes

    mrn_value = tk.StringVar()
    mrn_entry = ttk.Entry(root, width=10, textvariable=mrn_value)
    mrn_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

    name_value = tk.StringVar()
    name_entry = ttk.Entry(root, width=10, textvariable=name_value)
    name_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    roomNum_value = tk.StringVar()
    room_entry = ttk.Entry(root, width=10, textvariable=roomNum_value)
    room_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

    pressure_value = tk.StringVar()

    def pressureQueryResponse():
        """
        Continuously queries and updates pressure information for the patient.

        This function periodically retrieves pressure information for the
        patient based on the MRN (Medical Record Number) value. It checks the
        state of the register_button, and if it's disabled, it updates the
        pressure information by calling 'getPressure' using the MRN value from
        the entry box. After updating the pressure, it triggers the
        'updateInfo_gui' function. Process occurs every 30 seconds

        Returns:
        None
        """
        if str(register_button.cget('state')) == "disabled":

            pressure_value.set(getPressure(mrn_value.get()))

            updateInfo_gui()

        root.after(30000, pressureQueryResponse)

    pressure_entry = ttk.Entry(root, width=10, textvariable=pressure_value)
    pressure_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

    file_var = tk.StringVar()
    fileName_display = ttk.Label(root, textvariable=file_var)
    fileName_display.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

    pressure_var = tk.StringVar()
    pressure_display = ttk.Label(root, textvariable=pressure_var)
    pressure_display.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)

    breathing_rate_var = tk.StringVar()
    breathing_rate_display = ttk.Label(root, textvariable=breathing_rate_var)
    breathing_rate_display.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)

    def update_apnea_label_color(apneaCount):
        """
        Changes color of apnea count display text based on apena count value

        If the Apnea count is deemed dangerous by dangerApnea() function,
        the display foreground is set to red and black if otherwise.

        Returns:
        None
        """

        if dangerApnea(apneaCount):
            apnea_count_display.configure(foreground='red')
        else:
            apnea_count_display.configure(foreground=default_foreground_color)

    apnea_count_var = tk.StringVar()
    apnea_count_display = ttk.Label(root, textvariable=apnea_count_var)
    apnea_count_display.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)
    default_foreground_color = apnea_count_display.cget('foreground')

    # Allow User to Select File for Analysis
    def browseFiles():
        """
        Open a file dialog to select and process a file.

        This function opens a file dialog window allowing the user to select a
        file. If a file is selected, it updates the global variable
        'fullDataFilePath' with the selected file's path.
        It then extracts the filename, updates the label to display the
        shortened filename, and enables the 'Calculate Metrics' button.

        Returns:
        None
        """
        global fullDataFilePath
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select a File",
                                              filetypes=(("Text files",
                                                          "*.txt"),
                                                         ("All files", "*.*")))
        # Change label contents

        if filename:

            fullDataFilePath = filename
            filename_short = os.path.basename(filename)
            file_var.set(filename_short)
            calculate_button.config(state=tk.NORMAL)

    # Create Image with Label
    plot_label = ttk.Label(root,
                           text="CPAP Data Image:",
                           font=("Helvetica", 15))
    plot_label.grid(row=6, column=0, columnspan=3, pady=(20, 10))
    image_label = ttk.Label(root)

    image_label.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    # Display patient information based on the selected room
    def calcResultsGui():
        """
        Calculate CPAP metrics and update the GUI with the results.

        This function computes health metrics based on the data in
        'fullDataFilePath' by calling the 'calcHealthMetrics' function. It then
        displays the obtained metrics. Additionally, it manages the state of
        the 'post_result_button' based on the 'postBool' bool. True -> Enable,
        else Disable

        Returns:
        None
        """
        global fullDataFilePath
        global postBool

        display_results(*calcHealthMetrics(fullDataFilePath))

        if postBool:
            post_result_button.config(state=tk.NORMAL)
        else:
            post_result_button.config(state=tk.DISABLED)

    def display_results(breathing_rate, apnea_count, encodedImg):
        """
        Update the GUI with CPAP metrics and imapge.

        This function updates the GUI elements to display health metrics and an
        associated image.

        Args:
            breathing_rate (float): The breathing rate in breaths per minute.
            apnea_count (int): The count of apnea occurrences.
            encodedImg (str): The encoded image representing health metrics.

        Returns:
            None
        """
        global encodedImageGlobal
        breathing_rate_var.set(round(breathing_rate, 2))

        update_apnea_label_color(apnea_count)
        apnea_count_var.set(apnea_count)

        encodedImageGlobal = encodedImg

        buffer = decodeImg(encodedImg)

        image_obj = Image.open(buffer)

        image_obj.thumbnail(imageSize)

        photo_image = ImageTk.PhotoImage(image_obj)
        image_label.config(image=photo_image)
        image_label.image = photo_image

    def clear_patient_info():
        """
        Clear GUI and Reset Fields

        Function resets global variables, button states, and fields. To start
        new CPAP workflow

        Returns:
            None
        """
        # Clear entry fields
        mrn_value.set("")
        name_value.set("")
        roomNum_value.set("")
        pressure_value.set("")

        # Reset display labels
        file_var.set("")
        pressure_var.set("")
        breathing_rate_var.set("")
        apnea_count_var.set("")

        # Reset Button States
        calculate_button.config(state=tk.DISABLED)
        update_button.config(state=tk.DISABLED)
        register_button.config(state=tk.NORMAL)
        post_result_button.config(state=tk.DISABLED)

        # Reset Image Box
        image_label.config(image=None)
        image_label.image = None

        # Reset Entry Box States

        mrn_entry.config(state="enabled")
        room_entry.config(state="enabled")

        # Reset Global Variable

        global fullDataFilePath
        global encodedImageGlobal
        global postBool

        fullDataFilePath = ""
        encodedImageGlobal = ""
        postBool = False

    def registerNewPatient_gui():
        """
        Register a new patient Function for Button.

        Retrieves mrn, roomNum, names, pressure field entry. The pressure is
        validated and if validation fails an error message is thrown. Else the
        function calls the registerPatient() function to update Database. After
        this action is done the mrn and room number are locked and updates
        postBool global variable to represent viability of post_result
        functionality.

        Returns:
            None
        """
        global postBool

        if not valPressureInput(pressure_value.get()):

            pressureErrorMsg()
            return

        out_dict = {"mrn": int(mrn_value.get()),
                    "roomNum": int(roomNum_value.get()),
                    "name": name_value.get(),
                    "pressure": pressure_value.get()}

        registerPatient(out_dict)

        register_button.config(state=tk.DISABLED)

        mrn_entry.config(state="disabled")
        room_entry.config(state="disabled")

        update_button.config(state=tk.NORMAL)

        if pressure_value.get():
            postBool = True
        else:
            postBool = False

    def addResult_gui():
        """
        Register a new test for an Existing patient button funcionality.

        Retrieves mrn, breathingRate, apneaCount, image field entries and calls
        the addResult() function to update Database.

        Returns:
            None
        """
        global encodedImageGlobal

        obtainedRate = float(breathing_rate_var.get())

        out_dict = {"mrn": int(mrn_value.get()),
                    "breathingRate": obtainedRate,
                    "apneaCount": int(apnea_count_var.get()),
                    "image": encodedImageGlobal}

        addResult(out_dict)

    def updateInfo_gui():
        """
        Update Pressure and Name for Existing patient button functionality.

        Retrieves mrn, breathingRate, name, and pressure fields. Validates
        pressure value, if failure, error message is throwin. Else the
        function calls the updateInfo() function and update postBool boolean to
        represent posting result viability.

        Returns:
            None
        """

        global postBool

        if not valPressureInput(pressure_value.get()):

            pressureErrorMsg()
            return

        out_dict = {"mrn": int(mrn_value.get()),
                    "name": name_value.get(),
                    "pressure": pressure_value.get()}

        updateInfo(out_dict)

        if pressure_value.get():
            postBool = True
        else:
            postBool = False
            post_result_button.config(state=tk.DISABLED)

    def pressureErrorMsg():
        """
        Display an error message for pressure validation

        This function displays an error message  if the
        entered pressure value is invalid Additionally, it clears the
        'pressure_value' entry if an error occurs.

        Returns:
            None
        """

        msg = "Pressure Must be an Integer between 4 and 25 Inclusive"

        tk.messagebox.showerror(title="Pressure Validation Error",
                                message=msg)

        pressure_value.set("")

    # Setup Buttons

    register_button = ttk.Button(root,
                                 text="Register Patient",
                                 command=registerNewPatient_gui)
    register_button.grid(row=1, column=2, columnspan=1, pady=10)

    update_button = ttk.Button(root,
                               text="Update Information",
                               command=updateInfo_gui,
                               state=tk.DISABLED)
    update_button.grid(row=2, column=2, columnspan=1, pady=10)

    fileExplorer = ttk.Button(root,
                              text="Browse Files",
                              command=browseFiles)
    fileExplorer.grid(row=5, column=0, padx=10, pady=10, sticky=tk.E)

    calculate_button = ttk.Button(root,
                                  text="Calculate Metrics",
                                  command=calcResultsGui,
                                  state=tk.DISABLED)
    calculate_button.grid(row=5, column=2, columnspan=1, pady=10)

    post_result_button = ttk.Button(root,
                                    text="Post Result",
                                    command=addResult_gui,
                                    state=tk.DISABLED)
    post_result_button.grid(row=9, column=2, pady=10, sticky=tk.E)

    clear_button = ttk.Button(root,
                              text="Clear Interface",
                              command=clear_patient_info,
                              width=20)
    clear_button.grid(row=11, column=0, pady=10, columnspan=3)

    pressureQueryResponse()
    root.mainloop()


if __name__ == "__main__":
    main_window()
