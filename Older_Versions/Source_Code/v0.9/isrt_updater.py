'''
ISRT - Insurgency Sandstorm RCON Tool Updater, Madman
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Thanks to Helsing, Mamba, Sparkie and Stuermer for the pre-release testing - I appreciate that very much!
------------------------------------------------------------------
Importing required classes and libraries
------------------------------------------------------------------'''
import os
import sys
import time
import sqlite3
import shutil
import zipfile
import ctypes
import urllib.request
from datetime import datetime
from pathlib import Path
import psutil
import requests
from PyQt5 import QtGui, QtWidgets
from bin.isrt_updater import Ui_Updater


#
# Set Dev Mode during development here, to not mix the register and other stuff
#

##################################################################################
##################################################################################
running_dev_mode = 0
##################################################################################
##################################################################################



class Updater_GUI(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        # Global variable setup
        global running_dev_mode
        # Gui Setup
        super().__init__(*args, **kwargs)
        self.ugui = Ui_Updater()
        self.ugui.setupUi(self)

        self.definitions()
        self.get_versions()
        # Reset Progressbar
        self.ugui.updater_progressbar.setValue(0)

    # Check if  ISRT or Monitor is running
    def check_running_progs(self):
        runlist = []
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
            except Exception:
                pass
            if p.name().startswith("isrt.exe") or p.name().startswith("isrt_monitor.exe"):
                runlist.append(p.name())
        runcounter = len(runlist)
        self.runlist = runlist

        def close_processes():
            for processname in self.runlist:
                os.system("taskkill /F /IM " + str(processname) + "> nul")
            self.ugui.label_output_window_update.clear()
            self.ugui.label_output_window_update.append("Killed all ISRT processes to prevent the update from breaking the app!")
            self.install_update()

        if runcounter >= 1:
            msg = QtWidgets.QMessageBox()
            msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("ISRT Updater Error Message")
            msg.setText("ISRT Main or Monitor running - close them first!")
            close_button = msg.addButton(
                        "Close it automatically", msg.ActionRole)
            close_button.clicked.connect(close_processes)
            quit_button = msg.addButton(
                "Quit Updater", msg.ActionRole)
            quit_button.clicked.connect(self.close_updater)
            msg.exec_()
        else:
            self.ugui.label_output_window_update.clear()
            self.install_update()

    # Setup all GUI elements and Paths
    def definitions(self):
        # Create variables
        self.update_url = "http://www.isrt.info/version/update/"
        # Create buttons
        self.ugui.btn_update_check.clicked.connect(self.get_versions)
        self.ugui.btn_update_backup.clicked.connect(self.create_db_backup)
        self.ugui.btn_update_install.clicked.connect(self.check_running_progs)
        # File and directory setup
        self.installdir = Path(__file__).absolute().parent
        self.dbdir = str(self.installdir / './db/')
        self.dbfile = str(self.installdir / './db/isrt_data.db')
        print(self.dbdir)
        print(self.dbfile)
        # Database connection setup
        self.conn = sqlite3.connect(self.dbfile)
        self.c = self.conn.cursor()

    # Get all versions and the Update Text
    def get_versions(self):
        self.ugui.label_output_window_update.clear()
        self.ugui.updater_progressbar.setValue(10)
        self.c.execute("select version from configuration")
        version_res = self.c.fetchone()
        self.conn.commit()
        self.current_version = (str(version_res[0]))
        self.ugui.lbl_updater_current_version.setText(self.current_version)
        self.ugui.label_output_window_update.append("Loaded current version from DB")
        self.ugui.updater_progressbar.setValue(20)
        try:
            new_version_available = urllib.request.urlopen(
            "http://www.isrt.info/version/version_check2.txt")
            self.ugui.updater_progressbar.setValue(30)
            update_text = urllib.request.urlopen(
            "http://www.isrt.info/version/update_message2.txt")
            self.ugui.updater_progressbar.setValue(40)
            self.ugui.label_output_window_update.append("Loaded available version from Website")
            self.ugui.label_output_window_update.append("Loaded Update Text from Website")
        except Exception:
            new_version_available = None
            update_text = "No Update Info vailable"
            self.ugui.updater_progressbar.setValue(50)
            err0 = "Unable to load Version and Update Text from Website"
            err0 = '<span style=\" color: #ff0000;\">%s</span>' % err0
            self.ugui.label_output_window_update.append(err0)

        if new_version_available:
            self.ugui.updater_progressbar.setValue(60)
            for line in new_version_available.readlines():
                line = line.decode("utf-8")
                line = line.strip('\n')
                self.new_version_available = line
        if update_text:
            self.ugui.updater_progressbar.setValue(60)
            for line2 in update_text.readlines():
                line2 = line2.decode("utf-8")
                line2 = line2.strip('\n')
                update_text_public = line2
        self.ugui.updater_progressbar.setValue(70)

        self.ugui.lbl_update_text.setText(update_text_public)
        self.ugui.lbl_updater_available_version.setText(self.new_version_available)
        self.ugui.updater_progressbar.setValue(80)
        if self.new_version_available != self.current_version:
            self.ugui.lbl_updater_available_version.setStyleSheet("color: red;")
        else:
            self.ugui.lbl_updater_available_version.setStyleSheet("color: green;")

        def isAdmin():
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            return is_admin
        isAdmin()
        self.ugui.updater_progressbar.setValue(90)
        if isAdmin():
            self.ugui.label_output_window_update.append("Running with Admin privileges - no exceptions expected!")
        else:
            err1 = "You are not an Admin - if you run into permission errors, consider executing the Updater with admin privileges!"
            err1 = '<span style=\" color: #0000ff;\">%s</span>' % err1
            self.ugui.label_output_window_update.append(err1)
        self.ugui.updater_progressbar.setValue(100)
        time.sleep(0.3)
        self.ugui.updater_progressbar.setValue(0)

    # DB Backup Routine
    def create_db_backup(self):
        # Define a timestamp format for backup
        FORMAT2 = '%Y%m%d%H%M%S'
        db_backup_directory = (str(self.dbdir) + "\\")
        db_source_filename = (str(self.dbfile))
        self.ugui.updater_progressbar.setValue(10)
        db_backup_filename = (db_backup_directory +
                                datetime.now().strftime(FORMAT2) + '_isrt_data_update_backup.db')
        shutil.copy2(str(db_source_filename), str(db_backup_filename))
        self.ugui.updater_progressbar.setValue(50)
        dbb_filename = db_backup_filename.replace("\\", "/")
        self.ugui.label_output_window_update.append(
            "Database Backup created at: \n" + dbb_filename)
        self.ugui.updater_progressbar.setValue(100)
        time.sleep(0.3)
        self.ugui.updater_progressbar.setValue(0)

    # Update files
    def update_files(self):
        self.backup_error = 0
        # Check if new files list contains anything, and if go on
        self.ugui.label_output_window_update.append("Creating update file list from regster!")

        # Check is the Update file list is there
        isfile = os.path.isfile(self.temp_path + f"update_{self.new_version_available}.txt")

        # If it is there, delete and re-create it, or just write and open it
        if isfile is True:
            try:
                self.ugui.updater_progressbar.setValue(25)
                os.remove(self.temp_path + f"update_{self.new_version_available}.txt")
                update_file  = open(self.temp_path + f"update_{self.new_version_available}.txt", "a+")
                self.ugui.updater_progressbar.setValue(27)
            except PermissionError:
                err2 = "Cannot create the Update File List - please check if it's in use by another program and restart!"
                err2 = '<span style=\" color: #ff0000;\">%s</span>' % err2
                self.ugui.label_output_window_update.append(err2)
                self.ugui.updater_progressbar.setValue(27)
        else:
            try:
                update_file  = open(self.temp_path + f"update_{self.new_version_available}.txt", "a+")
                self.ugui.updater_progressbar.setValue(30)
            except PermissionError:
                err3 = "Cannot create the Update File List - please check if the temp directory exists and restart!"
                err3 = '<span style=\" color: #ff0000;\">%s</span>' % err3
                self.ugui.label_output_window_update.append(err3)
                self.ugui.updater_progressbar.setValue(30)

        # Write the new files list into the update file
        for line in self.new_files_list.readlines():
            line = line.decode("utf-8")
            line = line.strip('\n')
            new_file = line
            update_file.write(new_file + "\n")
        self.ugui.updater_progressbar.setValue(35)
        # Close the update file list
        update_file.close()
        self.ugui.updater_progressbar.setValue(40)

        # Download the new files list if available
        update_file_download  = open(self.temp_path + f"update_{self.new_version_available}.txt", "r")
        for download in update_file_download.readlines():
            try:
                download = download.strip('\n')
                download_new_file = download
                dl_file = (self.update_url + download_new_file)
                r = requests.get(dl_file)
                with open(self.temp_path + download_new_file, 'wb') as output_file:
                    output_file.write(r.content)
                self.ugui.label_output_window_update.append("Downloading Update for new version...")
                self.ugui.updater_progressbar.setValue(45)
            # Handle an exception error
            except PermissionError as f:
                err4 = f"Cannot write downloaded files - please check file and folder permissions - {f}"
                err4 = '<span style=\" color: #ff0000;\">%s</span>' % err4
                self.ugui.label_output_window_update.append(err4)
                self.ugui.updater_progressbar.setValue(50)
        self.ugui.label_output_window_update.append("Download complete!")
        # Close file and start updating
        self.ugui.updater_progressbar.setValue(55)
        update_file_download.close()
        self.ugui.label_output_window_update.append("Unzipping new files...")

        # Unzip update - remove source files
        update_zip = (self.temp_path + download_new_file)
        with zipfile.ZipFile(update_zip, 'r') as zip_ref:
            zip_ref.extractall(self.temp_path)
        self.ugui.label_output_window_update.append("Unzipping complete - removing sources!")
        self.ugui.updater_progressbar.setValue(65)
        try:
            os.remove(update_zip)
            os.remove(self.temp_path + f"update_{self.new_version_available}.txt")
        except PermissionError:
            err5 = "Permission Error when trying to delete the update zip file!"
            err5 = '<span style=\" color: #ff0000;\">%s</span>' % err5
            self.ugui.label_output_window_update.append(err5)
        self.ugui.updater_progressbar.setValue(60)

        self.ugui.label_output_window_update.append("Reading new files list and checking for update tasks!")
        self.ugui.updater_progressbar.setValue(70)

        # Start the updating itself
        source_dir = self.temp_path
        target_dir = (str(self.installdir) + "\\")
        self.ugui.label_output_window_update.append(f"Update source folder: {source_dir}")
        self.ugui.label_output_window_update.append(f"Update target folder: {target_dir}")
        issqlfile = os.path.isfile(self.temp_path + "_update_list.txt")
        self.ugui.updater_progressbar.setValue(75)
        if issqlfile is True:
            with open(self.temp_path + "_update_list.txt", 'r') as update_file:
                for handle_line in update_file.readlines():
                    handle_line = handle_line.strip('\n')
                    new_file_handling = handle_line
                    file_action = new_file_handling.split(",")
                    if file_action[0] == "none" or file_action[0] == "None":
                        self.ugui.label_output_window_update.append("No file update required")
                        self.ugui.updater_progressbar.setValue(90)
                    else:
                        file_method = file_action[0]
                        handled_file_temp = file_action[1]
                        handled_file = handled_file_temp.replace("/", "\\")
                        file_update_error = 0
                        if file_method == "add" or file_method == "Add":
                            action = "Adding"
                            report_action = (action + " " + handled_file + " to " + target_dir)
                            try:
                                shutil.move(source_dir + handled_file, target_dir + handled_file)
                                self.ugui.updater_progressbar.setValue(75)
                            except PermissionError:
                                err6 = f"Unable to add {handled_file} due to a Permission Error!"
                                err6 = '<span style=\" color: #ff0000;\">%s</span>' % err6
                                self.ugui.label_output_window_update.append(err6)
                                self.ugui.updater_progressbar.setValue(75)
                                self.backup_error = 1
                                file_update_error = 1
                            except FileNotFoundError:
                                err7 = f"Unable to add {handled_file} - file wasn't vailable!"
                                err7 = '<span style=\" color: #ff0000;\">%s</span>' % err7
                                self.ugui.label_output_window_update.append(err7)
                                self.ugui.updater_progressbar.setValue(75)
                                file_update_error = 1
                                self.backup_error = 1
                        elif file_method == "delete" or file_method == "Delete":
                            action = "Deleting"
                            report_action = (action + " " + handled_file + " from " + target_dir)
                            try:
                                os.remove(target_dir + handled_file)
                                self.ugui.updater_progressbar.setValue(75)
                            except PermissionError:
                                err8 = f"Unable to delete {handled_file} due to a Permission Error!"
                                err8 = '<span style=\" color: #ff0000;\">%s</span>' % err8
                                self.ugui.label_output_window_update.append(err8)
                                self.ugui.updater_progressbar.setValue(75)
                                file_update_error = 1
                                self.backup_error = 1
                            except FileNotFoundError:
                                err9 = f"File not Found: {handled_file} disregarding - not needed anyway!"
                                err9 = '<span style=\" color: #0000ff;\">%s</span>' % err9
                                self.ugui.label_output_window_update.append(err9)
                                self.ugui.updater_progressbar.setValue(75)
                        elif file_method == "replace" or file_method == "Replace":
                            action = "Replacing"
                            report_action = (action + " " + handled_file + " in " + target_dir)
                            try:
                                try:
                                    os.remove(target_dir + handled_file)
                                    self.ugui.updater_progressbar.setValue(75)
                                except FileNotFoundError:
                                    err10 = f"File not Found: {handled_file} disregarding - not needed anyway!"
                                    err10 = '<span style=\" color: #0000ff;\">%s</span>' % err10
                                    self.ugui.updater_progressbar.setValue(75)
                                    self.ugui.label_output_window_update.append(err10)
                                shutil.move(source_dir + handled_file, target_dir + handled_file)
                            except PermissionError:
                                err11 = f"Unable to replace {handled_file} due to a Permission Error!"
                                err11 = '<span style=\" color: #ff0000;\">%s</span>' % err11
                                self.ugui.label_output_window_update.append(err11)
                                self.ugui.updater_progressbar.setValue(75)
                                self.backup_error = 1
                                file_update_error = 1
                            except FileNotFoundError:
                                err12 = f"Unable to replace {handled_file} - file wasn't vailable!"
                                err12 = '<span style=\" color: #ff0000;\">%s</span>' % err12
                                self.ugui.label_output_window_update.append(err12)
                                self.ugui.updater_progressbar.setValue(75)
                                self.backup_error = 1
                                file_update_error = 1
                        else:
                            err13 = f"Alert - UNKNOWN ACTION - not doing anything with {handled_file} - please report it!"
                            err13 = '<span style=\" color: #ff0000;\">%s</span>' % err13
                            self.ugui.updater_progressbar.setValue(75)
                            report_action = (err13)
                            self.backup_error = 1
                        self.ugui.label_output_window_update.append(report_action)

            # Report status
            if file_update_error == 0:
                err14 = "No critical errors detected - all necessary files updated!"
                err14 = '<span style=\" color: #009900;\">%s</span>' % err14
                self.ugui.label_output_window_update.append(err14)
                self.ugui.updater_progressbar.setValue(80)
            else:
                err15 = "There were errors during Update, please check above messages!"
                err15 = '<span style=\" color: #ff0000;\">%s</span>' % err15
                self.backup_error = 1
                self.ugui.label_output_window_update.append(err15)
                self.ugui.updater_progressbar.setValue(80)
        else:
            self.ugui.label_output_window_update.append("No files require an update!")
            self.ugui.updater_progressbar.setValue(80)

    # Update Database
    def update_db(self):
        self.ugui.updater_progressbar.setValue(85)
        # Check is the Update SQL file is there
        issqlfile = os.path.isfile(self.temp_path + "_update.sql")
        if issqlfile is True:
            self.backup_db_error = 0
            try:
                try:
                    self.ugui.label_output_window_update.append("Updating Database")
                    self.create_db_backup()
                    self.ugui.updater_progressbar.setValue(88)
                except Exception:
                    err16 = "Database Backup failed!"
                    err16 = '<span style=\" color: #ff0000;\">%s</span>' % err16
                    self.ugui.label_output_window_update.append(err16)
                    self.backup_db_error = 1
                    self.ugui.updater_progressbar.setValue(88)
                if self.backup_db_error == 1:
                    err17 = "DB Backup failed - stopping DB Backup - please manually create a backup and try to update again!"
                    err17 = '<span style=\" color: #ff0000;\">%s</span>' % err17
                    self.ugui.label_output_window_update.append(err17)
                else:
                    self.ugui.updater_progressbar.setValue(90)
                    with open(self.temp_path + "_update.sql", 'r') as update_file:
                        for sql_handle_line in update_file.readlines():
                            sql_handle_line = sql_handle_line.strip('\n')
                            new_sql_handling = sql_handle_line
                            if new_sql_handling == "none" or new_sql_handling == "None":
                                self.ugui.label_output_window_update.append("No Database update required - finishing!")
                            else:
                                try:
                                    self.c.execute(new_sql_handling)
                                    self.conn.commit()
                                    self.ugui.label_output_window_update.append(f"SQL Update: {new_sql_handling}")
                                except Exception as e:
                                    err18 = f"An Error occured during update: {e} - DB might be broken now - try to replace the current DB with the Backup and run again, keeping your backup file in a safe area!"
                                    err18 = '<span style=\" color: #ff0000;\">%s</span>' % err18
                                    self.ugui.label_output_window_update.append(err18)
                                    self.backup_db_error = 1
                        err24 = "Database updated successfully!"
                        err24 = '<span style=\" color: #009900;\">%s</span>' % err24
                        self.ugui.label_output_window_update.append(err24)
                        self.ugui.updater_progressbar.setValue(95)
            except Exception:
                err19 = "Cannot update the database due to a Permission Error - ensure no other program is accessing it!"
                err19 = '<span style=\" color: #ff0000;\">%s</span>' % err19
                self.ugui.label_output_window_update.append(err19)
                self.backup_db_error = 1
                self.ugui.updater_progressbar.setValue(97)
        else:
            self.ugui.label_output_window_update.append("No Database update required!")
            self.ugui.updater_progressbar.setValue(97)

    # Install Update method
    def install_update(self):
        # Define the basics
        self.ugui.label_output_window_update.append("Updater started...relax for a moment!")
        self.ugui.updater_progressbar.setValue(5)
        self.temp_path = (str(self.installdir) + "\\tmp\\")
        self.ugui.label_output_window_update.append("Creating temporary update directory")
        # Check if TMP Dir is already there - if not create it
        isdir = os.path.isdir(self.temp_path)
        if isdir is False:
            try:
                os.mkdir(self.temp_path)
            except PermissionError:
                err20 = "Permission Error when trying to create temporary update directory!"
                err20 = '<span style=\" color: #ff0000;\">%s</span>' % err20
                self.ugui.label_output_window_update.append(err20)
        self.ugui.updater_progressbar.setValue(10)

        # Get the new files list for downloading
        try:
            self.new_files_list = urllib.request.urlopen(
                "http://www.isrt.info/version/new_files_list.txt")
            self.ugui.updater_progressbar.setValue(15)
            self.ugui.label_output_window_update.append("Update register loaded.")
        except Exception:
            self.new_files_list = None
            self.ugui.updater_progressbar.setValue(15)
            err21 = "Error during update register donwload!"
            err21 = '<span style=\" color: #ff0000;\">%s</span>' % err21
            self.ugui.label_output_window_update.append(err21)

        if self.new_files_list is not None:
            self.ugui.updater_progressbar.setValue(20)
            self.update_files()
            self.update_db()
            # Remove the temporary directory with all in it
            self.ugui.label_output_window_update.append("Removing temporary directory")
            if running_dev_mode == 0:
                shutil.rmtree(self.temp_path)
            self.ugui.updater_progressbar.setValue(98)

            if self.backup_db_error == 1 or self.backup_error == 1:
                err26 = "There were errors during update - please check and retry after solving or report to support@isrt.info!"
                err26 = '<span style=\" color: #009900;\">%s</span>' % err26
                self.ugui.label_output_window_update.append(err26)
            else:
                err25 = f"Update completed, you are now on version: {self.new_version_available}!"
                err25 = '<span style=\" color: #009900;\">%s</span>' % err25
                self.ugui.label_output_window_update.append(err25)

            self.ugui.updater_progressbar.setValue(100)
            self.ugui.lbl_updater_current_version.setText(self.new_version_available)
        else:
            err22 = "No new files available - possible error on server side - quiting!"
            err22 = '<span style=\" color: #0000ff;\">%s</span>' % err22
            self.ugui.label_output_window_update.append(err22)
            self.ugui.updater_progressbar.setValue(100)

        # Re-check the version
        self.c.execute("select version from configuration")
        version_res = self.c.fetchone()
        self.current_version = (str(version_res[0]))
        if self.new_version_available != self.current_version:
            self.ugui.lbl_updater_available_version.setStyleSheet("color: red;")
        else:
            self.ugui.lbl_updater_available_version.setStyleSheet("color: green;")
        # Sleep shortly to keep things in the flow
        time.sleep(0.5)

        # Reset the progress bar
        self.ugui.updater_progressbar.setValue(0)

    # Close Updater per Button
    def close_updater(self):
        self.conn.commit()
        self.conn.close()
        self.close()

    # Close Event Handling
    def closeEvent(self, event): # pylint: disable=unused-argument
        self.close()

# Main programm call
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Updater = QtWidgets.QWidget()
    ugui = Updater_GUI()
    ugui.show()
    sys.exit(app.exec_())
