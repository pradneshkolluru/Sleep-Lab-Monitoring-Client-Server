import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import glob
import requests
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from cpap_analyze import obtainMetrics
from tkinter import filedialog
import os
import ast
import json
from gui_helperFuncs import decodeImg, dangerApnea, valPressureInput


# server = "http://127.0.0.1:5000"
server = "http://vcm-35156.vm.duke.edu:5000"
imageSize = (475, 350)
current_mrn = ""


def get_roomlist():
    """
    Retrieves the list of available room numbers from the server.

    This function simply calls the /room_nums get route to return a tuple of
    the available room numbers without duplicates

    Returns:
        tuple: available room numbers.
    """
    roomnum_list = requests.get(server + "/room_nums")
    return ast.literal_eval(roomnum_list.text)


def get_oldtests(mrn):
    """
    Retrieves the list of old test dates for a patient MRN from the server.

    This function simply calls the /old_test_dates get route to return the test
    dates that aren't the most recent. It then evaluates these test dates as a
    tuple and uses the ast.literal_eval to format these dates in a easy-to-read
    way

    Args:
        mrn (int): Patient MRN (Medical Record Number).

    Returns:
        tuple: Tuple containing old test dates.
    """
    oldtests_list = requests.get(server + "/old_test_dates/" + str(mrn))
    return tuple(ast.literal_eval(oldtests_list.text))


def get_oldimg(mrn, dateval):
    """
    Get Old Image Function

    Retrieves the encoded image text for a historical test for a given patient
    MRN and date from the server. inputs the mrn and dateval provided from the
    text label field and dropdown to send to the /get_old_img/ route

    Args:
        mrn (str): Patient MRN (Medical Record Number).
        dateval (str): Date value of the historical test.

    Returns:
        str: Encoded image text.
    """
    oldimg_text = requests.get(server + "/get_old_img/" + mrn + "/" + dateval)
    return oldimg_text.text


def get_patient_info(roomNum):
    """
    Retrieves patient information for a given room number from the server.

    This function simply takes in a room number and returns a list of all the
    necessary information and test results (most recent) to be displayed on the
    left side of the gui. These results include patient MRN, name, pressure,
    test time, breathing rate, apnea count, and encoded image text

    Args:
        roomNum (int): Room number.

    Returns:
        tuple: Tuple containing necessary patient information from most recent
        test
    """
    pt = requests.get(server + "/pt_info_fromRoom/" + str(roomNum))
    pt = ast.literal_eval(pt.text)
    mrn = pt['mrn']
    name = pt['name']
    press = pt['p']  # Pressure
    t = pt['time']  # Test Time
    br = pt['br']  # Breathing Rate
    ac = pt['ac']  # Apnea Count
    img = pt['img']  # Encoded Image Text
    return mrn, name, press, t, br, ac, img


def updateInfo(out_dict):
    """
    Updates patient information on the server.

    This function simply calls the updateinfo post route to send a pressure
    value to the server. This route is the same route used by the patient
    client

    Args:
        out_dict (dict): Dictionary containing updated patient information.
    """
    r = requests.post(server + "/updateInfo", json=out_dict)
    print(r.text, r.status_code)


def main_window():
    root = tk.Tk()

    # Title
    title_label = ttk.Label(root, text="CPAP Monitoring Station",
                            font=("Helvetica", 20, "bold"))
    title_label.grid(row=0, column=0, columnspan=9, pady=(20, 10))

    # Patient Room Dropdown
    room_label = ttk.Label(root, text="Patient Room #:")
    room_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

    room_var = tk.IntVar()
    room_dropdown = ttk.Combobox(root, textvariable=room_var,
                                 values=get_roomlist())
    room_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

    # Historic Test Dropdown
    choose_hist_label = ttk.Label(root, text="Old Test Date:")
    choose_hist_label.grid(row=3, column=3, padx=10, pady=10, sticky=tk.E)

    historic_var = tk.StringVar()
    historic_dropdown = ttk.Combobox(root, textvariable=historic_var)
    historic_dropdown.grid(row=3, column=4, padx=10, pady=10, sticky=tk.W)

    # Labels (Patient Information)
    patient_name_label = ttk.Label(root, text="Patient Name:")
    patient_name_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)

    patient_mrn_label = ttk.Label(root, text="Patient MRN:")
    patient_mrn_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)

    # Labels (CPAP Information)
    pressure_label = ttk.Label(root, text="Pressure:")
    pressure_label.grid(row=7, column=0, padx=10, pady=5, sticky=tk.E)

    breathing_rate_label = ttk.Label(root, text="Breathing Rate:")
    breathing_rate_label.grid(row=8, column=0, padx=10, pady=5, sticky=tk.E)

    apnea_count_label = ttk.Label(root, text="Apnea Count:")
    apnea_count_label.grid(row=9, column=0, padx=10, pady=5, sticky=tk.E)

    test_time_label = ttk.Label(root, text="Date Uploaded:")
    test_time_label.grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)

    add_pressure_label = ttk.Label(root, text="Input Pressure:")
    add_pressure_label.grid(row=9, column=3, padx=10, pady=5, sticky=tk.E)

    # Pressure entry box
    pressure_value_var = tk.StringVar()
    pressure_entry = ttk.Entry(root, width=10, textvariable=pressure_value_var)
    pressure_entry.grid(row=9, column=4, padx=30, pady=5, sticky=tk.W)

    # Display Patient Values
    patient_name_var = tk.StringVar()
    patient_name_display = ttk.Label(root, textvariable=patient_name_var)
    patient_name_display.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

    patient_mrn_var = tk.StringVar()
    patient_mrn_display = ttk.Label(root, textvariable=patient_mrn_var)
    patient_mrn_display.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

    pressure_var = tk.StringVar()
    pressure_display = ttk.Label(root, textvariable=pressure_var)
    pressure_display.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)

    breathing_rate_var = tk.StringVar()
    breathing_rate_display = ttk.Label(root, textvariable=breathing_rate_var)
    breathing_rate_display.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)

    apnea_count_var = tk.StringVar()
    apnea_count_display = ttk.Label(root, textvariable=apnea_count_var)
    apnea_count_display.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)
    default_foreground_color = apnea_count_display.cget('foreground')

    test_time_var = tk.StringVar()
    test_time_display = ttk.Label(root, textvariable=test_time_var)
    test_time_display.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

    # Horizonal Line
    separator = ttk.Separator(root, orient='horizontal')
    separator.grid(row=1, column=0, columnspan=9, pady=(5, 60), sticky="ew")

    # Vertical Line
    vertical_separator = ttk.Separator(root, orient='vertical')
    vertical_separator.grid(row=1, column=3, rowspan=9, padx=(0, 110),
                            sticky="ns")

    # Create Image with Label
    plot_label = ttk.Label(root, text="Most Recent CPAP Data Image:",
                           font=("Helvetica", 15))
    plot_label.grid(row=4, column=0, columnspan=3, pady=(20, 10))
    image_label = ttk.Label(root)
    image_label.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    # Historical Test Image
    plot2_label = ttk.Label(root, text="Historical CPAP Data Image:",
                            font=("Helvetica", 15))
    plot2_label.grid(row=4, column=3, columnspan=4, pady=(20, 10))
    image2_label = ttk.Label(root)
    image2_label.grid(row=5, column=3, columnspan=3, padx=10, pady=5)

    # Update apnea color based on value
    def update_apnea_label_color(apneaCount):
        """
        Update the color of the apnea count label based on the apnea count
        value

        This function takes the apnea count as input and checks if it's in the
        danger range using the dangerApnea function. If true, it sets the
        foreground color of apnea_count_display to red.

        Args:
            apneaCount (int): Apnea count value

        Returns:
            None
        """
        if dangerApnea(apneaCount):
            apnea_count_display.configure(foreground='red')

    # Display patient information based on the selected room
    def update_patient_info():
        """
        Update the patient information based on the selected room.

        This function retrieves the selected room number, calls the
        get_patient_info function, and displays the patient's information
        using the display_all_patient_info function.

        Returns:
            None
        """
        selected_room = room_var.get()
        display_all_patient_info(*get_patient_info(int(selected_room)))

    def display_all_patient_info(mrn, name, pressure, test_time, breath_rate,
                                 apnea_count, image_text):
        """
        Display all patient information on the GUI.

        This function takes patient information as input and updates the GUI
        labels and values accordingly. It also decodes and displays the
        patient's image, updates the apnea count label color, and manages the
        state of various buttons and dropdowns.

        Args:
            mrn (int): Patient's Medical Record Number
            name (str): Patient's name
            pressure (str): Pressure information
            test_time (str): Date of the test
            breath_rate (str): Breathing rate
            apnea_count (str): Apnea count
            image_text (str): Encoded image text

        Returns:
            None
        """
        global current_mrn
        current_mrn = mrn

        add_pressure_button.config(state=tk.NORMAL)

        patient_name_var.set(name)
        patient_mrn_var.set(mrn)
        pressure_var.set(pressure)
        breathing_rate_var.set(breath_rate)
        apnea_count_var.set(apnea_count)
        test_time_var.set(test_time)
        apnea_count_display.configure(foreground=default_foreground_color)

        # Decode Image and Add Image to GUI
        if image_text == "N/A":  # Check if there is a result
            print("No plot to display")
            historic_dropdown['state'] = 'disabled'
            historic_var.set("No Historical Tests")
            download_button.config(state=tk.DISABLED)
            download_button2.config(state=tk.DISABLED)
            update_hist_button.config(state=tk.DISABLED)
            clearimg()
        else:
            update_apnea_label_color(apnea_count)
            newtestvals = get_oldtests(mrn)  # fills dropdown w old tests
            update_hist_button.config(state=tk.NORMAL)
            historic_dropdown['state'] = 'enabled'
            historic_dropdown['values'] = newtestvals

            if len(image_text) < 50:  # removes error when running test data
                print("plot not valid")
                clearimg()

                if len(newtestvals) == 0:
                    historic_dropdown['state'] = 'disabled'
                    historic_var.set("No Historical Tests")
                    clearimg2()
            else:
                buffer = decodeImg(image_text)
                image_obj = Image.open(buffer)
                image_obj.thumbnail(imageSize)
                pil_image = ImageTk.PhotoImage(image_obj)
                image_label.pil_image = image_obj
                image_label.config(image=pil_image)
                image_label.image = pil_image

                download_button.config(state=tk.NORMAL)

                if len(newtestvals) == 0:
                    historic_dropdown['state'] = 'disabled'
                    historic_var.set("No Historical Tests")
                    clearimg2()

    def clearimg():
        """
        Clear the second displayed image on the GUI.

        This function clears BOTH images displayed

        Returns:
            None
        """
        image_label.image = None
        image2_label.image = None

    def clearimg2():
        """
        Clear the second displayed image on the GUI.

        This function sets the second image label to None.

        Returns:
            None
        """
        image2_label.image = None

    def show_comp_image():
        """
        Display the historical CPAP data image on the GUI.

        This function retrieves the selected MRN and date value, gets the
        historical image using get_oldimg, and displays it on the GUI.

        Returns:
            None
        """
        clearimg2()
        mrn = patient_mrn_var.get()
        dateval = historic_var.get()
        img_text = get_oldimg(mrn, dateval)

        if len(img_text) < 50:
            print("plot not valid")
            clearimg()
        else:
            buffer = decodeImg(img_text)
            image2_obj = Image.open(buffer)
            image2_obj.thumbnail(imageSize)
            pil2_image = ImageTk.PhotoImage(image2_obj)
            image2_label.pil2_image = image2_obj
            image2_label.config(image=pil2_image)
            image2_label.image = pil2_image

            download_button2.config(state=tk.NORMAL)

    # BUTTONS
    # Main Show Records Button
    update_button = ttk.Button(root, text="Show Records",
                               command=update_patient_info)
    update_button.grid(row=1, column=2, columnspan=1, pady=10)

    # Show old plot button
    update_hist_button = ttk.Button(root, text="Show Old Data Plot",
                                    command=show_comp_image,
                                    state=tk.DISABLED)
    update_hist_button.grid(row=3, column=5, columnspan=1, pady=10)

    # Function to download image1
    def download_image1():
        """
        Download the currently displayed image (Image 1).

        This function retrieves the currently displayed PIL image in
        image_label and prompts the user to choose a file path for saving the
        image as a PNG file. It prints a success message upon successful
        download and a message if there's no image to download.

        Returns:
            None
        """
        current_pil_image = image_label.pil_image
        if current_pil_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files",
                                                                 "*.png"),
                                                                ("All files",
                                                                 "*.*")])
            if file_path:
                current_pil_image.save(file_path)
                print("Image 1 downloaded successfully.")
        else:
            print("No image to download.")

    # Download Image 1 Button
    download_button = ttk.Button(root, text="Download Image",
                                 command=download_image1,
                                 state=tk.DISABLED)
    download_button.grid(row=6, column=2, pady=10, sticky=tk.E)

    # Function to donwload image 2
    def download_image2():
        """
        Download the currently displayed image (Image 2).

        This function retrieves the currently displayed PIL image in
        image_label and prompts the user to choose a file path for saving the
        image as a PNG file. It prints a success message upon successful
        download and a message if there's no image to download.

        Returns:
            None
        """
        current_pil_image = image2_label.pil2_image
        if current_pil_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files",
                                                                 "*.png"),
                                                                ("All files",
                                                                 "*.*")])
            if file_path:
                current_pil_image.save(file_path)
                print("Image 2 downloaded successfully.")
        else:
            print("No image to download.")

    # Download Image 2 Button
    download_button2 = ttk.Button(root, text="Download Image",
                                  command=download_image2,
                                  state=tk.DISABLED)
    download_button2.grid(row=6, column=5, pady=10)

    def add_new_pressure():
        """
        Add new pressure information for a patient.

        This function retrieves the patient's name, MRN, and pressure value
        from the corresponding variables. If the pressure value is within the
        correct range (as evaluated by the valPressureInput() function), then
        it creates a dictionary and calls the updateInfo function with the
        dictionary as an argument. If the pressure is not within the desired
        range, then a label will appear in the gui telling the user that the
        pressure is not in range

        Returns:
            None
        """
        name = patient_name_var.get()
        mrn = patient_mrn_var.get()
        pressure = pressure_value_var.get()
        if valPressureInput(pressure) is False:
            print("pressure not between 4 and 25")
            wrongpresstext = "PRESSURE MUST BE BETWEEN 4 and 25!"
            wrong_press_label = ttk.Label(root, text=wrongpresstext)
            wrong_press_label.grid(row=10, column=4, padx=(2, 40), pady=5)
            wrong_press_label.configure(foreground='red')
            root.after(4000, lambda: wrong_press_label.grid_forget())

        else:
            out_dict = {"mrn": int(mrn),
                        "name": str(name),
                        "pressure": pressure}
            wrong_press_label = ttk.Label(root, text="Valid Pressure Inputted")
            wrong_press_label.grid(row=10, column=4, padx=(2, 40), pady=5)
            wrong_press_label.configure(foreground='green')
            root.after(2000, lambda: wrong_press_label.grid_forget())
            updateInfo(out_dict)

    # Add Pressure Data Button
    add_pressure_button = ttk.Button(root, text="Upload Pressure",
                                     command=add_new_pressure,
                                     state=tk.DISABLED)
    add_pressure_button.grid(row=9, column=4, pady=20, padx=(150, 2))

    # Update Info every 10 seconds
    def update_dropdown_values():
        """
        Update the values in the room dropdown periodically.

        This function sets the values of the room dropdown to the list of
        available room numbers retrieved from the server. It is scheduled to
        run every 10 seconds.

        Returns:
            None
        """
        room_dropdown['values'] = get_roomlist()
        root.after(6000, update_dropdown_values)
    update_dropdown_values()

    def update_patient_info_periodically():
        """
        Update patient information periodically.

        This function checks if a room number is selected. If a room number is
        selected, it calls the update_patient_info function to refresh the
        patient information. It is scheduled to run every 10 seconds.

        Returns:
            None
        """
        selected_room = room_var.get()
        if selected_room:
            update_patient_info()
        root.after(1000, update_patient_info_periodically)
    update_patient_info_periodically()

    root.mainloop()


if __name__ == "__main__":
    main_window()
