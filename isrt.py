'''
ISRT - Insurgency Sandstorm RCON Tool; August 2021, Madman
Website: https://github.com/olli-e/ISRT/releases
Current Version: v1.5
Database: ./db/isrt_data.db
Monitor: ./isrt_monitor.py/exe
This is open Source, you may use, copy, modify it as you wish, but you may not create anything from or with my code,
that will earn you money - no selling of any kind of stuff with my code, not even parts of it!
------------------------------------------------------------------
Importing required classes and libraries
------------------------------------------------------------------'''
import os
import platform
import random
import sqlite3
import sys
import requests

from datetime import datetime
from pathlib import Path

import psutil

from PyQt5 import QtGui, QtWidgets
import modules.map_manager as maps
import modules.config as conf

import modules.server_manager as server
import modules.custom_elements as custom
import modules.definitions as my_def

from bin.isrt_db_gui import Ui_db_importer_gui
from bin.isrt_gui import Ui_ISRT_Main_Window


#
# Set Dev Mode during development here, to not mix the register and other stuff
#

##################################################################################
##################################################################################
running_dev_mode = 0
running_dev_mode_dbi = 0
##################################################################################
##################################################################################


#
# DB Importer GUI Handler
#
class dbgui(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        # Gui Setup
        super().__init__(*args, **kwargs)
        self.dbgui = Ui_db_importer_gui()
        self.dbgui.setupUi(self)
        # Database connection setup
        self.dbdir = Path(__file__).absolute().parent
        self.dbconn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.dbconn.cursor()
        self.dbi_path = None
        self.dbgui.btn_dbg_close.clicked.connect(self.close_dbg)
        self.dbgui.btn_dbi_select_database.clicked.connect(
            lambda: self.DBI_executor("select_db"))
        self.dbgui.btn_dbi_import_database.clicked.connect(
            lambda: self.DBI_executor("replace_db"))
    # Grep all Servers from old DB and import them

    def DBI_executor(self, db_action):
        if db_action == 'select_db':
            db_select_directory = (str(self.dbdir) + '\\db\\')
            self.dbi_path = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select Database', db_select_directory, '*.db',)
            self.dbgui.label_dbi_selected_db.setText(self.dbi_path[0])
        elif db_action == 'replace_db':
            server.create_db_backup()
            msg13 = QtWidgets.QMessageBox()
            msg13.setWindowIcon(QtGui.QIcon(":/img/img/isrt.ico"))
            msg13.setIcon(QtWidgets.QMessageBox.Information)
            msg13.setWindowTitle("ISRT DB Backup created")
            msg13.setText(
                "I created a backup of your existing \nRestarting ISRT!")
            msg13.exec_()
            if self.dbi_path and self.dbi_path[0].endswith(".db"):
                # Database connection setup for Importing
                dbimportdir = self.dbi_path[0]
                connimport = sqlite3.connect(dbimportdir)
                cidb = connimport.cursor()
                cidb.execute("select * FROM server")
                dbimport_result = cidb.fetchall()
                connimport.commit()
                try:
                    cidb.execute("select version FROM configuration")
                    dbi_result = cidb.fetchone()
                    old_db_version_temp = dbi_result[0]
                    old_db_version = str(old_db_version_temp)
                    connimport.commit()
                    connimport.close()
                except Exception:
                    old_db_version = None
                if old_db_version:
                    if old_db_version.startswith("0.8") or old_db_version.startswith("0.9") or old_db_version.startswith("1."):
                        self.c.execute("DELETE FROM server")
                        self.dbconn.commit()
                        for import_result in dbimport_result:
                            import_id = import_result[0]
                            import_server_alias = import_result[1]
                            import_server_ip = import_result[2]
                            import_server_queryport = import_result[3]
                            import_server_rconport = import_result[4]
                            import_server_rconpw = import_result[5]
                            self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                                           'id': import_id, 'alias': import_server_alias, 'ipaddress': import_server_ip, 'queryport': import_server_queryport, 'rconport': import_server_rconport, 'rconpw': import_server_rconpw})
                        self.dbconn.commit()
                        msg3 = QtWidgets.QMessageBox()
                        msg3.setWindowIcon(QtGui.QIcon(":/img/img/isrt.ico"))
                        msg3.setIcon(QtWidgets.QMessageBox.Information)
                        msg3.setWindowTitle("ISRT DB imported")
                        msg3.setText(
                            "Server Import Successful\nRestarting ISRT!")
                        msg3.exec_()
                        self.dbi_path = ''
                        self.dbi_path = None
                        dbgsetoff = 0
                        self.c.execute("UPDATE configuration SET import=:importval", {
                                       'importval': dbgsetoff})
                        self.dbconn.commit()
                        self.dbconn.close()
                        restart_program()
                    elif old_db_version == "0.7":
                        self.c.execute("DELETE FROM server")
                        self.dbconn.commit()
                        id_counter = 1
                        for import_result in dbimport_result:
                            import_id = id_counter
                            import_server_alias = import_result[0]
                            import_server_ip = import_result[1]
                            import_server_queryport = import_result[2]
                            import_server_rconport = import_result[3]
                            import_server_rconpw = import_result[4]
                            self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                                           'id': import_id, 'alias': import_server_alias, 'ipaddress': import_server_ip, 'queryport': import_server_queryport, 'rconport': import_server_rconport, 'rconpw': import_server_rconpw})
                            id_counter += 1
                        self.dbconn.commit()
                        msg4 = QtWidgets.QMessageBox()
                        msg4.setWindowIcon(QtGui.QIcon(":/img/img/isrt.ico"))
                        msg4.setIcon(QtWidgets.QMessageBox.Information)
                        msg4.setWindowTitle("ISRT DB imported")
                        msg4.setText(
                            "Server Import Successful\nRestarting ISRT!")
                        msg4.exec_()
                        self.dbi_path = ''
                        self.dbi_path = None
                        dbgsetoff = 0
                        self.c.execute("UPDATE configuration SET import=:importval", {
                                       'importval': dbgsetoff})
                        self.dbconn.commit()
                        self.dbconn.close()
                        restart_program()
                else:
                    msg5 = QtWidgets.QMessageBox()
                    msg5.setWindowIcon(QtGui.QIcon(":/img/img/isrt.ico"))
                    msg5.setIcon(QtWidgets.QMessageBox.Warning)
                    msg5.setWindowTitle("ISRT Error Message")
                    msg5.setText(
                        "The database is from before v0.7, which cannot replace this version's DB.\n\nYou can import the old servers using 'Add'-Function in the Server Manager!")
                    msg5.exec_()

            else:
                msg6 = QtWidgets.QMessageBox()
                msg6.setWindowIcon(QtGui.QIcon(":/img/img/isrt.ico"))
                msg6.setIcon(QtWidgets.QMessageBox.Warning)
                msg6.setWindowTitle("ISRT Error Message")
                msg6.setText(
                    "No file selected or wrong file type\nPlease select a database first!")
                msg6.exec_()

    # Handle Close per Button
    def close_dbg(self):
        self.dbi_path = None
        dbgsetoff = 0
        self.dbdir = Path(__file__).absolute().parent
        self.dbconn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.dbconn.cursor()
        self.c.execute("UPDATE configuration SET import=:importval", {
                       'importval': dbgsetoff})
        self.dbconn.commit()
        self.dbconn.close()
        self.close()

    # Handle Close Event
    def closeEvent(self, event):  # pylint: disable=unused-argument
        self.dbi_path = None
        dbgsetoff = 0
        self.dbdir = Path(__file__).absolute().parent
        self.dbconn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.dbconn.cursor()
        self.c.execute("UPDATE configuration SET import=:importval", {
                       'importval': dbgsetoff})
        self.dbconn.commit()
        self.dbconn.close()
        self.close()



#
# Main GUI Handlers
#
class maingui(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        # Global variable setup
        global running_dev_mode
        self.running_dev_mode = running_dev_mode
        # Gui Setup
        super().__init__(*args, **kwargs)
        self.gui = Ui_ISRT_Main_Window()
        self.gui.setupUi(self)

        # Database connection setup
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
        self.data_path = None
        self.datapath = None


        # Execute the pre-requisites and set the configuration
        my_def.action_elements(self)
        my_def.pre_vars(self)
        my_def.set_version(self)
        my_def.clientid(self)
        conf.get_it(self)
        server.fill_server_elements(self)
        custom.fill_dropdown_and_list(self)
        maps.fill_map_manager_dropdown(self)



    # Close Event handling
    def closeEvent(self, event):
        self.c.execute("select quitbox from configuration")
        self.conn.commit()
        quitbox_result = self.c.fetchone()

        if self.running_dev_mode == 0:
            if quitbox_result[0] == 1:
                choice = QtWidgets.QMessageBox.warning(
                    self, 'Quit Message!', "Really close the app?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if choice == QtWidgets.QMessageBox.Yes:
                    self.conn.close()
                    self.close()
                else:
                    event.ignore()
            else:
                self.conn.close()
                self.close()
        else:
            self.conn.close()
            self.close()



#
# Main program
#
if __name__ == "__main__":
    # Define path to installation
    installdir = Path(__file__).absolute().parent
    # Database connection setup
    dbfile = (str(installdir / 'db/isrt_data.db'))
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    # Grep or define start variables
    c.execute(
        "select startcounter, version, client_id, import from configuration")
    check_startvars = c.fetchall()
    startvars = check_startvars[0]
    conn.commit()
    startcounter = startvars[0]
    current_version = str(startvars[1])
    client_id = startvars[2]
    show_importer = startvars[3]
    runcheck = 1
    runlist = []
    # Decide if self-restart is okay at first start and exempted from runcheck
    if startcounter <= 2:
        new_startcounter = 1
        c.execute("update configuration set startcounter=:newstartcounter", {
                  'newstartcounter': new_startcounter})
        conn.commit()
        # Check if running in Dev Mode
        if running_dev_mode == 1:
            print("************************************")
            print("*                                  *")
            print("* Running in DEVELOPMENT MODE!!!!! *")
            print("*                                  *")
            print("************************************")
            client_hash = random.getrandbits(64)
            FORMAT = '%d%m%y'
            datestamp = datetime.now().strftime(FORMAT)
            client_os = platform.system()
            client_id_new = (client_os + "_" + current_version + "_" + datestamp + "_" + str(client_hash))
            
            c.execute("UPDATE configuration SET client_id=:cid",
                      {'cid': str(client_id_new)})
            conn.commit()
            client_id = client_id_new
        else:
            # Check if Client ID is already existing
            if client_id == "" or client_id is None:
                client_hash = random.getrandbits(128)
                FORMAT = '%d%m%y'
                datestamp = datetime.now().strftime(FORMAT)
                client_os = platform.system()
                client_id_new = (client_os + "_" + current_version + "_" + datestamp + "_" + str(client_hash))
                c.execute("update configuration set client_id=:cid",
                          {'cid': str(client_id_new)})
                conn.commit()
                client_id = client_id_new


    else:
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
            except Exception:
                pass
            if p.name().startswith("isrt.exe"):
                runlist.append(p.name())
        runcounter = len(runlist)
        if runcounter >= 2:
            runcheck = 0

    # Check if App may run
    if runcheck == 1:
        # Initialize GUIs
        app = QtWidgets.QApplication(sys.argv)
        ISRT_Main_Window = QtWidgets.QWidget()
        db_window = QtWidgets.QWidget()
        mgui = maingui()
        mgui.show()
        conn.close()
                

        if running_dev_mode == 1:
            if running_dev_mode_dbi == 1:
                db_gui = dbgui()
                db_gui.show()

        else:
            # Check if DB Importer shall be shown or not
            if show_importer == 1:
                db_gui = dbgui()
                db_gui.show()


        # Restart on first DB-Import
        def restart_program():
            python = sys.executable
            os.execl(python, python, * sys.argv)
        sys.exit(app.exec_())

    else:
        # Show Error that app is already running
        app = QtWidgets.QApplication(sys.argv)
        msg = QtWidgets.QMessageBox()
        msg.setWindowIcon(QtGui.QIcon(":/img/img/isrt.ico"))
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("ISRT Error Message")
        msg.setText("ISRT is already running - exiting!")
        msg.exec_()
        conn.close()
