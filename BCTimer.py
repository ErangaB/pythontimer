#!/usr/bin/env python

# import the library
from appJar import gui
from hashlib import md5
from datetime import datetime
import mysql.connector
import sys
import time
import os

#database information
db_user = 'root'
db_password = ''
db_host = '127.0.0.1'
db_database = 'python_test'    

#global variables
usr = ""
pwd = ""
cursor = ""
user_name = ""
user_id = 0
projects = []
project_id = []
result_array = []
selected_project = ""
start_time = 0
stop_time = 0
total_time_spent = 0
row_id = 0
date = ""
project_time_id = 0
old_start_time = ""
old_end_time = ""

# display username in status bar
def display_username():
    global user_name
    if(user_name==""):
        display_name = "Please sign in"
    else:
        display_name = user_name
    return display_name

# alert when going to exit from the application
def check_stop():
    return app.yesNoBox("Confirm Exit", "Are you sure you want to exit the application?")

#sign out the user
def sign_out():
	print "sign out"

#SCREENS
#login screen
def screen_login():
    # create a GUI variable for login
    app.setResizable(canResize=False)
    app.setIcon('./img/logo.ico')
    app.setBg("#222222")
    app.setFg("#EEEEEE", override=False)
    app.setFont(12)
    app.enableEnter(press)
    # add & configure widgets - widgets get a name, to help referencing them later
    app.removeAllWidgets()
    app.setPadding([6,6])
    app.addLabel("title1", "Welcome to BC-Portal")
    app.setLabelPadding("title1", [5,5])
    app.setLabelBg("title1", "red")
    app.startLabelFrame("Login")
    app.setLabelFrameFg("Login", "#EEEEEE")
    app.setPadding([8,8])
    app.setSticky("EW")
    app.addLabelEntry("Username :")
    app.addLabelSecretEntry("Password :")
    app.addButtons(["Sign in", "Cancel"], press)# link the buttons to the function called press()
    app.stopLabelFrame()
    #set statusbar status
    status_text = display_username()
    app.setStatusbar(status_text, field=0)

#project screen
def screen_project():
    app.removeAllWidgets()
    app.setPadding([6,6])
    app.addLabel("title2", "0 hours 0 minutes 0 seconds")
    app.setLabelPadding("title2", [5,5])
    app.setLabelBg("title2", "red")
    app.addFlashLabel("title3", "In Progress")
    app.setLabelPadding("title3", [5,5])
    app.setLabelBg("title3", "red")
    app.hideLabel("title3")
    app.startLabelFrame("Timer")
    app.setLabelFrameFg("Timer", "#EEEEEE")
    app.setSticky("EW")
    app.setPadding([18,18])
    app.addOptionBox('project_list',projects)
    app.addButtons(["Start","Stop","Edit","Sign out", "Exit"], start_timer)
    app.setButtonBg("Edit", "#FFCC5C")
    app.setButtonBg("Sign out", "#B0AAC0")
    app.setButtonBg("Exit", "#DC4C46")
    app.disableButton("Stop")
    app.stopLabelFrame()
    #set statusbar status
    status_text = display_username()
    app.setStatusbarBg("#B5E7A0", 0)
    app.setStatusbar(status_text, field=0)

#edit screen
def screen_edit():
    app.removeAllWidgets()
    app.setIcon('./img/logo.ico')
    app.setBg("#222222")
    app.setFg("#EEEEEE", override=False)
    app.setFont(12)
    app.setGeometry("400x200")
    app.setPadding([8,8])
    app.setSticky("EW")
    app.addLabel("title4", "Edit Timer Event")
    app.setLabelPadding("title4", [5,5])
    app.setLabelBg("title4", "red")
    app.startLabelFrame("Overview")# start the frame
    app.setLabelFrameFg("Overview", "#EEEEEE")
    app.setPadding([8,8])
    app.setSticky("EW")
    app.addLabelOptionBox("projects",['- Select Project -'] ,colspan=2)
    app.addLabelEntry("Start time", 1, 0)
    app.addLabelEntry("End time", 1,1)
    app.addButtons(["Update","Delete","Cancel"], update_timer, colspan=2)
    app.setButtonBg("Update", "#96CEB4")
    app.setButtonBg("Delete", "#FF6F69")
    app.setEntryDefault("Start time", "--:--:--")
    app.setEntryDefault("End time", "--:--:--")
    app.stopLabelFrame()# stop the frame
    #set statusbar status
    status_text = display_username()
    app.setStatusbarBg("#B5E7A0", 0)
    app.setStatusbar(status_text, field=0)

#END OF SCREENS

# connect to database
def start_db():
    global db_user
    global db_password
    global db_host
    global db_database 
    return mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)

# convert time to seconds
def str2secs(time):
    periods = time.count(':')
    if(periods==2):
        h,m,s = map(int,time.split(":")) 
        return h*3600+m*60 + s
    else:
        app.warningBox("Error !", "Please keep the proper time formatting", parent=None)
        return 0
    
#check 'total_time_spent' when the programe is loading
def check_total_time():
    global user_id
    global total_time_spent
    global date
    current_time = datetime.now()
    date = current_time.strftime('%d/%m/%Y') #work_date
    connect_db = start_db()
    cursor = connect_db.cursor()
    cursor.execute("SELECT total_time FROM time WHERE user_id=%s AND work_date=%s AND total_time IS NOT NULL ORDER BY time_id DESC LIMIT 1",(user_id,date))
    result_array = cursor.fetchall()
    cursor.close()
    if(result_array):
        for row in result_array:
            total_time_spent_formatted = row[0]
        if total_time_spent_formatted is not None:
            total_time_spent = str2secs(total_time_spent_formatted)
        else:
           total_time_spent = 0 
    else:
        total_time_spent = 0
    connect_db.close()

# check if there are any incomplete records in the table
def incomplete_record_alert():
    connect_db = start_db()
    cursor = connect_db.cursor()
    cursor.execute("SELECT total_time FROM time WHERE user_id=%s AND work_date=%s AND total_time IS NULL",(user_id,date))
    result_array = cursor.fetchall()
    cursor.close()
    connect_db.close()
    if result_array:
        app.warningBox("Warning !", "Incomplete records found.\nPlease fix them before starting a new session", parent=None)
    else:
        return 0

# enable update button
def activate_update_button(*args):
    global old_start_time
    global old_end_time
    new_start_time = app.getEntry("Start time")
    new_end_time = app.getEntry("End time")
    if(old_start_time != new_start_time or old_end_time != new_end_time):
        app.enableButton("Update")
        app.disableButton("Delete")
    else:
        app.disableButton("Update")
        app.enableButton("Delete")
    
# display start time and end time in edit view according to the selected project
def get_project_times(*args):
    global result_array
    global project_time_id
    global old_start_time
    global old_end_time
    project_name_id = app.getOptionBox("projects")
    name_number_array = project_name_id.split(".")
    index = int(name_number_array[0])-1
    selected_project = result_array[index]
    project_time_id = selected_project[0]
    old_start_time = selected_project[2]
    old_end_time = selected_project[3]
    app.setEntry("Start time", old_start_time, callFunction=False)
    app.setEntry("End time", old_end_time, callFunction=False)
    app.setEntryChangeFunction("Start time", activate_update_button)
    app.setEntryChangeFunction("End time", activate_update_button)
    app.disableButton("Update")
    app.enableButton("Delete")
    
# create a log file
def create_file():
    current_time = datetime.now()
    filename = "%s_%s.txt"%(usr, current_time.strftime('%d-%m-%Y'))
    filepath = os.path.join('./logs', filename)
    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    return filepath
        
# get time in hh:mm:ss format
def time_format(time, mode): #mode 0-less details, 1-more details
    m, s = divmod(time, 60)
    h, m = divmod(m, 60)
    if(mode == 1):
        return "%d hours : %02d minutes : %02d seconds"%(h, m, s)
    else:
        return "%d:%02d:%02d"%(h, m, s)

# update the 'total_time' field in the table
def update_total_time(time_id,time_difference):
    global total_time_spent
    connect_db = start_db()
    cursor = connect_db.cursor()
    cursor.execute("SELECT total_time FROM time WHERE time_id=%s",[time_id])
    result_array = cursor.fetchall()
    cursor.close()
    for row in result_array:
        old_total_time = row[0]
    if old_total_time is not None:
        formatted_old_total_time = str2secs(old_total_time)
    else:
        formatted_old_total_time = total_time_spent
    formatted_new_total_time = formatted_old_total_time + time_difference
    updated_row_total_time = time_format(formatted_new_total_time, 0)
    cursor = connect_db.cursor()
    cursor.execute("UPDATE time SET total_time=%s WHERE time_id=%s",(updated_row_total_time,time_id))
    connect_db.commit()
    cursor.close()
    connect_db.close()

# create new sub array from main array by spliting the main array
def split_array():
    global result_array
    id_array = []
    for row in result_array: # put time_id s into an array
        id_array.append(row[0])
    split_point_index = id_array.index(project_time_id) + 1 # get index where we want to split main array
    return id_array[split_point_index:]
    
# update new time event from the edit window
def update_timer(button):
    global project_time_id
    global old_start_time
    global old_end_time
    if (button == "Update"):
        update_array = []
        new_start_time = app.getEntry("Start time")
        new_end_time = app.getEntry("End time")
        if(new_start_time == old_start_time and new_end_time == old_end_time):
            app.warningBox("Warning !", "No changes detected. Nothing to update", parent=None)
        else:
            formatted_new_start_time = str2secs(new_start_time)
            formatted_new_end_time = str2secs(new_end_time)
            formatted_old_start_time = str2secs(old_start_time)
            if old_end_time is not None:
                formatted_old_end_time = str2secs(old_end_time)
            else:
                formatted_old_end_time = 0
            if(formatted_new_start_time != 0 and formatted_new_end_time != 0):
                time_difference_seconds_new = formatted_new_end_time - formatted_new_start_time
                if (formatted_old_end_time != 0):
                    time_difference_seconds_old = formatted_old_end_time - formatted_old_start_time
                else:
                    time_difference_seconds_old = 0
                formatted_time_different = time_difference_seconds_new - time_difference_seconds_old # get time differents in seconds
                spent_time_new = time_format(time_difference_seconds_new, 0) # get new spent time
                update_array = split_array() # new array with ids that want to be updated
                #update affected row
                # first step - get the 'total time' from the table updated
                update_total_time(project_time_id,formatted_time_different)
                # second step - update affected row
                connect_db = start_db()
                cursor = connect_db.cursor()
                cursor.execute("UPDATE time SET start_time=%s, end_time=%s, spend_time=%s WHERE time_id=%s",(new_start_time,new_end_time,spent_time_new,project_time_id))
                connect_db.commit()
                # third step - update total time for the existing rows
                for row in update_array:
                    update_total_time(row,formatted_time_different)
                app.warningBox("Success !", "Record updated successfully", parent=None)
                app.disableButton("Update")
                app.disableButton("Delete") 
                #close the database connection
                cursor.close()
                connect_db.close()
                start_timer("Edit")
            else:
                start_timer("Edit")
    elif(button == "Delete"):
        update_array = []
        formatted_spent_time = 0
        confirmation = app.questionBox("Warning !", "Are you sure want to delete this session", parent=None)
        if(confirmation=='yes'):
            connect_db = start_db()
            cursor = connect_db.cursor()
            cursor.execute("SELECT spend_time FROM time WHERE time_id=%s",[project_time_id])# select the 'spent_time' of the record that is going to delete
            result = cursor.fetchall()
            cursor.close()
            cursor = connect_db.cursor()
            cursor.execute("DELETE FROM time WHERE time_id=%s",[project_time_id])# delete the selected row from the database
            connect_db.commit()
            cursor.close()
            for row in result:
                spent_time = row[0] # get the 'spent_time' from the record we want to delete
            formatted_spent_time = str2secs(spent_time) # spent_time in seconds
            update_array = split_array()
            if update_array is not None:
                for row in update_array:
                    time_id_select = row
                    cursor_select = connect_db.cursor()
                    cursor_select.execute("SELECT time_id, total_time FROM time WHERE time_id=%s AND total_time IS NOT NULL",[time_id_select]) # get total time for other records
                    select_result = cursor_select.fetchall()
                    cursor_select.close()
                    for total_time_row in select_result:
                        time_id = total_time_row[0]
                        total_time = total_time_row[1]
                        formatted_total_time = str2secs(total_time)
                        new_formatted_total_time = formatted_total_time - formatted_spent_time
                        new_total_time = time_format(new_formatted_total_time, 0)
                        cursor_update = connect_db.cursor()
                        cursor_update.execute("UPDATE time SET total_time=%s WHERE time_id=%s",(new_total_time, time_id)) # update total time for other records
                        connect_db.commit()
                        cursor_update.close()
            connect_db.close()
            app.warningBox("Success !", "Record deleted successfully", parent=None)
            app.disableButton("Update")
            app.disableButton("Delete")
            start_timer("Edit")
    else:
        load_projects()

# get id according to option value
def get_project_id():
    global selected_project
    if selected_project in projects:
        project_index = projects.index(selected_project)
        return project_id[project_index]

# insert values to database
def insert_db(start_time):
    global user_id
    global total_time_spent
    global date
    user = user_id #user_id
    project = get_project_id() # project_id
    #connect to the database
    connect_db = start_db()
    cursor = connect_db.cursor()
    cursor.execute("INSERT INTO time (user_id,project_id,work_date,start_time) VALUES (%s,%s,%s,%s)",(user,project,date,start_time)) # insert new row to table
    connect_db.commit()
    if cursor.lastrowid:
        return cursor.lastrowid #app.warningBox("Success !", "Your session is saved", parent=None)
    else:
        app.warningBox("Error !", "Something wrong. Please try again", parent=None)
    #close the cursor and database connection
    cursor.close()
    connect_db.close()

# update values of the table
def update_db(stop_time,time_taken,total_time):
    global row_id
    connect_db = start_db()
    cursor = connect_db.cursor()
    cursor.execute("UPDATE time SET end_time=%s, spend_time=%s, total_time=%s WHERE time_id=%s",(stop_time,time_taken,total_time,row_id)) # update row of the table
    connect_db.commit();
    if cursor.rowcount:
        app.warningBox("Success !", "Your session is saved", parent=None)
    else:
        app.warningBox("Error !", "Something wrong. Please try again", parent=None)
    #close the cursor and database connection
    cursor.close()
    connect_db.close()

# retrieve data from database
def select_db():
    global user_id
    global date
    connect_db = start_db()
    cursor = connect_db.cursor()
    cursor.execute("SELECT  time_id, project_name, start_time, end_time FROM time INNER JOIN projects ON time.project_id=projects.project_id WHERE user_id=%s AND work_date=%s ORDER BY time_id ASC ;",(user_id,date)) # update row of the table
    result = cursor.fetchall()
    return result
    cursor.close()
    connect_db.close()
    
# start and stop the timer
def start_timer(button):
    global usr
    global pwd
    global cursor
    global user_name
    global user_id
    global projects
    global project_id
    global result_array
    global selected_project
    global start_time
    global stop_time
    global total_time_spent
    global row_id
    global date
    global project_time_id
    global old_start_time
    global old_end_time
    if (button == "Start"):
        project = app.getOptionBox("project_list")
        app.disableOptionBox("project_list")
        if(project==None):
            app.enableOptionBox("project_list")
            app.warningBox("Error !", "No Project Selected", parent=None)
        else:
            start_time = time.time()
            start_time_simple = time.strftime("%H:%M:%S", time.localtime(start_time))# startup time for the task (simple format)
            selected_option = app.getOptionBox("project_list") # get the selected project
            selected_project = selected_option
            row_id = insert_db(start_time_simple)# insert data to the database
            app.disableButton("Start")
            app.disableButton("Edit")
            app.disableButton("Sign out")
            app.disableButton("Exit")
            app.enableButton("Stop")
            app.hideLabel("title2")
            app.showLabel("title3")
  
    elif (button == "Stop"):
        stop_time = time.time()
        app.disableButton("Stop")
        app.enableButton("Start")
        app.enableButton("Edit")
        app.enableButton("Sign out")
        app.enableButton("Exit")
        app.enableOptionBox("project_list")
        total_time = stop_time - start_time
        stop_time_simple = time.strftime("%H:%M:%S", time.localtime(stop_time))# stop time for the task (simple format)
        total_time_spent += total_time# total time spent is updated
        time_taken = time_format(total_time, 1)# time for each task
        time_taken_simple = time_format(total_time, 0)# time for each task (simple format)
        time_taken_all = time_format(total_time_spent, 1)#time for all tasks
        time_taken_all_simple = time_format(total_time_spent, 0)#time for all tasks (simple format)
        app.setLabel("title2", time_taken_all)# update the label time
        app.hideLabel("title3")
        app.showLabel("title2")
        update_db(stop_time_simple,time_taken_simple,time_taken_all_simple)# add data to the database
        output = "=================== Project : %s ======================= \nTime taken for this task = %s \nTime taken for all tasks = %s \n============================================================ \n\n"%(selected_project,time_taken,time_taken_all)
        print output
        #write in the log file for project details
        path = create_file()
        log_file =  open(path, "a+")
        log_file.write(output)
        log_file.close()

    elif (button == "Edit"):
        result_array = select_db()
        if(result_array):
            # start edit screen
            screen_edit()
            app.disableButton("Update")
            app.disableButton("Delete")

            #edit time function
            project_name = []
            count = 1
            project_name.append('- Select Project -')
            for row in result_array:
                project_name.append("%s. %s"%(count, row[1]))
                count += 1
            app.changeOptionBox("projects", project_name, callFunction=True)
            app.setOptionBoxChangeFunction("projects", get_project_times)          
        else:
            app.warningBox("Error !", "No records to edit or records are expired", parent=None)
            load_projects()

    elif (button == "Sign out"):
        usr = ""
        pwd = ""
        cursor = ""
        user_name = ""
        user_id = 0
        projects = []
        project_id = []
        result_array = []
        selected_project = ""
        start_time = 0
        stop_time = 0
        total_time_spent = 0
        row_id = 0
        date = ""
        project_time_id = 0
        old_start_time = ""
        old_end_time = ""
        status_text = display_username()
        app.setStatusbarBg("#F0F0F0", 0)
        app.setStatusbar(status_text, field=0)
        screen_login()

    else:
        #write in the log file for logout
        current_time = datetime.now()
        date_time = current_time.strftime('%d-%b-%Y-%H:%M:%S')
        path = create_file()
        log_file =  open(path, "a+")
        log_file.write("************* %s logged out %s ************\n\n"%(usr, date_time))
        log_file.close()
        app.stop()
        
# function for load the timer screen and clear the window
def timer_screen_start():
    app.removeAllWidgets()
    app.addImage('spinner', './img/spinner.gif')

# function for user login
def login():
    connect_db = start_db()
    cursor = connect_db.cursor()
    global user_name
    global usr
    global pwd
    error = None
    username_form  = usr
    password_form  = pwd
    cursor.execute("SELECT COUNT(1) FROM user WHERE username = %s;", [username_form]) # checks if username is exsits
    if cursor.fetchone()[0]:
        cursor.execute("SELECT * FROM user WHERE username = %s;", [username_form]) # fetch the hashed password
        for row in cursor.fetchall():
            if md5(password_form).hexdigest() == row[2]: #column number for password field in the table 
                #app.warningBox("Error !", "Login Successful", parent=None)
                #user_name = row[1] # get the user name
                user_name = usr # TEMPORARY
                validated_user_id = row[0] #column number for userid
                timer_screen_start() #start the timer screen
                return validated_user_id
            else:
                app.enableEnter(press)
                app.warningBox("Error !", "Invalid Credentials", parent=None)
                return 0
    else:
        app.enableEnter(press)
        app.warningBox("Error !", "Invalid Credentials", parent=None)
        return 0
    #close the cursor and database connection
    cursor.close()
    connect_db.close()

# load the projects
def load_projects():
    connect_db = start_db()
    if(connect_db):
        global usr
        global user_id
        global projects
        global project_id
        user_id = login()
        if(user_id > 0):
            check_total_time()
            incomplete_record_alert()
            if not projects and not project_id:
                cursor = connect_db.cursor()
                cursor.execute("SELECT * FROM projects WHERE project_approval = 1;") # get all approved projects
                result_array = cursor.fetchall()
                project_id.append(0)
                projects.append('- Select Project -')
                for row in result_array:
                    project_id.append(row[0]) # get project ids to array
                    projects.append(row[1]) # get project names to array
                #close the cursor and database connection
                cursor.close()
                connect_db.close()
            #write in the log file for login
            current_time = datetime.now()
            date_time = current_time.strftime('%d-%b-%Y-%H:%M:%S')
            path = create_file()
            log_file =  open(path, "a+")
            log_file.write("************* %s logged in %s ************\n\n"%(usr, date_time))
            log_file.close()
            # strt Projects screen
            screen_project()
        else:
            print "Error"
            connect_db.close()
            
# function for submit login dialogbox
def press(button):
    if button == "Cancel":
        app.stop()
    else:
        global usr
        global pwd
        usr = app.getEntry("Username :")
        pwd = app.getEntry("Password :")
        if(usr == "" or pwd == ""):
            app.warningBox("Error !", "Please fill the fields", parent=None)
            app.enableEnter(press)
        else:
            app.disableEnter()
            load_projects()        

#start the GUI application
app = gui("BCTimer", "400x215")

#create status bar to display user name
app.addStatusbar(fields=1, side="RIGHT")
app.setStatusbarWidth(15, field=0)

#start the login screen
screen_login()

# confirm stopping the application
app.setStopFunction(check_stop)

# splash screen
#app.showSplash("BCPortal - Timer", fill='red', stripe='#222222', fg='white', font=44)

# start the GUI
app.go()

#"SELECT * FROM time WHERE user_id=%s AND work_date=%s AND end_time IS NULL ORDER BY time_id DESC ;",(user_id,date)
