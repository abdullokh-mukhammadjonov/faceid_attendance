from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import argparse
import datetime
import cv2
import os
import face_recognition as face_id
import pkg.helpers as helper
from tkcalendar import DateEntry

PURPLE_COLOR = (255, 0, 255)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "data\\test\\actual")
TEST_IMAGE_DIR = os.path.join(BASE_DIR, "data\\test\\mock")
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
RECTANELE_STROKE = 2

class Application:
    def __init__(self, output_path = "./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.cap = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera

        self.root = tk.Tk()  # initialize root window
        self.root.title("PyImageSearch PhotoBooth")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        knownPeople, labels = helper.get_images_and_labels(IMAGE_DIR)
        self.encodings = helper.get_encodings(knownPeople)
        self.labels = labels

        # ---------------------------
        self.root.state('zoomed') # for windows
        # self.root.attributes('-zoomed', True) # for linux (ubuntu)

        # left side of the window
        self.root.resizable(False,False)
        self.root.title("Attendance System")
        self.root.configure(background='#262523')
        self.leftHalf = tk.Frame(self.root, bg="#00ff00")


        root.option_add("*tearOff", False)

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True, padx=1, pady=(4, 0))

        menubar = tk.Menu()
        root.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        help_menu = tk.Menu(menubar)

        menubar.add_cascade(menu=file_menu, label="File")
        menubar.add_cascade(menu=help_menu, label="Help")

        file_menu.add_command(label="Admin",background="#66ee22", command=example)
        file_menu.add_command(label="Save File", command=example)
        file_menu.add_command(label="Open File", command=example)
        file_menu.add_command(label="Close Tab", command=example)
        file_menu.add_command(label="Exit", command=quit_app)

        help_menu.add_command(label="About", command=show_about_info)

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)



        self.leftHalf.place(relx=0.01, rely=0.08, relwidth=0.5, relheight=0.90)
        self.topLabelLeft = tk.Label(self.leftHalf, text="                       For Already Registered                       ", fg="black",bg="#3ece48" ,font=('times', 17, ' bold ') )
        self.topLabelLeft.pack(side=tk.TOP)
        self.dateAndTimeFrame = tk.Frame(self.leftHalf, bg="#00ff00")
        self.cur_date, self.cur_time = helper.get_date_and_time()
        self.dateLabel = tk.Label(self.dateAndTimeFrame, text="Today : "+self.cur_date,
                                                        width=20,
                                                        height=25,
                                                        bg="#006633",
                                                        fg="white",
                                                        font=('times', 17, ' bold '))
        self.timeLabel = tk.Label(self.dateAndTimeFrame, text="Vaqt : "+self.cur_time,
                                                        width=13,
                                                        height=25,
                                                        bg="#00ff00",
                                                        fg="red",
                                                        font=('times', 17, ' bold '))
        self.dateLabel.place(relx=0.12, y=1, height=25)
        self.timeLabel.place(relx=0.6, y=35, height=25)
        self.dateAndTimeFrame.place(relx=0.005, rely=0.05, relwidth=0.97, relheight=0.3)
        self.update_date_and_time()

        self.panel = tk.Label(self.leftHalf)  # initialize image panel
        self.panel.pack(expand=True)
    
        # create a button, that when pressed, will take the current frame and save it to file
        btn = tk.Button(self.leftHalf, text="Snapshot!", font=("Helvetica", 17), height=3, width=15, borderwidth=0, command=self.take_snapshot)
        btn.pack(fill="both", side=tk.BOTTOM, padx=10, pady=0)

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
        
        # # Registration
        registrationFrame = tk.Frame(self.rightHalf, bg="#ffeeaa")

        self.employee_name = tk.StringVar()
        self.employee_surname = tk.StringVar()
        registrationFrameLabel = tk.Label(registrationFrame, text="                Add new employee",
                                                        fg="black",
                                                        bg="#ffeeaa",
                                                        font=('times', 20, ' bold '))
        placeholderLabel = tk.Label(registrationFrame, text="",
                                                        fg="black",
                                                        bg="#ffeeaa",
                                                        height=3,
                                                        font=('times', 20, ' bold '),
                                                        state='disabled')
        employeeNameLabel = tk.Label(registrationFrame, text="Employee name",
                                                        width=20,
                                                        height=1,
                                                        bg="#ffeeaa",
                                                        fg="black",
                                                        font=('times', 17, ' bold '))
        employeeName = tk.Entry(registrationFrame, textvariable=self.employee_name, 
                                                        width=60,
                                                        fg="black",
                                                        font=('times', 15, ' bold '))
        employeeSurnameLabel = tk.Label(registrationFrame, text="Employee surname",
                                                        width=20,
                                                        height=1,
                                                        bg="#ffeeaa",
                                                        fg="black",
                                                        font=('times', 17, ' bold '))
        employeeSurname = tk.Entry(registrationFrame, textvariable=self.employee_surname,
                                                        width=60,
                                                        fg="black",
                                                        font=('times', 15, ' bold '))
        employeeBirthdateLabel = tk.Label(registrationFrame, text="Birth date",
                                                        width=20,
                                                        height=1,
                                                        bg="#ffeeaa",
                                                        fg="black",
                                                        font=('times', 17, ' bold '))
        datePicker = DateEntry(registrationFrame,width= 16,
                                                        background= "magenta3",
                                                        foreground="white",
                                                        bd=2,
                                                        year=1996,
                                                        selectmode='day',
                                                        locale = 'en_us',
                                                        date_pattern ='dd.mm.yyyy')
        placeholderLabel2 = tk.Label(registrationFrame, text="",
                                                        fg="black",
                                                        bg="#ffeeaa",
                                                        height=1,
                                                        font=('times', 20, ' bold '),
                                                        state='disabled')
        datePicker.place(relx=0.7, rely=0.75)
        
        submitBtn = tk.Button(registrationFrame, text='Submit', command=self.form_submit, width=27)

        registrationFrameLabel.place(x=10, y=20)
        placeholderLabel.grid(row=0,column=0)
        employeeNameLabel.grid(row=1,column=0,ipady=17)
        employeeName.grid(row=1,column=1,ipady=7)
        employeeSurnameLabel.grid(row=2,column=0,ipady=17)
        employeeSurname.grid(row=2,column=1,ipady=7)
        employeeBirthdateLabel.grid(row=3,column=0,ipady=17)
        placeholderLabel2.grid(row=4,column=0,ipady=7)
        submitBtn.grid(row=4,column=1,ipady=1,sticky='w')

        # registrationFrame.place(relx=0.15, rely=0.25, relwidth=0.7, relheight=0.44)




        # # Attendance Table
        attendanceTable = tk.Frame(self.rightHalf, bg="#ffeeaa")
        tv=ttk.Treeview(attendanceTable,height=13,columns=('id','name','date','time'))
        tv.column('#0',width=40)
        tv.column('id',width=82)
        tv.column('name',width=130)
        tv.column('date',width=133)
        tv.column('time',width=133)
        tv.grid(row=2,column=0,padx=(0,0),pady=(150,0),columnspan=4)
        tv.heading('#0',text ='#')
        tv.heading('id',text ='ID')
        tv.heading('name',text ='NAME')
        tv.heading('date',text ='DATE')
        tv.heading('time',text ='TIME')
        i = 1
        for word in ('hgj', 'kjhk', 'lkj', 'drdt','lkj','hgj', 'kjhk', 'lkj', 'drdt','lkj','hgj', 'kjhk', 'lkj', 'drdt','lkj','hgj', 'kjhk', 'lkj', 'drdt','lkj','hgj', 'kjhk', 'lkj', 'drdt','lkj','hgj', 'kjhk', 'lkj', 'drdt','lkj'):
            i = i + 1
            tv.insert('', 0, text='9', values=('Abdulloh', 'Nurulloh', 'Men','8.45'))
        scroll=ttk.Scrollbar(attendanceTable,orient='vertical',command=tv.yview)
        scroll.grid(row=2,column=4,padx=(0,100),pady=(150,0),sticky='ns')
        tv.configure(yscrollcommand=scroll.set)
        attendanceTable.place(relx=0.15, rely=0.25, relwidth=0.7, relheight=0.70)
        


        # lbl2 = tk.Label(rightHalf, text="Enter Name",width=20  ,fg="black"  ,bg="#00aeff" ,font=('times', 17, ' bold '))
        # lbl2.place(x=80, y=140)

        # txt2 = tk.Entry(rightHalf,width=32 ,fg="black",font=('times', 15, ' bold ')  )
        # txt2.place(x=30, y=173)

        # message1 = tk.Label(rightHalf, text="1)Take Images  >>>  2)Save Profile" ,bg="#00aeff" ,fg="black"  ,width=39 ,height=1, activebackground = "yellow" ,font=('times', 15, ' bold '))
        # message1.place(x=7, y=230)

        # message = tk.Label(rightHalf, text="" ,bg="#00aeff" ,fg="black"  ,width=39,height=1, activebackground = "yellow" ,font=('times', 16, ' bold '))
        # message.place(x=7, y=450)

        # clearButton = tk.Button(rightHalf, text="Clear", command=clear  ,fg="black"  ,bg="#ea2a2a"  ,width=11 ,activebackground = "white" ,font=('times', 11, ' bold '))
        # clearButton.place(x=335, y=86)
        # clearButton2 = tk.Button(rightHalf, text="Clear", command=clear2  ,fg="black"  ,bg="#ea2a2a"  ,width=11 , activebackground = "white" ,font=('times', 11, ' bold '))
        # clearButton2.place(x=335, y=172)    
        # takeImg = tk.Button(rightHalf, text="Take Images", command=TakeImages  ,fg="white"  ,bg="blue"  ,width=34  ,height=1, activebackground = "white" ,font=('times', 15, ' bold '))
        # takeImg.place(x=30, y=300)
        # trainImg = tk.Button(rightHalf, text="Save Profile", command=psw ,fg="white"  ,bg="blue"  ,width=34  ,height=1, activebackground = "white" ,font=('times', 15, ' bold '))
        # trainImg.place(x=30, y=380)

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.root.configure(menu=menubar)
        self.video_loop()

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        # while True:
        #     success, frame = cap.read() # capture each frame
        #     frame = cv.flip(frame, 180) # flip 180 degrees
        #     camera_picture = cv.resize(frame, (0, 0), None, 0.8, 0.8)
        #     colored_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB) # get greyscale copy of frame image
        #     colored_frame = cv.resize(colored_frame, (0, 0), None, 0.25, 0.25)
            
        #     frame_faces = face_id.face_locations(colored_frame) # get all faces in the current frame
        #     frame_face_encodings = face_id.face_encodings(colored_frame, frame_faces) # get face encodings
            
        #     for face_encode, face_location in zip(frame_face_encodings, frame_faces):
        #         matches = face_id.compare_faces(encodings, face_encode)
        #         distance = face_id.face_distance(encodings, face_encode)
        #         best_match_index = np.argmin(distance)
        #         y1, x2, y2, x1 = face_location
        #         y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                
        #         if matches[best_match_index]:
        #             print(y1, x2, y2, x1)
        #             match_name = labels[best_match_index]
                    
        #             cv.rectangle(frame, (x1, y1), (x2, y2), COLOR_LIGHT_GREEN, RECTANELE_STROKE)
        #             cv.rectangle(frame, (x1, y2-40), (x2, y2), COLOR_LIGHT_GREEN, cv.FILLED)
        #             cv.putText(frame,  f'{match_name} {round(distance[best_match_index], 2)}', (x1+6, y2-6), cv.FONT_HERSHEY_COMPLEX, 1, COLOR_WHITE, 2)
        #         else:
        #             cv.rectangle(frame, (x1, y1), (x2, y2), COLOR_RED, RECTANELE_STROKE)
                    
        #         scaled_img = cv.resize(frame, (x1, y1), interpolation=cv.INTER_CUBIC)
        #         cv.imwrite("picture.jpg", scaled_img)

            # cv.imshow('frame1', camera_picture) # image show


        ok, frame = self.cap.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            frame = cv2.flip(frame, 180) # flip 180 degrees
            # camera_picture = cv.resize(frame, (0, 0), None, 0.8, 0.8)
            # colored_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB) # get greyscale copy of frame image
            # colored_frame = cv.resize(colored_frame, (0, 0), None, 0.25, 0.25)
            
            # frame_faces = face_id.face_locations(colored_frame) # get all faces in the current frame
            # frame_face_encodings = face_id.face_encodings(colored_frame, frame_faces) # get face encodings


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
        p = os.path.join(self.output_path, filename)  # construct output path
          # convert to RGB
        self.current_image.save(p, "png")  # save image as jpeg file
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
        print('name :', name, '   surname :', surname)

    def update_date_and_time(self):
        self.cur_date, self.cur_time = helper.get_date_and_time()
        self.dateLabel.configure(text=self.cur_date)
        self.timeLabel.configure(text=self.cur_time)
        self.dateAndTimeFrame.after(1000, self.update_date_and_time)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
    help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()

