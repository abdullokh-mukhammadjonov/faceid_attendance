import csv
import json
import re
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import argparse
import datetime
import cv2
import os
import face_recognition as face_id
import numpy as np
import pkg.helpers as helper
from tkcalendar import DateEntry

PURPLE_COLOR = (255, 0, 255)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "data/test/actual")
EMPLOYEES_IMAGES_DIR = os.path.join(BASE_DIR, "data/images/employees")
EMPLOYEES_DATA_FILE_PATH = os.path.join(BASE_DIR, "data/csv/employees.csv")
ATTENDANCE_DATA_FOLDER_PATH = os.path.join(BASE_DIR, "data/csv/attendance")
TEST_IMAGE_DIR = os.path.join(BASE_DIR, "data/test/mock")
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
RECTANGLE_STROKE = 2
SCALING_FACTOR = 0.7
SNAPSHOT_CROP_SIZE = (80+RECTANGLE_STROKE, 80+RECTANGLE_STROKE, 420-RECTANGLE_STROKE, 420-RECTANGLE_STROKE)

class Application:
    def __init__(self, output_path = "./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.cap = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera
        self.mode = 'table'

        self.root = tk.Tk()  # initialize root window
        self.root.title("PyImageSearch PhotoBooth")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.refresh_labels_and_encodings()

        # ---------------------------
        # self.root.state('zoomed') # for windows
        self.root.attributes('-zoomed', True) # for linux (ubuntu)

        # left side of the window
        self.root.resizable(False,False)
        self.root.title("Attendance System")
        self.root.configure(background='#262523')
        self.leftHalf = tk.Frame(self.root, bg="#00ff00")

        # root.option_add("*tearOff", False)
        menubar = tk.Menu()
        file_menu = tk.Menu(menubar)
        help_menu = tk.Menu(menubar)

        menubar.add_cascade(menu=file_menu, label="Admin")
        menubar.add_cascade(menu=help_menu, label="Help")

        file_menu.add_command(label="Add new employee",background="#66ee22", command=self.bring_registration_frame)
        file_menu.add_command(label="Save File", command=self.example)
        file_menu.add_command(label="Open File", command=self.example)
        file_menu.add_command(label="Close Tab", command=self.example)
        file_menu.add_command(label="Exit", command=self.example)

        self.leftHalf.place(relx=0.01, rely=0.08, relwidth=0.5, relheight=0.90)
        self.topLabelLeft = tk.Label(self.leftHalf, text="                       For Already Registered                       ", fg="black",bg="#3ece48" ,font=('times', 17, ' bold ') )
        self.topLabelLeft.pack(side=tk.TOP)
        self.dateAndTimeFrame = tk.Frame(self.leftHalf, bg="#00ff00")
        self.cur_date, self.cur_time = helper.get_date_and_time()
        self.dateLabel = helper.make_label(self.dateAndTimeFrame, "Today : "+self.cur_date, 20, 25, "", "white", "#006633", font=('times', 17, ' bold '))
        self.timeLabel = helper.make_label(self.dateAndTimeFrame, "Vaqt : "+self.cur_time, 13, 25, "", "red", "#00ff00", ('times', 17, ' bold '))
        self.dateLabel.place(relx=0.12, y=1, height=25)
        self.timeLabel.place(relx=0.6, y=35, height=25)
        self.dateAndTimeFrame.place(relx=0.005, rely=0.05, relwidth=0.97, relheight=0.3)
        self.update_date_and_time()

        self.panel = tk.Label(self.leftHalf)  # initialize image panel
        self.panel.pack(expand=True)

        # # # right side of the window
        self.rightHalf = tk.Frame(self.root, bg="#00aeff")
        self.rightHalf.place(relx=0.51, rely=0.08, relwidth=0.5, relheight=0.90)
        
        help_menu = tk.Menu(self.root ,relief='ridge')
        admin_menu = tk.Menu(self.root ,relief='ridge')
        filemenu = tk.Menu(help_menu,tearoff=0)
        mainmenu = tk.Menu(help_menu,tearoff=0)
        mainmenu.add_command(label='Add new employee')
        filemenu.add_command(label='Change Password')
        filemenu.add_command(label='Contact Us')
        filemenu.add_command(label='Exit')
        help_menu.add_cascade(label='Help',font=('times', 29, ' bold '),menu=filemenu)
        admin_menu.add_cascade(label='Admin',font=('times', 29, ' bold '),menu=mainmenu)
        
        # # load table frame
        self.load_table_frame()
        self.refresh_table_data()
        

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.root.configure(menu=menubar)
        self.video_loop()

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.cap.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            frame = cv2.flip(frame, 180) # flip 180 degrees
            frame = cv2.resize(frame, (500, 500), interpolation = cv2.INTER_AREA)
            if self.mode == 'register':
                cv2.rectangle(frame, (80, 420), (420, 80), COLOR_LIGHT_GREEN, RECTANGLE_STROKE)
            else:
                colored_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # get greyscale copy of frame image
                colored_frame = cv2.resize(colored_frame, (0, 0), None, 0.35, 0.35)
                
                frame_faces = face_id.face_locations(colored_frame) # get all faces in the current frame
                frame_face_encodings = face_id.face_encodings(colored_frame, frame_faces) # get face encodings
                
                for face_encode, face_location in zip(frame_face_encodings, frame_faces):
                    matches = face_id.compare_faces(self.encodings, face_encode)
                    distance = face_id.face_distance(self.encodings, face_encode)
                    best_match_index = np.argmin(distance)
                    y1, x2, y2, x1 = face_location
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    
                    pad_size = 60
                    Y1_POSITION, Y2_POSITION = y1-pad_size, y2-pad_size
                    X1_POSITION, X2_POSITION = x1-pad_size, x2-pad_size
                    
                    if matches[best_match_index]:
                        # print(y1, x2, y2, x1)
                        match_name = self.labels[best_match_index]

                        cv2.rectangle(frame, (X1_POSITION, Y1_POSITION), (X2_POSITION, Y2_POSITION), COLOR_LIGHT_GREEN, RECTANGLE_STROKE)
                        cv2.rectangle(frame, (X1_POSITION, Y2_POSITION-40), (X2_POSITION, Y2_POSITION), COLOR_LIGHT_GREEN, cv2.FILLED)
                        cv2.putText(frame,  f'{match_name}', (X1_POSITION+6, Y2_POSITION-6), cv2.FONT_HERSHEY_COMPLEX, 1, COLOR_WHITE, 2) # {round(distance[best_match_index], 2)}
                    else:
                        cv2.rectangle(frame, (X1_POSITION, Y1_POSITION), (X2_POSITION, Y2_POSITION), COLOR_RED, RECTANGLE_STROKE)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.root.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now() # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # construct filename
        snapshot_image = self.current_image.crop(SNAPSHOT_CROP_SIZE) # crop the frame to only include the face
        # p = os.path.join(self.output_path, filename)  # construct output path
        # snapshot_image.save(p, "png")  # save image as jpeg file
        
        if self.mode == 'register':
            snapshot_resized = snapshot_image.resize((225,225))
        
            imgtk = ImageTk.PhotoImage(image=snapshot_resized)
            self.employee_picture = snapshot_resized
            self.employeePhoto.imgtk = imgtk
            self.employeePhoto.config(image=imgtk)
            
        print("[INFO] saved {}".format(filename))

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.cap.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application

    def form_submit(self):
        name = self.employee_name.get()
        surname = self.employee_surname.get()
        birth_date = self.datePicker.get_date()
        name_trimmed = re.sub('[^a-zA-Z]+', '', name.lower())
        surname_trimmed = re.sub('[^a-zA-Z]+', '', surname.lower())
        img_name = name_trimmed + "_" + surname_trimmed + ".jpg"
        img_destination = EMPLOYEES_IMAGES_DIR + "/"+ img_name
        self.employee_picture.save(img_destination, "png")
        
        encodings = helper.get_single_image_encodings(img_destination)
        stringified_encodings = "\n".join(str(x) for x in encodings)
        data_array = [name, surname, birth_date, img_name, stringified_encodings]

        exists = os.path.isfile(EMPLOYEES_DATA_FILE_PATH)
        if exists:
            with open(EMPLOYEES_DATA_FILE_PATH, 'a+') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(data_array)
            csv_file.close()
        else:
            with open(EMPLOYEES_DATA_FILE_PATH, 'w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(data_array)
            csv_file.close()
        
        self.refresh_labels_and_encodings()

    def update_date_and_time(self):
        self.cur_date, self.cur_time = helper.get_date_and_time()
        self.dateLabel.configure(text=self.cur_date)
        self.timeLabel.configure(text=self.cur_time)
        self.dateAndTimeFrame.after(1000, self.update_date_and_time)
    
    def example(self):
        print("Example")
        
    def refresh_table_data(self):
        cur_date, _ = helper.get_date_and_time()
        data_file_path = ATTENDANCE_DATA_FOLDER_PATH + "/" + cur_date + ".csv"
        exists = os.path.isfile(data_file_path)
        if not exists:
            helper.generate_deatils_csv_file(EMPLOYEES_DATA_FILE_PATH, cur_date, data_file_path)
        
        # # adding an attendance details row
        attendance_details = []
        attendance_details_count = 0
        with open(data_file_path, 'r') as csv_reader_file:
            reader = csv.reader(csv_reader_file)
            for line in reader:
                attendance_details.append(line)
                attendance_details_count = attendance_details_count + 1
        csv_reader_file.close()
        
        # # checking if new employee was added
        employees_count = 0
        last_employee = []
        with open(EMPLOYEES_DATA_FILE_PATH, 'r') as csv_employees_file:
            reader = csv.reader(csv_employees_file)
            for line in reader:
                last_employee = line
                employees_count = employees_count + 1
        csv_employees_file.close()
        
        if employees_count > attendance_details_count:
            with open(data_file_path, 'a+') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([cur_date, last_employee[0], last_employee[1], '---', '---', '---', '---'])
            csv_file.close()
        
        return attendance_details
        
    def load_table_frame(self):
        # # Attendance Table
        self.attendanceTable = tk.Frame(self.rightHalf, bg="#ffeeaa")
        tv=ttk.Treeview(self.attendanceTable,height=13,columns=('name','surname','arrival_time','on_time'))
        tv.column('#0',width=30)
        tv.column('name',width=133)
        tv.column('surname',width=133)
        tv.column('arrival_time',width=95)
        tv.column('on_time',width=40)
        tv.grid(row=2,column=0,padx=(0,0),pady=(150,0),columnspan=4)
        tv.heading('#0',text ='#')
        tv.heading('name',text ='NAME')
        tv.heading('surname',text ='SURNAME')
        tv.heading('arrival_time',text ='ARRIVED_AT')
        tv.heading('on_time',text ='ON_TIME')
        
        attendance_details = self.refresh_table_data()
        i = len(attendance_details)
        for employee in attendance_details:
            tv.insert('', 0, text=str(i), values=(employee[1], employee[2], employee[3], employee[4]))
            i = i - 1
        scroll=ttk.Scrollbar(self.attendanceTable,orient='vertical',command=tv.yview)
        scroll.grid(row=2,column=4,padx=(0,100),pady=(150,0),sticky='ns')
        tv.configure(yscrollcommand=scroll.set)
        self.attendanceTable.place(relx=0.15, rely=0.25, relwidth=0.7, relheight=0.70)
    
    def bring_table_frame(self):
        # # remove back button
        self.backButton.destroy()
        # # remove snapshot button
        self.snapshot_btn.destroy()
        # # remove registrationFrame
        self.registrationFrame.destroy()
        # # switch mode
        self.mode = 'table'
        self.load_table_frame()
        
    def refresh_labels_and_encodings(self):
        labels, encodings = helper.get_images_and_labels_from_csv(EMPLOYEES_DATA_FILE_PATH, EMPLOYEES_IMAGES_DIR)
        self.encodings = encodings
        self.labels = labels
        
    def bring_registration_frame(self):
        # # remove table frame
        self.attendanceTable.destroy()
        # # switch mode
        self.mode = 'register'
        # # create a button, that when pressed, will take the current frame and save it to file
        self.snapshot_btn = tk.Button(self.leftHalf, text="Snapshot!", font=("Helvetica", 17), height=3, width=15, borderwidth=0, command=self.take_snapshot)
        self.snapshot_btn.pack(fill="both", side=tk.BOTTOM, padx=10, pady=0)
        # # back button
        self.backButton = tk.Button(self.rightHalf, text="< back",bg="yellow",command=self.bring_table_frame)
        # # Registration frame
        self.registrationFrame = tk.Frame(self.rightHalf, bg="#ffeeaa")

        self.employee_name = tk.StringVar()
        self.employee_surname = tk.StringVar()
        registrationFrameLabel = helper.make_label(self.registrationFrame, "                Add new employee", 0, 0, "", "", "#ffeeaa", font=('times', 20, ' bold '))
        placeholderLabel = helper.make_label(self.registrationFrame, "", 0, 3, "disabled", "", "#ffeeaa", font=('times', 20, ' bold '))
        employeeNameLabel = helper.make_label(self.registrationFrame, "Employee name", 20, 1, "", "", "#ffeeaa", font=('times', 17, ' bold '))

        employeeName = tk.Entry(self.registrationFrame, textvariable=self.employee_name, 
                                                        width=60,
                                                        fg="black",
                                                        font=('times', 15, ' bold '))
        employeeSurnameLabel = helper.make_label(self.registrationFrame, "Employee surname", 20, 1, "", "", "#ffeeaa", font=('times', 17, ' bold '))
        employeeSurname = tk.Entry(self.registrationFrame, textvariable=self.employee_surname,
                                                        width=60,
                                                        fg="black",
                                                        font=('times', 15, ' bold '))
        employeeBirthdateLabel = helper.make_label(self.registrationFrame, "Birth date", 20, 1, "", "", "#ffeeaa", font=('times', 17, ' bold '))
        self.datePicker = DateEntry(self.registrationFrame,width= 16,
                                                        background= "magenta3",
                                                        foreground="white",
                                                        bd=2,
                                                        year=1996,
                                                        selectmode='day',
                                                        locale = 'en_us',
                                                        date_pattern ='dd.mm.yyyy')
        employeePhotoLabel = helper.make_label(self.registrationFrame, "Face picture", 20, 1, "", "", "#ffeeaa", font=('times', 17, ' bold '))
           
        unknown_person_img = Image.open("data/images/unknown.jpeg")
        self.employeePhoto = tk.Label(self.registrationFrame, bg="#ffeeaa")
        
        imgtk = ImageTk.PhotoImage(unknown_person_img) # convert image for tkinter
        self.employeePhoto.imgtk = imgtk # anchor imgtk so it does not be deleted by garbage-collector
        self.employeePhoto.config(image=imgtk) # show the image
        placeholderLabel2 = helper.make_label(self.registrationFrame, "", 0, 1, "disabled", "", "#ffeeaa", font=('times', 20, ' bold '))

        self.datePicker.place(relx=0.7, rely=0.39)
        
        submitBtn = tk.Button(self.registrationFrame, text='Submit', command=self.form_submit, width=27)

        registrationFrameLabel.place(x=10, y=20)
        placeholderLabel.grid(row=0,column=0)
        employeeNameLabel.grid(row=1,column=0,ipady=17)
        employeeName.grid(row=1,column=1,ipady=7)
        employeeSurnameLabel.grid(row=2,column=0,ipady=17)
        employeeSurname.grid(row=2,column=1,ipady=7)
        employeeBirthdateLabel.grid(row=3,column=0,ipady=17)
        employeePhotoLabel.grid(row=4,column=0,ipady=7)
        self.employeePhoto.grid(row=4,column=1,ipady=17)
        placeholderLabel2.grid(row=5,column=0,ipady=7)
        submitBtn.grid(row=5,column=1,ipady=1,sticky='w')

        self.backButton.place(width=55, relx=0.15, rely=0.15)
        self.registrationFrame.place(relx=0.15, rely=0.2, relwidth=0.7, relheight=0.61)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
    help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()

