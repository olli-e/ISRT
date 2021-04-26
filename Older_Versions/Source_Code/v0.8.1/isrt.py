'''
ISRT - Insurgency Sandstorm RCON Tool; 01.02.2021, Madman
In case of questions: isrt@edelmeier.org
Website: http://www.isrt.info
Current Version: v0.9
Database: ./db/isrt_data.db
Monitor: ./isrt_monitor.py/exe
This is open Source, you may use, copy, modify it as you wish - feel free!
Thanks to Helsing and Stuermer for the pre-release testing - I appreciate that very much!
------------------------------------------------------------------
Importing required classes and libraries
------------------------------------------------------------------'''
import os
import platform
import random
import re
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from shutil import copy2

import psutil
import requests
from PIL import Image as pilimg
from PyQt5 import QtCore, QtGui, QtWidgets

import bin.query as query
import bin.SourceQuery as sq
import res_rc
from bin.isrt_db_gui import Ui_db_importer_gui
from bin.isrt_gui import Ui_ISRT_Main_Window
from bin.rcon.console import Console
from bin.rn_gui import Ui_rn_window

# Set Dev Mode during development here, to not mix the register and other stuff
##################################################################################
##################################################################################
running_dev_mode = 1
running_dev_mode_dbi = 0
running_dev_mode_rn = 0
##################################################################################
##################################################################################

'''
------------------------------------------------------------------
------------------------------------------------------------------
'''
# PyQt5 Main UI Initialization
#
# Release Notes GUI Handler


class rngui(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        # Gui Setup
        super().__init__(*args, **kwargs)
        # Database connection setup
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
        self.rngui = Ui_rn_window()
        self.rngui.setupUi(self)
        # Setup Version number and set in About and Main Title
        self.c.execute("Select version from configuration")
        version_temp = self.c.fetchone()
        self.conn.commit()
        version = ("v" + version_temp[0])
        self.rngui.rn_top_layer.setText(QtCore.QCoreApplication.translate("rn_window", f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:600;\">ISRT {version} Release Notes</span></p></body></html>"))
        
        self.rngui.btn_rn_close.clicked.connect(self.close_rn)
    # Close RN per Button

    def close_rn(self):
        if self.rngui.chkbx_show_rn.isChecked():
            rnsetoff = 0
            self.c.execute("UPDATE configuration SET show_rn = :rnset", {
                           'rnset': rnsetoff})
            self.conn.commit()
            self.conn.close()
        self.close()
    # Close Event Handling

    def closeEvent(self, event):
        self.close()


'''
------------------------------------------------------------------
------------------------------------------------------------------
'''
# DB Importer GUI Handler


class dbgui(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        # Gui Setup
        super().__init__(*args, **kwargs)
        self.dbgui = Ui_db_importer_gui()
        self.dbgui.setupUi(self)
        # Database connection setup
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
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
                    old_db_version = float(dbi_result[0])
                    connimport.commit()
                except Exception:
                    old_db_version = None
                if old_db_version:
                    if old_db_version >= 0.8:
                        self.c.execute("DELETE FROM server")
                        self.conn.commit()
                        for import_result in dbimport_result:
                            import_id = import_result[0]
                            import_server_alias = import_result[1]
                            import_server_ip = import_result[2]
                            import_server_queryport = import_result[3]
                            import_server_rconport = import_result[4]
                            import_server_rconpw = import_result[5]
                            self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                                           'id': import_id, 'alias': import_server_alias, 'ipaddress': import_server_ip, 'queryport': import_server_queryport, 'rconport': import_server_rconport, 'rconpw': import_server_rconpw})
                        self.conn.commit()
                        msg = QtWidgets.QMessageBox()
                        msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                        msg.setIcon(QtWidgets.QMessageBox.Information)
                        msg.setWindowTitle("ISRT DB imported")
                        msg.setText(
                            "Server Import Successful\nRestarting ISRT!")
                        msg.exec_()
                        self.dbi_path = ''
                        self.dbi_path = None
                        dbgsetoff = 0
                        self.c.execute("UPDATE configuration SET import=:importval", {
                                       'importval': dbgsetoff})
                        self.conn.commit()
                        self.conn.close()
                        restart_program()
                    elif old_db_version == 0.7:
                        self.c.execute("DELETE FROM server")
                        self.conn.commit()
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
                        self.conn.commit()
                        msg = QtWidgets.QMessageBox()
                        msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                        msg.setIcon(QtWidgets.QMessageBox.Information)
                        msg.setWindowTitle("ISRT DB imported")
                        msg.setText(
                            "Server Import Successful\nRestarting ISRT!")
                        msg.exec_()
                        self.dbi_path = ''
                        self.dbi_path = None
                        dbgsetoff = 0
                        self.c.execute("UPDATE configuration SET import=:importval", {
                                       'importval': dbgsetoff})
                        self.conn.commit()
                        self.conn.close()
                        restart_program()
                else:
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setWindowTitle("ISRT Error Message")
                    msg.setText(
                        "The database is from before v0.7, which cannot replace this version's DB.\n\nYou can import the old servers using 'Add'-Function in the Server Manager!")
                    msg.exec_()

            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    "No file selected or wrong file type\nPlease select a database first!")
                msg.exec_()
    # Handle Close per Button

    def close_dbg(self):
        self.dbi_path = None
        dbgsetoff = 0
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
        self.c.execute("UPDATE configuration SET import=:importval", {
                       'importval': dbgsetoff})
        self.conn.commit()
        self.conn.close()
        self.close()
    # Handle Close Event

    def closeEvent(self, event):
        self.dbi_path = None
        dbgsetoff = 0
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
        self.c.execute("UPDATE configuration SET import=:importval", {
                       'importval': dbgsetoff})
        self.conn.commit()
        self.conn.close()
        self.close()


'''
------------------------------------------------------------------
------------------------------------------------------------------
'''
# Main GUI Handlers


class maingui(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
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

        # Setup Version number and set in About and Main Title
        self.c.execute("Select version from configuration")
        version_temp = self.c.fetchone()
        self.conn.commit()
        version = ("v" + version_temp[0])
        self.setWindowTitle(QtCore.QCoreApplication.translate("ISRT_Main_Window", f"ISRT - Insurgency Sandstorm RCON Tool {version}"))
        self.gui.aboutbody.setText(QtCore.QCoreApplication.translate("ISRT_Main_Window", f"<html><head/><body><p align=\"center\"><span style=\" font-size:22pt; font-weight:600;\">ISRT {version}</span></p><p align=\"center\"><br/></p><p align=\"center\"><span style=\" font-size:16pt;\">Insurgency Sandstorm RCON/Query Tool</span></p><p align=\"center\"><span style=\" font-size:16pt;\">by Olli E. aka </span><a href=\"mailto:madman@isrt.info\"><span style=\" font-size:18pt; text-decoration: underline; color:#0000ff;\">Madman@isrt.info</span></a></p><p align=\"center\"><br/></p><p align=\"center\"><br/></p><p align=\"center\"><span style=\" font-size:16pt;\">Get Support: </span><a href=\"http://www.isrt.info\"><span style=\" font-size:16pt; text-decoration: underline; color:#0000ff;\">http://www.isrt.info</span></a></p><p align=\"center\"><a href=\"https://github.com/olli-e/ISRT-Insurgency-Sandstorm-RCON-Query-Tool\"><span style=\" font-size:16pt; text-decoration: underline; color:#0000ff;\">GitHub</span></a></p><p align=\"center\"><br/></p><p align=\"center\"><span style=\" font-size:14pt;\">Donate for the development of ISRT!</span></p><p align=\"center\"><br/></p><p align=\"center\"><a href=\"https://www.paypal.com/donate?hosted_button_id=RLSPYUNWLYA9Y\"><img src=\":/img/img/paypal.png\"/></a></p><p align=\"center\"><br/></p><p align=\"center\"><span style=\" font-size:16pt;\">Report issues </span><a href=\"https://github.com/olli-e/ISRT-Insurgency-Sandstorm-RCON-Query-Tool/issues\"><span style=\" font-size:16pt; text-decoration: underline; color:#0000ff;\">here</span></a><br/></p><p align=\"center\"><a href=\"https://github.com/olli-e/ISRT-Insurgency-Sandstorm-RCON-Query-Tool/blob/main/LICENSE\"><span style=\" font-size:14pt; text-decoration: underline; color:#0000ff;\">GNU/Public License Software</span></a></p></body></html>"))
        
        # Setup ISRT Monitor Call

        def call_monitor():
            # Check which version of OS is ISRT running on
            os_running = platform.system()
            # If in Dev Mode, use the Python variant
            if self.running_dev_mode == 1:
                #os.system(f"python {self.dbdir}/isrt_monitor.py")
                subprocess.Popen(['python', f'{self.dbdir}/isrt_monitor.py'])
            else:
                # If on Windows, use the exe-file
                if os_running == "Windows":
                    subprocess.Popen(["isrt_monitor.exe"])
                else:
                    # If on Linux or Mac, use the python file
                    subprocess.Popen(
                        ['python', f'{self.dbdir}/isrt_monitor.py'])
        # Open Explorer Backup Window

        def open_explorer():
            fulldir = (str(self.dbdir / 'db/'))
            os.system(f'start %windir%\\explorer.exe "{fulldir}"')

        def clear_main_rcon():
            self.gui.label_output_window.clear()
            self.gui.label_rconcommand.clear()
        
        def clear_server_manager():
            self.gui.server_alias.clear()
            self.gui.server_ip.clear()
            self.gui.server_query.clear()
            self.gui.server_rconport.clear()
            self.gui.server_rconpw.clear()
            self.gui.btn_server_delete.setEnabled(False)
            self.gui.btn_server_modify.setEnabled(False)

        # Define buttons and menu items including their functionalities
        self.gui.btn_main_adminsay.clicked.connect(self.adminsay)
        self.gui.btn_main_exec_query.clicked.connect(self.checkandgoquery)
        self.gui.btn_main_clear_rcon.clicked.connect(clear_main_rcon)
        self.gui.btn_server_clear.clicked.connect(clear_server_manager)
        self.gui.btn_exec_open_bck_dir.clicked.connect(open_explorer)
        self.gui.btn_main_open_server_monitor.clicked.connect(call_monitor)
        self.gui.btn_main_exec_rcon.clicked.connect(self.checkandgorcon)
        self.gui.btn_cust_delete_selected.clicked.connect(
            self.custom_command_clear_selected)
        self.gui.btn_cust_delete_all.clicked.connect(
            self.custom_command_clear_all)
        self.gui.btn_save_settings.clicked.connect(self.save_settings)
        self.gui.btn_mapmgr_add.clicked.connect(self.add_new_map)
        self.gui.btn_mapmgr_save.clicked.connect(self.save_existing_map)
        self.gui.btn_mapmgr_select_day_image.clicked.connect(
            lambda: self.select_map_pic("day"))
        self.gui.btn_mapmgr_select_night_image_2.clicked.connect(
            lambda: self.select_map_pic("night"))
        self.gui.btn_mapmgr_delete.clicked.connect(self.delete_custom_map)
        # self.gui.btn_main_copytoclipboard.clicked.connect(self.copy2clipboard)
        self.gui.btn_main_drcon_changemap.clicked.connect(self.map_changer)
        self.gui.btn_add_cust_command.clicked.connect(
            self.add_custom_command_manually)
        self.gui.btn_exec_db_backup.clicked.connect(self.create_db_backup)
        self.gui.btn_main_add_server_db.clicked.connect(
            self.add_server_directly)
        self.gui.btn_mapmgr_clear.clicked.connect(self.clear_map_manager)
        # Set client id
        self.c.execute("select client_id from configuration")
        client = self.c.fetchone()
        self.conn.commit()
        self.client_id = client[0]
        if self.client_id:
            self.gui.lbl_client_id.setText(f"Client-ID: {self.client_id}")
        else:
            self.gui.lbl_client_id.setText(
                "No Client ID defined yet - will be displayed automatically on next restart")
        # Define entry fields for user input
        self.gui.entry_ip.returnPressed.connect(self.checkandgoquery)
        self.gui.LE_add_custom_command.returnPressed.connect(
            self.add_custom_command_manually)
        self.gui.entry_queryport.returnPressed.connect(self.checkandgoquery)
        self.gui.entry_rconport.returnPressed.connect(self.checkandgoquery)
        self.gui.entry_rconpw.returnPressed.connect(self.checkandgoquery)
        self.gui.label_button_name_2.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_3.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_5.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_6.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_7.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_8.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_9.returnPressed.connect(self.save_settings)
        self.gui.label_button_name_10.returnPressed.connect(self.save_settings)
        self.gui.label_command_button_2.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_3.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_5.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_6.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_7.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_8.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_9.returnPressed.connect(
            self.save_settings)
        self.gui.label_command_button_10.returnPressed.connect(
            self.save_settings)
        # Connect Labels with enter key press
        self.gui.label_rconcommand.returnPressed.connect(self.checkandgorcon)
        # self.gui.entry_refresh_timer.returnPressed.connect(self.checkandgorcon)
        self.gui.server_alias.returnPressed.connect(self.server_add)
        self.gui.server_ip.returnPressed.connect(self.server_add)
        self.gui.server_query.returnPressed.connect(self.server_add)
        self.gui.server_rconport.returnPressed.connect(self.server_add)
        self.gui.server_rconpw.returnPressed.connect(self.server_add)
        # Fill the Dropdown menus
        self.create_server_table_widget()
        self.fill_server_table_widget()
        self.fill_dropdown_server_box()
        self.fill_dropdown_custom_command()
        self.fill_list_custom_command()
        self.get_configuration_from_DB_and_set_settings()
        self.fill_map_manager_dropdown()
        # Define the server manager tab
        self.gui.btn_server_add.clicked.connect(self.server_add)
        self.gui.btn_server_modify.clicked.connect(self.server_modify)
        self.gui.btn_server_delete.clicked.connect(self.server_delete)
        #
        # Assign Server variables for Dropdown menu on selection
        #

        def assign_server_values_list(text):
            self.assign_server_values_list_text = text
            selection = self.assign_server_values_list_text
            self.c.execute("select ipaddress FROM server WHERE alias = (:select_alias)", {
                           'select_alias': selection})
            extract = self.c.fetchone()
            for selip in extract:
                sel_ipaddress = selip
            self.c.execute("select queryport FROM server WHERE alias = (:select_alias)", {
                           'select_alias': selection})
            extract = self.c.fetchone()
            for selqp in extract:
                sel_queryport = str(selqp)
            self.c.execute("select rconport FROM server WHERE alias = (:select_alias)", {
                           'select_alias': selection})
            extract = self.c.fetchone()
            for selrp in extract:
                sel_rconport = str(selrp)
            self.c.execute("select rconpw FROM server WHERE alias = (:select_alias)", {
                           'select_alias': selection})
            extract = self.c.fetchone()
            for selrpw in extract:
                sel_rconpw = selrpw
            self.conn.commit()
            self.gui.entry_ip.setText(sel_ipaddress)
            self.gui.entry_queryport.setText(sel_queryport)
            self.gui.entry_rconport.setText(sel_rconport)
            self.gui.entry_rconpw.setText(sel_rconpw)
            self.checkandgoquery()
        #
        # Assign custom Commands variables for Dropdown menu
        #

        def assign_custom_commands_values_list(text):
            self.assign_custom_commands_values_list_text = text
            selection = self.assign_custom_commands_values_list_text
            # Handover selected RCON Command
            self.gui.label_rconcommand.setText(selection)
        # Connect execution of selected variables with drop down menu select
        self.gui.dropdown_select_server.activated[str].connect(
            assign_server_values_list)
        self.gui.dropdown_custom_commands.activated[str].connect(
            assign_custom_commands_values_list)
        # Set empty saved indicator for configuration window
        self.gui.label_saving_indicator.clear()
        # Call method to define the custom buttons
        self.assign_main_custom_buttons()
        # DB Import Buttons and fields
        self.gui.btn_select_database.clicked.connect(
            lambda: self.DB_import("select_db"))
        self.gui.btn_add_database.clicked.connect(
            lambda: self.DB_import("add_db"))
        self.gui.btn_replace_database.clicked.connect(
            lambda: self.DB_import("replace_db"))
        # Map and option assignment
        self.gui.dropdown_select_travelscenario.activated[str].connect(
            self.selected_map_switch)
        self.gui.dropdown_mapmgr_selector.activated[str].connect(
            self.fill_map_manager_conf_tab)
        self.unique_modifier_id = ""
        self.gui.btn_server_delete.setEnabled(False)
        self.gui.btn_server_modify.setEnabled(False)

    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # Dropdown Menu Handling
    #
    # Fill Dropdown Menue for custom commands from scratch

    def fill_dropdown_custom_command(self):
        self.c.execute("select distinct commands FROM cust_commands")
        dh_alias = self.c.fetchall()
        self.gui.dropdown_custom_commands.clear()
        for row in dh_alias:
            self.gui.dropdown_custom_commands.addItems(row)
        self.conn.commit()
    # Fill Dropdown Custom Commands Manager

    def fill_list_custom_command(self):
        self.c.execute("select distinct commands FROM cust_commands")
        dcust_alias = self.c.fetchall()
        self.gui.list_custom_commands_console.clear()
        for row in dcust_alias:
            self.gui.list_custom_commands_console.addItems(row)
        self.conn.commit()

        def onClicked(item):
            QtWidgets.QApplication.clipboard().setText(item.text())
            self.gui.lbl_command_copied.setText("Command copied to Clipboard!")

            def waitandreturn():
                time.sleep(1)
                self.gui.lbl_command_copied.setText(
                    "Double-Click on command to copy to Clipboard")
            thread1 = threading.Thread(target=waitandreturn)
            thread1.start()
        self.gui.list_custom_commands_console.itemDoubleClicked.connect(
            onClicked)
    # Create Sevrer Manager Table

    def create_server_table_widget(self):
        self.gui.tbl_server_manager.setRowCount(0)
        self.gui.tbl_server_manager.insertRow(0)
        self.gui.tbl_server_manager.setColumnWidth(0, 30)
        self.gui.tbl_server_manager.setItem(
            0, 0, QtWidgets.QTableWidgetItem("ID"))
        self.gui.tbl_server_manager.item(
            0, 0).setBackground(QtGui.QColor(254, 254, 254))
        self.gui.tbl_server_manager.setColumnWidth(1, 370)
        self.gui.tbl_server_manager.setItem(
            0, 1, QtWidgets.QTableWidgetItem("Alias"))
        self.gui.tbl_server_manager.item(
            0, 1).setBackground(QtGui.QColor(254, 254, 254))
        self.gui.tbl_server_manager.setColumnWidth(2, 120)
        self.gui.tbl_server_manager.setItem(
            0, 2, QtWidgets.QTableWidgetItem("IP-Address"))
        self.gui.tbl_server_manager.item(
            0, 2).setBackground(QtGui.QColor(254, 254, 254))
        self.gui.tbl_server_manager.setColumnWidth(3, 90)
        self.gui.tbl_server_manager.setItem(
            0, 3, QtWidgets.QTableWidgetItem("Query Port"))
        self.gui.tbl_server_manager.item(
            0, 3).setBackground(QtGui.QColor(254, 254, 254))
        self.gui.tbl_server_manager.setItem(
            0, 4, QtWidgets.QTableWidgetItem("RCON Port"))
        self.gui.tbl_server_manager.item(
            0, 4).setBackground(QtGui.QColor(254, 254, 254))
    # Fill Dropdown Menue Server Selection on Main Window

    def fill_dropdown_server_box(self):
        # Database connection setup
        self.c.execute("select alias FROM server")
        dd_alias = self.c.fetchall()
        self.gui.dropdown_select_server.clear()
        for row in dd_alias:
            self.gui.dropdown_select_server.addItems(row)
        self.conn.commit()
    # Fill the server Table Widget

    def fill_server_table_widget(self):
        self.gui.tbl_server_manager.clearSpans()
        self.c.execute("SELECT * FROM server")
        self.conn.commit()
        for row, form in enumerate(self.c):
            row = row + 1
            self.gui.tbl_server_manager.insertRow(row)
            for column, item in enumerate(form):
                self.gui.tbl_server_manager.setItem(
                    row, column, QtWidgets.QTableWidgetItem(str(item)))

        def prepare_update_server(item):
            self.selected_row = item.row()
            self.resitem = self.gui.tbl_server_manager.item(self.selected_row, 0)
            if self.selected_row != 0:
                self.gui.btn_server_delete.setEnabled(True)
                self.gui.btn_server_modify.setEnabled(True)
                try:
                    self.c.execute("SELECT alias, ipaddress, queryport, rconport, rconpw FROM server where id=:sel_id", {
                                   'sel_id': self.resitem.text()})
                    select_result = self.c.fetchone()
                    self.conn.commit()
                    self.gui.server_alias.setText(select_result[0])
                    self.gui.server_alias.setCursorPosition(1)
                    self.gui.server_ip.setText(select_result[1])
                    self.gui.server_query.setText(str(select_result[2]))
                    self.gui.server_rconport.setText(str(select_result[3]))
                    self.gui.server_rconpw.setText(select_result[4])
                    self.unique_modifier_id = self.resitem.text()
                    print(self.unique_modifier_id)
                    self.conn.commit()
                except Exception:
                    self.gui.label_db_console.append(
                        f"No server with ID {self.selected_row} exists")
            else:
                self.gui.server_alias.clear()
                self.gui.server_ip.clear()
                self.gui.server_query.clear()
                self.gui.server_rconport.clear()
                self.gui.server_rconpw.clear()
        self.gui.tbl_server_manager.clicked.connect(prepare_update_server)
    # Fill Dropdown Menu for Mapchanging from scratch

    def fill_dropdown_map_box(self):
        self.c.execute(
            "select map_name FROM map_config WHERE modid = '0' ORDER by Map_name")
        dm_alias = self.c.fetchall()
        self.conn.commit()
        self.gui.dropdown_select_travelscenario.clear()
        self.gui.dropdown_select_gamemode.clear()
        self.gui.dropdown_select_lighting.clear()
        for rowmaps in dm_alias:
            self.gui.dropdown_select_travelscenario.addItems(rowmaps)
        if self.mutator_id_list == "None":
            pass
        else:
            if self.mutator_id_list[0]:
                self.gui.dropdown_select_travelscenario.addItem(
                    "---Custom Maps---")
                for custom_maps in self.mutator_id_list:
                    self.c.execute("select map_name FROM map_config WHERE modid=:mod_id ORDER by Map_name", {
                                   'mod_id': custom_maps})
                    dm2_alias = self.c.fetchone()
                    self.conn.commit()
                    if dm2_alias:
                        self.gui.dropdown_select_travelscenario.addItems(
                            dm2_alias)
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # Custom Command Handling
    #
    # Add custom command manually

    def add_custom_command_manually(self):
        # Check new RCON commands for validity
        def assess_custom_command_var(new__manual_custom_command):
            self.positive_command_check = 0
            if (new__manual_custom_command.startswith("quit") or
                new__manual_custom_command.startswith("exit") or
                new__manual_custom_command.startswith("listplayers") or
                new__manual_custom_command.startswith("help") or
                new__manual_custom_command.startswith("kick") or
                new__manual_custom_command.startswith("permban") or
                new__manual_custom_command.startswith("travel") or
                new__manual_custom_command.startswith("ban") or
                new__manual_custom_command.startswith("banid") or
                new__manual_custom_command.startswith("listbans") or
                new__manual_custom_command.startswith("unban") or
                new__manual_custom_command.startswith("say") or
                new__manual_custom_command.startswith("restartround") or
                new__manual_custom_command.startswith("maps") or
                new__manual_custom_command.startswith("scenarios") or
                new__manual_custom_command.startswith("travelscenario") or
                new__manual_custom_command.startswith("gamemodeproperty") or
                    new__manual_custom_command.startswith("listgamemodeproperties")):
                self.positive_c_command_check = 1
            else:
                self.positive_c_command_check = 0
        # Check and assign for positive assesment value and insert or throw error
        new__manual_custom_command = self.gui.LE_add_custom_command.text()
        if new__manual_custom_command:
            assess_custom_command_var(new__manual_custom_command)
            if self.positive_c_command_check == 1:
                self.c.execute("INSERT INTO cust_commands VALUES (:commands)", {
                               'commands': new__manual_custom_command})
                self.conn.commit()
                self.gui.LE_add_custom_command.clear()
            if self.positive_c_command_check == 0:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new__manual_custom_command} is no new valid custom RCON command! \n\n Please try again!")
                msg.exec_()
        self.fill_list_custom_command()
        self.fill_dropdown_custom_command()
    # Clear all Custom Commands

    def custom_command_clear_all(self):
        self.c.execute("DELETE from cust_commands")
        self.gui.list_custom_commands_console.clear()
        self.conn.commit()
        self.fill_list_custom_command()
        self.fill_dropdown_custom_command()
    # Clear selected commands from Custom commands

    def custom_command_clear_selected(self):
        delete_commands = self.gui.list_custom_commands_console.selectedItems()
        if delete_commands:
            for row in delete_commands:
                self.c.execute("DELETE FROM cust_commands WHERE commands=:delcommand", {
                               'delcommand': row.text()})
        self.conn.commit()
        self.fill_list_custom_command()
        self.fill_dropdown_custom_command()
    # Define the Custom Buttons in the Main menu

    def assign_main_custom_buttons(self):
        # Get DB variables for custom buttons
        self.c.execute('''select btn1_name, btn1_command,
                            btn2_name, btn2_command,
                            btn3_name, btn3_command,
                            btn4_name, btn4_command,
                            btn5_name, btn5_command,
                            btn6_name, btn6_command,
                            btn7_name, btn7_command,
                            btn8_name, btn8_command,
                            btn9_name, btn9_command,
                            btn10_name, btn10_command,
                            btn11_name, btn11_command
                            from configuration''')
        dbconf_cust = self.c.fetchall()
        self.conn.commit()
        dbconf_cust_strip = dbconf_cust[0]
        # Split Tuple and extract buttons names and commands
        self.button2_name = (dbconf_cust_strip[2])
        self.button2_command = (dbconf_cust_strip[3])
        self.button3_name = (dbconf_cust_strip[4])
        self.button3_command = (dbconf_cust_strip[5])
        self.button5_name = (dbconf_cust_strip[8])
        self.button5_command = (dbconf_cust_strip[9])
        self.button6_name = (dbconf_cust_strip[10])
        self.button6_command = (dbconf_cust_strip[11])
        self.button7_name = (dbconf_cust_strip[12])
        self.button7_command = (dbconf_cust_strip[13])
        self.button8_name = (dbconf_cust_strip[14])
        self.button8_command = (dbconf_cust_strip[15])
        self.button9_name = (dbconf_cust_strip[16])
        self.button9_command = (dbconf_cust_strip[17])
        self.button10_name = (dbconf_cust_strip[18])
        self.button10_command = (dbconf_cust_strip[19])
        self.button11_name = (dbconf_cust_strip[20])
        self.button11_command = (dbconf_cust_strip[21])
        # Assign variables (Button names and commands) to custom Buttons
        self.gui.btn_main_drcon_listbans.setText(self.button2_name)
        self.gui.btn_main_drcon_listbans_definition.setText(self.button2_name)
        self.gui.btn_main_drcon_listmaps.setText(self.button3_name)
        self.gui.btn_main_drcon_listmaps_definition.setText(self.button3_name)
        self.gui.btn_main_drcon_restartround.setText(self.button5_name)
        self.gui.btn_main_drcon_restartround_definition.setText(
            self.button5_name)
        self.gui.btn_main_drcon_showgamemode.setText(self.button6_name)
        self.gui.btn_main_drcon_showgamemode_definition.setText(
            self.button6_name)
        self.gui.btn_main_drcon_showaidiff.setText(self.button7_name)
        self.gui.btn_main_drcon_showaidiff_definition.setText(
            self.button7_name)
        self.gui.btn_main_drcon_showsupply.setText(self.button8_name)
        self.gui.btn_main_drcon_showsupply_definition.setText(
            self.button8_name)
        self.gui.btn_main_drcon_roundlimit.setText(self.button9_name)
        self.gui.btn_main_drcon_roundlimit_definition.setText(
            self.button9_name)
        self.gui.btn_main_drcon_showroundtime.setText(self.button10_name)
        self.gui.btn_main_drcon_showroundtime_definition.setText(
            self.button10_name)
        self.gui.btn_main_drcon_help.setText(self.button11_name)
        self.gui.btn_main_drcon_listbans.clicked.connect(
            lambda: self.direct_rcon_command(self.button2_command))
        self.gui.btn_main_drcon_listmaps.clicked.connect(
            lambda: self.direct_rcon_command(self.button3_command))
        self.gui.btn_main_drcon_restartround.clicked.connect(
            lambda: self.direct_rcon_command(self.button5_command))
        self.gui.btn_main_drcon_showgamemode.clicked.connect(
            lambda: self.direct_rcon_command(self.button6_command))
        self.gui.btn_main_drcon_showaidiff.clicked.connect(
            lambda: self.direct_rcon_command(self.button7_command))
        self.gui.btn_main_drcon_showsupply.clicked.connect(
            lambda: self.direct_rcon_command(self.button8_command))
        self.gui.btn_main_drcon_roundlimit.clicked.connect(
            lambda: self.direct_rcon_command(self.button9_command))
        self.gui.btn_main_drcon_showroundtime.clicked.connect(
            lambda: self.direct_rcon_command(self.button10_command))
        self.gui.btn_main_drcon_help.clicked.connect(
            lambda: self.direct_rcon_command(self.button11_command))
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # Query Handling
    #
    # Check for the IP and Queryport to be correct in syntax and range and go for the query

    def checkandgoquery(self):
        # Check IP
        self.regexip = r'''^(25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)$'''
        val_localhost = "127.0.0.1"
        if self.gui.entry_ip.text() == val_localhost:
            try:
                qmsg = QtWidgets.QMessageBox()
                qmsg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                qmsg.setIcon(QtWidgets.QMessageBox.Information)
                qmsg.setWindowTitle("ISRT Error Message")
                qmsg.setText(
                    "Due to a Windows connection problem, 127.0.0.1\ncannot be used for INS, switching to LAN IP-Address!")
                qmsg.exec_()
                self.serverhost = socket.gethostbyname(socket.getfqdn())
                self.queryport = self.gui.entry_queryport.text()
                self.gui.entry_ip.setText(self.serverhost)
                self.gui.label_output_window.setStyleSheet(
                    "border-image:url(:/img/img/rcon-bck.jpg);\n")
                self.queryserver(self.serverhost, self.queryport)
                if self.queryserver:
                    self.get_listplayers_fancy()
            except Exception:
                self.gui.label_output_window.setStyleSheet(
                    "border-image:url(:/img/img/offline.jpg);\n")
                self.gui.le_password.setStyleSheet(
                    "border-image: url(:/img/img/lock-unchecked.png);")
                self.gui.label_map_view.setStyleSheet(
                    "border-image: url(:/map_view/img/maps/map_views.jpg)")
                self.gui.tbl_player_output.setRowCount(0)
                self.gui.le_servername.clear()
                self.gui.le_gamemode.clear()
                self.gui.dropdown_select_travelscenario.clear()
                self.gui.dropdown_select_gamemode.clear()
                self.gui.dropdown_select_lighting.clear()
                self.gui.le_serverip_port.clear()
                self.gui.le_vac.clear()
                self.gui.le_players.clear()
                self.gui.le_ping.clear()
                self.gui.le_map.clear()
                self.gui.le_mods.clear()
        elif re.search(self.regexip, self.gui.entry_ip.text()):
            self.serverhost = self.gui.entry_ip.text()
            try:
                if self.gui.entry_queryport.text() and 1 <= int(self.gui.entry_queryport.text()) <= 65535:
                    self.queryport = self.gui.entry_queryport.text()
                    try:
                        self.queryserver(self.serverhost, self.queryport)
                        if self.queryserver:
                            self.get_listplayers_fancy()
                        self.gui.label_output_window.setStyleSheet(
                            "border-image:url(:/img/img/rcon-bck.jpg);\n")
                    except Exception:
                        self.gui.le_password.setStyleSheet(
                            "border-image: url(:/img/img/lock-unchecked.png);")
                        self.gui.label_map_view.setStyleSheet(
                            "border-image: url(:/map_view/img/maps/map_views.jpg)")
                        self.gui.label_output_window.setStyleSheet(
                            "border-image:url(:/img/img/offline.jpg);\n")
                        self.gui.tbl_player_output.setRowCount(0)
                        self.gui.dropdown_select_travelscenario.clear()
                        self.gui.dropdown_select_gamemode.clear()
                        self.gui.dropdown_select_lighting.clear()
                        self.gui.le_servername.clear()
                        self.gui.le_gamemode.clear()
                        self.gui.le_serverip_port.clear()
                        self.gui.le_vac.clear()
                        self.gui.le_players.clear()
                        self.gui.le_ping.clear()
                        self.gui.le_map.clear()
                        self.gui.le_mods.clear()
                else:
                    raise ValueError
            except ValueError:
                self.gui.label_output_window.setText(self.gui.entry_queryport.text(
                ) + " is no valid Query Port number - please retry!")
        else:
            self.gui.label_output_window.setText(
                self.gui.entry_ip.text() + " is no valid IP address - please retry!")
    # Execute Query Command, when called by checkandgoquery()!

    def queryserver(self, serverhost, queryport):
        self.gui.label_output_window.clear()
        self.server = query.Query(self.serverhost, self.queryport)
        self.serverinfo = (self.server.info())
        self.servergamedetails = (self.serverinfo['info'])
        self.serverrules = (self.server.rules())
        self.serverruledetails = (self.serverrules['rules'])
        self.servernetworkdetails = (self.serverinfo['server'])
        self.pwcheck = (self.servergamedetails['server_password_protected'])
        self.vaccheck = (self.servergamedetails['server_vac_secured'])
        self.ranked = (self.serverruledetails['RankedServer_b'])
        self.coop = (self.serverruledetails['Coop_b'])
        self.mods = (self.serverruledetails['Mutated_b'])
        self.day = (self.serverruledetails['Day_b'])
        if self.mods == "true":
            self.servermodcheck = "Yes"
        else:
            self.servermodcheck = "No"
        if self.pwcheck == 0:
            self.gui.le_password.setStyleSheet(
                "border-image: url(:/img/img/lock-unlocked.png);")
        else:
            self.gui.le_password.setStyleSheet(
                "border-image: url(:/img/img/lock-locked.png);")
        if self.vaccheck == 0:
            self.servervaccheck = "No"
        else:
            self.servervaccheck = "Yes"

        if self.ranked == "true":
            self.serverrulecheck = "Yes"
        else:
            self.serverrulecheck = "No"
        if self.coop == "true":
            self.servercoopcheck = "Coop"
        else:
            self.servercoopcheck = "Versus"
        if self.servermodcheck == "Yes":
            self.mutatorids = self.serverruledetails['Mutators_s']
        else:
            self.mutatorids = "None"
        if self.day == "true":
            self.lighting_map = "Day"
        else:
            self.lighting_map = "Night"
        self.gui.le_servername.setText(
            str(self.servergamedetails['server_name']))
        self.gui.le_gamemode.setText(str(
            self.serverruledetails['GameMode_s']) + " (" + str(self.servercoopcheck) + ")")
        self.gui.le_serverip_port.setText(str(
            self.servernetworkdetails['ip']) + ":" + str(self.servergamedetails['server_port']))
        self.gui.le_vac.setText(
            str(self.servervaccheck) + "/" + str(self.serverrulecheck))
        self.gui.le_players.setText(str(
            self.servergamedetails['players_current']) + "/" + str(self.servergamedetails['players_max']))
        self.gui.le_ping.setText(str(self.servernetworkdetails['ping']))
        self.gui.le_map.setText(
            str(self.servergamedetails['game_map']) + " (" + self.lighting_map + ")")
        self.gui.le_mods.setText(str(self.mutatorids))
        self.gui.le_mods.setToolTip(str(self.mutatorids))
        self.gui.le_mods.setCursorPosition(1)
        # Creating a list for mutator-IDs to identify installed maps
        check_modlist = self.serverruledetails.get('ModList_s')
        if check_modlist:
            self.mutator_id_list = (
                self.serverruledetails['ModList_s'].split(','))
        else:
            self.mutator_id_list = "None"
        #
        # Create Map View Picture based on running map
        #

        def assign_map_view_pic(self):
            map_view_pic = str(self.servergamedetails['game_map'])
            self.c.execute("select map_pic FROM map_config WHERE map_alias=:map_view_result", {
                           'map_view_result': map_view_pic})
            dpmap_alias = self.c.fetchone()
            dpmap_split = dpmap_alias[0].split(".")
            mapname = dpmap_split[0]
            ending = dpmap_split[1]

            self.c.execute("select self_added FROM map_config WHERE map_alias=:map_view_result", {
                           'map_view_result': map_view_pic})
            self_added_temp = self.c.fetchone()
            self_added_check = self_added_temp[0]

            if self.lighting_map == "Day":
                mapview_pic = (mapname + "." + ending)
            else:
                mapview_pic = (mapname + "_night." + ending)
            self.conn.commit()

            if self_added_check == 0:
                if dpmap_alias:
                    self.gui.label_map_view.setStyleSheet(
                        f"border-image: url(:map_thumbs/img/maps/thumbs/{mapview_pic}); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
                else:
                    self.gui.label_output_window.setText(
                        "No Map Image available - referring to placeholder!")
                    self.gui.label_map_view.setStyleSheet(
                        "border-image: url(:/map_view/img/maps/map_views.jpg); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
            else:
                if dpmap_alias:
                    custom_map_pic_temp = (
                        str(self.dbdir) + '\\img\\custom_map_pics\\' + mapview_pic)
                    custom_map_pic = custom_map_pic_temp.replace("\\", "/")
                    self.gui.label_map_view.setStyleSheet(
                        f"border-image: url({custom_map_pic}); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
                else:
                    self.gui.label_output_window.setText(
                        "No Map Image available - referring to placeholder!")
                    self.gui.label_map_view.setStyleSheet(
                        "border-image: url(:/map_view/img/maps/map_views.jpg); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")

        assign_map_view_pic(self)
        self.fill_dropdown_map_box()
    # Get fancy returned Playerlist

    def get_listplayers_fancy(self):
        self.serverhost = self.gui.entry_ip.text()
        self.queryport = self.gui.entry_queryport.text()
        self.server_players = sq.SourceQuery(
            self.serverhost, int(self.queryport))
        row = 0
        self.gui.tbl_player_output.setRowCount(0)
        if self.server_players.get_players():
            for player in self.server_players.get_players():
                data_id = ("{id}".format(**player))
                data_name = ("{Name}".format(**player))
                data_frags = ("{Frags}".format(**player))
                data_prettyTime = ("{PrettyTime}".format(**player))
                self.gui.tbl_player_output.insertRow(row)
                self.gui.tbl_player_output.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(data_id))
                self.gui.tbl_player_output.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(data_name))
                self.gui.tbl_player_output.setItem(
                    row, 2, QtWidgets.QTableWidgetItem(data_frags))
                self.gui.tbl_player_output.setItem(
                    row, 3, QtWidgets.QTableWidgetItem(data_prettyTime))
                row = row + 1
        else:
            self.gui.label_output_window.setText("No Players online")
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # RCON Handling
    #
    # Map Changer Preparation - Selector

    def selected_map_switch(self):
        self.selected_map = self.gui.dropdown_select_travelscenario.currentText()
        self.c.execute("select map_alias FROM map_config WHERE map_name=:var_selected_map", {
                       'var_selected_map': self.selected_map})
        dsma_alias = self.c.fetchone()
        self.conn.commit()
        var_selected_map = (dsma_alias[0])

        self.c.execute("select * from map_config where map_alias=:varselmap",
                       {'varselmap': var_selected_map})
        dsmam_alias = self.c.fetchall()

        self.conn.commit()
        dsmam_list = (dsmam_alias[0])
        light_day = dsmam_list[3]
        light_night = dsmam_list[4]
        var_cp = dsmam_list[8]
        var_cpins = dsmam_list[9]
        var_cphc = dsmam_list[6]
        var_cphcins = dsmam_list[7]
        var_dom = dsmam_list[10]
        var_ffe = dsmam_list[11]
        var_ffw = dsmam_list[12]
        var_fl = dsmam_list[13]
        var_op = dsmam_list[14]
        var_pu = dsmam_list[15]
        var_puins = dsmam_list[16]
        var_ski = dsmam_list[17]
        var_tdm = dsmam_list[18]

        var_dn = (str(light_day) + str(light_night))
        self.gui.dropdown_select_lighting.clear()
        self.gui.dropdown_select_gamemode.clear()
        if var_dn == "10":
            self.gui.dropdown_select_lighting.addItem("Day")
        else:
            var_dn_list = ("Day", "Night")
            self.gui.dropdown_select_lighting.addItems(var_dn_list)
        if var_cp:
            self.gui.dropdown_select_gamemode.addItem("CheckPoint Security")
        if var_cpins:
            self.gui.dropdown_select_gamemode.addItem("CheckPoint Insurgents")
        if var_cphc:
            self.gui.dropdown_select_gamemode.addItem("CheckPoint HC Security")
        if var_cphcins:
            self.gui.dropdown_select_gamemode.addItem(
                "CheckPoint HC Insurgents")
        if var_dom:
            self.gui.dropdown_select_gamemode.addItem("Domination")
        if var_ffe:
            self.gui.dropdown_select_gamemode.addItem("Firefight East")
        if var_ffw:
            self.gui.dropdown_select_gamemode.addItem("Firefight West")
        if var_fl:
            self.gui.dropdown_select_gamemode.addItem("Frontline")
        if var_op:
            self.gui.dropdown_select_gamemode.addItem("Outpost")
        if var_pu:
            self.gui.dropdown_select_gamemode.addItem("Push Security")
        if var_puins:
            self.gui.dropdown_select_gamemode.addItem("Push Insurgents")
        if var_ski:
            self.gui.dropdown_select_gamemode.addItem("Skirmish")
        if var_tdm:
            self.gui.dropdown_select_gamemode.addItem("TeamDeathMatch")
        self.gui.dropdown_select_gamemode.setCurrentText(
            "CheckPoint HC Security")
        self.gui.dropdown_select_lighting.setCurrentText("Day")
    # Mapchanger

    def map_changer(self):
        # Define required variables
        val_map = self.gui.dropdown_select_travelscenario.currentText()
        val_gamemode = self.gui.dropdown_select_gamemode.currentText()
        val_light = self.gui.dropdown_select_lighting.currentText()
        val_frenzy = self.gui.dropdown_select_frenzy.currentText()
        if val_gamemode == "CheckPoint Security":
            val_gamemode = "checkpoint"
        elif val_gamemode == "CheckPoint Insurgents":
            val_gamemode = "checkpoint_ins"
        elif val_gamemode == "CheckPoint HC Security":
            val_gamemode = "checkpointhardcore"
        elif val_gamemode == "CheckPoint HC Insurgents":
            val_gamemode = "checkpointhardcore_ins"
        elif val_gamemode == "Domination":
            val_gamemode = "domination"
        elif val_gamemode == "Firefight East":
            val_gamemode = "firefight_east"
        elif val_gamemode == "Firefight West":
            val_gamemode = "firefight_west"
        elif val_gamemode == "Frontline":
            val_gamemode = "frontline"
        elif val_gamemode == "Outpost":
            val_gamemode = "outpost"
        elif val_gamemode == "Push Security":
            val_gamemode = "push"
        elif val_gamemode == "Push Insurgents":
            val_gamemode = "push_ins"
        elif val_gamemode == "Skirmish":
            val_gamemode = "skirmish"
        elif val_gamemode == "TeamDeathMatch":
            val_gamemode = "teamdeathmath"

        if val_frenzy == "Activate Frenzy":
            val_frenzy_switch = 2
        elif val_frenzy == "Deactivate Frenzy":
            val_frenzy_switch = 0
        else:
            val_frenzy_switch = 1

        if val_map.startswith("Select") or val_map.startswith("--"):
            self.gui.label_output_window.setText(
                "This is not a valid map, please chose one first!")
        else:
            self.c.execute("select map_alias FROM map_config WHERE map_name=:sql_map_name", {
                           'sql_map_name': val_map})
            val_map_alias = self.c.fetchone()
            val_map_alias_result = (str(val_map_alias[0]))
            query2 = ("select " + val_gamemode +
                     " FROM map_config WHERE map_alias=:sqlmap_alias")
            self.c.execute(query2, {'sqlmap_alias': val_map_alias_result})
            val_travel_alias = self.c.fetchone()
            val_travel_alias_result = (str(val_travel_alias[0]))
            self.conn.commit()

            if val_gamemode == "checkpointhardcore_ins":
                val_gamemode = "checkpointhardcore"

            if val_frenzy_switch == 2:
                command = ("travel " + val_map_alias_result + "?Scenario=" + val_travel_alias_result +
                           "?Lighting=" + val_light + "?game=" + val_gamemode + "?Mutators=Frenzy")
            elif val_frenzy_switch == 0:
                command = ("travel " + val_map_alias_result + "?Scenario=" + val_travel_alias_result +
                           "?Lighting=" + val_light + "?game=" + val_gamemode + "?Mutators=?")
            else:
                command = ("travel " + val_map_alias_result + "?Scenario=" +
                           val_travel_alias_result + "?Lighting=" + val_light + "?game=" + val_gamemode)

            if command:
                self.gui.label_rconcommand.setText(command)
            else:
                self.gui.label_output_window.setText(
                    "Something went wrong with the Travel command, please check above and report it!")
            self.checkandgorcon()
            time.sleep(0.2)
            self.checkandgoquery()
            self.gui.progressbar_map_changer.setProperty("value", 0)
    # Direct RCON Command handling

    def direct_rcon_command(self, command):
        # Check if an rcon command is passed
        if command:
            self.gui.label_rconcommand.setText(command)
            self.checkandgorcon()
        else:
            self.gui.label_output_window.setText(
                "Something went wrong with the RCON command, please report it!")
    # Check for the format string and go for the rcon command, but only if rcon port and rcon password are given

    def checkandgorcon(self):
        # Check IP
        self.regexip = r'''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)$'''
        command_check = self.gui.label_rconcommand.text()
        save_command_check = None
        # Save commands while hitting Submit
        save_command_check = 1
        val_localhost = "127.0.0.1"
        if self.gui.entry_ip.text() == val_localhost:
            self.gui.label_output_window.setText(
                "Due to a Windows connection problem, 127.0.0.1 cannot be used currently, please use your LAN IP-Address!")
        else:
            if self.gui.entry_rconpw.text() and command_check.startswith("gamever") or command_check.startswith("quit") or command_check.startswith("exit") or command_check.startswith("help") or command_check.startswith("listplayers") or command_check.startswith("kick") or command_check.startswith("permban") or command_check.startswith("travel") or command_check.startswith("ban") or command_check.startswith("banid") or command_check.startswith("listbans") or command_check.startswith("unban") or command_check.startswith("say") or command_check.startswith("restartround") or command_check.startswith("maps") or command_check.startswith("scenarios") or command_check.startswith("travelscenario") or command_check.startswith("gamemodeproperty") or command_check.startswith("listgamemodeproperties"):
                if re.search(self.regexip, self.gui.entry_ip.text()):
                    self.serverhost = self.gui.entry_ip.text()
                    try:
                        if self.gui.entry_rconport.text() and 1 <= int(self.gui.entry_rconport.text()) <= 65535:
                            serverhost = str(self.gui.entry_ip.text())
                            rconpassword = str(self.gui.entry_rconpw.text())
                            rconport = int(self.gui.entry_rconport.text())
                            rconcommand = str(
                                self.gui.label_rconcommand.text())
                            if save_command_check == 1 and command_check:
                                self.c.execute("INSERT INTO cust_commands VALUES (:commands)", {
                                               'commands': command_check})
                                self.conn.commit()
                                self.fill_dropdown_custom_command()
                                self.fill_list_custom_command()
                            try:
                                self.rconserver(
                                    serverhost, rconpassword,  rconport, rconcommand)
                                self.gui.progressbar_map_changer.setProperty(
                                    "value", 33)
                                time.sleep(1)
                                self.gui.progressbar_map_changer.setProperty(
                                    "value", 66)
                                time.sleep(1)
                                self.gui.progressbar_map_changer.setProperty(
                                    "value", 100)
                                time.sleep(0.2)
                                self.gui.progressbar_map_changer.setProperty(
                                    "value", 0)
                            except Exception as e:
                                msg = QtWidgets.QMessageBox()
                                msg.setWindowIcon(
                                    QtGui.QIcon(".\\img/isrt.ico"))
                                msg.setIcon(QtWidgets.QMessageBox.Critical)
                                msg.setWindowTitle("ISRT Error Message")
                                msg.setText("We encountered and error: \n\n" + str(
                                    e) + "\n\nWrong IP, RCON Port, Command or Password?\nThe server may also be down - please check that!")
                                msg.exec_()
                                self.gui.progressbar_map_changer.setProperty(
                                    "value", 0)
                        else:
                            raise ValueError
                    except ValueError:
                        self.gui.label_output_window.setText(self.gui.entry_rconport.text(
                        ) + " is no valid RCON Port number - please retry!")
                        self.gui.progressbar_map_changer.setProperty(
                            "value", 0)
                else:
                    self.gui.label_output_window.setText(
                        self.gui.entry_ip.text() + " is no valid IP address - please retry!")
                    self.gui.progressbar_map_changer.setProperty("value", 0)
            else:
                self.gui.label_output_window.setText(
                    "No RCON Password given or no valid RCON command - please retry!")
                self.gui.progressbar_map_changer.setProperty("value", 0)
        self.gui.progressbar_map_changer.setProperty("value", 0)
    # Execute RCON Command, when called by checkandgorcon()!

    def rconserver(self, serverhost, rconpassword, rconport, rconcommand):
        if rconcommand.startswith("say") or rconcommand.startswith("Say"):
            self.gui.label_output_window.setText(
                rconcommand + " command has been sent to the server")
            console = Console(
                host=serverhost, password=rconpassword, port=rconport)
            commandconsole = (console.command(rconcommand))
        elif rconcommand.startswith("restartround") or rconcommand.startswith("Restartround"):
            self.gui.label_output_window.setText(
                "Round restarted without Team swap!")
            console = Console(
                host=serverhost, password=rconpassword, port=rconport)
            commandconsole = (console.command(rconcommand))
        else:
            console = Console(
                host=serverhost, password=rconpassword, port=rconport)
            commandconsole = (console.command(rconcommand))
            self.gui.label_output_window.setText(str(commandconsole))
        console.close()
    # Execute Admin Say

    def adminsay(self):
        if self.gui.entry_ip.text() and self.gui.entry_rconport.text():
            qid = QtWidgets.QInputDialog.getText(
                self, "Input Dialog", "Enter Admin Message:")
            message = qid[0]
            retval = qid[1]
            print(retval)
            if retval == True and message:
                saycommand = (f"say {message}")
                self.direct_rcon_command(saycommand)
        else:
            self.gui.label_output_window.setText(
                "You have to enter an IP-address and an RCON Port at least!")
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # Server Manager
    #
    # Add a server to DB

    def server_add(self):
        val_alias = self.gui.server_alias.text()
        val_ipaddress = self.gui.server_ip.text()
        val_queryport = self.gui.server_query.text()
        val_rconport = self.gui.server_rconport.text()
        val_rconpw = self.gui.server_rconpw.text()
        go_addserver_check = 0
        # Check IP
        self.regexip = r'''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)$'''
        self.regexport = r'''^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'''

        if val_alias and val_ipaddress and val_queryport:
            go_addserver_check = 1
        else:
            self.gui.label_db_console.append(
                "At least Alias, IP-Adress and Query Port have to contain a value!")
            go_addserver_check = 0

        if val_ipaddress and (re.search(self.regexip, val_ipaddress)):
            go_addserver_ipcheck = 1
        else:
            self.gui.label_db_console.setText(
                val_ipaddress + " is no valid IP address - please check and retry!")
            go_addserver_ipcheck = 0
        if val_queryport and (re.search(self.regexport, val_queryport)):
            go_addserver_qpcheck = 1
        else:
            self.gui.label_db_console.setText(
                val_queryport + " is no valid Query Port - please check and retry!")
            go_addserver_qpcheck = 0
        if val_rconport:
            if (re.search(self.regexport, val_rconport)):
                pass
            else:
                self.gui.label_db_console.setText(
                    val_rconport + " is no valid RCON Port - please check and retry!")
                go_addserver_check = 0
        self.c.execute("select alias FROM server")
        check_alias = self.c.fetchall()
        self.conn.commit()
        nogocheck = 1
        for check in check_alias:
            for item in check:
                if item and val_alias == item:
                    go_addserver_check = 0
                    self.gui.label_db_console.append(
                        "Alias already exists, please choose another one")
                    nogocheck = 0
                else:
                    nogocheck = 1
        if go_addserver_check == 1 and nogocheck == 1 and go_addserver_ipcheck == 1 and go_addserver_qpcheck == 1:
            self.c.execute("SELECT COALESCE(MAX(id), 0) FROM server")
            raw_table_counter = self.c.fetchone()
            self.conn.commit()
            val_id = raw_table_counter[0] + 1
            try:
                self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                               'id': val_id, 'alias': val_alias, 'ipaddress': val_ipaddress, 'queryport': val_queryport, 'rconport': val_rconport, 'rconpw': val_rconpw})
                self.conn.commit()
                self.gui.label_db_console.append(
                    "Server successfully inserted")
                self.gui.server_alias.clear()
                self.gui.server_ip.clear()
                self.gui.server_query.clear()
                self.gui.server_rconport.clear()
                self.gui.server_rconpw.clear()
            except sqlite3.Error as error:
                self.gui.label_db_console.append(
                    "Failed to insert server into database " + str(error))
        self.fill_dropdown_server_box()
        self.create_server_table_widget()
        self.fill_server_table_widget()
        self.gui.btn_server_delete.setEnabled(False)
        self.gui.btn_server_modify.setEnabled(False)
        
    # Add a server to DB

    def server_add_main(self):
        self.gui.label_output_window.setStyleSheet(
            "border-image:url(:/img/img/rcon-bck.jpg);\n")
        transferalias = self.gui.dropdown_select_server.currentText()
        transferip = self.gui.entry_ip.text()
        transferqport = self.gui.entry_queryport.text()
        transferrport = self.gui.entry_rconport.text()
        transferrpw = self.gui.entry_rconpw.text()
        # Check IP
        self.regextransip = r'''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)$'''
        self.regextransport = r'''^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'''
        go_addserver_check = 0
        go_addserver_ipcheck = 0
        go_addserver_qpcheck = 0
        if transferip and transferqport:
            go_addserver_check = 1
            if transferip and (re.search(self.regextransip, transferip)):
                go_addserver_ipcheck = 1
                if transferqport and (re.search(self.regextransport, transferqport)):
                    go_addserver_qpcheck = 1
                    if transferqport and (re.search(self.regextransport, transferqport)):
                        go_addserver_qpcheck = 1
                        if transferrport:
                            if (re.search(self.regextransport, transferrport)):
                                pass
                            else:
                                self.gui.label_output_window.append(
                                    "You entered no valid RCON Port - please check and retry!")
                                go_addserver_check = 0
                    else:
                        self.gui.label_output_window.append(
                            "You entered no valid Query Port - please check and retry!")
                        go_addserver_qpcheck = 0
                else:
                    self.gui.label_output_window.append(
                        "You entered no valid Query Port - please check and retry!")
                    go_addserver_qpcheck = 0
            else:
                self.gui.label_output_window.append(
                    "You entered no valid IP address - please check and retry!")
                go_addserver_ipcheck = 0
        else:
            self.gui.label_output_window.append(
                "At least IP-Adress and Query Port have to contain a value!")
            go_addserver_check = 0
        if go_addserver_check == 1 and go_addserver_ipcheck == 1 and go_addserver_qpcheck == 1:
            self.gui.TabWidget_Main_overall.setCurrentWidget(
                self.gui.Tab_Server)
            if transferalias == "Select Server":
                transferalias = ""
            self.gui.server_alias.setText(transferalias)
            self.gui.server_ip.setText(transferip)
            self.gui.server_query.setText(transferqport)
            self.gui.server_rconport.setText(transferrport)
            self.gui.server_rconpw.setText(transferrpw)
    # Add a server to DB

    def add_server_directly(self):
        asd_transferip = self.gui.entry_ip.text()
        asd_transferqport = self.gui.entry_queryport.text()
        asd_transferrport = self.gui.entry_rconport.text()
        asd_transferrpw = self.gui.entry_rconpw.text()
        # Check IP
        self.asd_regextransip = r'''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
        25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)$'''
        self.asd_regextransport = r'''^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'''
        go_addserver_check = 0
        go_addserver_ipcheck = 0
        go_addserver_qpcheck = 0
        if asd_transferip and asd_transferqport:
            go_addserver_check = 1
            if asd_transferip and (re.search(self.asd_regextransip, asd_transferip)):
                go_addserver_ipcheck = 1
                if asd_transferqport and (re.search(self.asd_regextransport, asd_transferqport)):
                    go_addserver_qpcheck = 1
                    if asd_transferqport and (re.search(self.asd_regextransport, asd_transferqport)):
                        go_addserver_qpcheck = 1
                        if asd_transferrport:
                            if (re.search(self.asd_regextransport, asd_transferrport)):
                                pass
                            else:
                                self.gui.label_output_window.append(
                                    "You entered no valid RCON Port - please check and retry!")
                                go_addserver_check = 0
                    else:
                        self.gui.label_output_window.append(
                            "You entered no valid Query Port - please check and retry!")
                        go_addserver_qpcheck = 0
                else:
                    self.gui.label_output_window.append(
                        "You entered no valid Query Port - please check and retry!")
                    go_addserver_qpcheck = 0
            else:
                self.gui.label_output_window.append(
                    "You entered no valid IP address - please check and retry!")
                go_addserver_ipcheck = 0
        else:
            self.gui.label_output_window.append(
                "At least IP-Adress and Query Port have to contain a value!")
            go_addserver_check = 0
        if go_addserver_check == 1 and go_addserver_ipcheck == 1 and go_addserver_qpcheck == 1:
            asd_alias = None
            try:
                self.gui.progressbar_map_changer.setProperty("value", 33)
                asd_server = query.Query(asd_transferip, asd_transferqport)
                asd_serverinfo = (asd_server.info())
                self.gui.progressbar_map_changer.setProperty("value", 66)
                asd_servergamedetails = (asd_serverinfo['info'])
                asd_alias = (asd_servergamedetails['server_name'])
                self.c.execute("SELECT COALESCE(MAX(id), 0) FROM server")
                raw_table_counter = self.c.fetchone()
                self.conn.commit()
                val_id = raw_table_counter[0] + 1
                alias_exists = 0
                alias_not_existing = 0
                if asd_alias:
                    self.c.execute("SELECT alias from server")
                    check_alias_list = self.c.fetchall()
                    self.conn.commit()
                    for checkalias in check_alias_list:
                        for item in checkalias:
                            if asd_alias == item:
                                alias_exists = 1
                            else:
                                alias_not_existing = 1
                    if asd_transferip and asd_transferqport and alias_exists == 0 and alias_not_existing == 1:
                        self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                                       'id': val_id, 'alias': asd_alias, 'ipaddress': asd_transferip, 'queryport': asd_transferqport, 'rconport': asd_transferrport, 'rconpw': asd_transferrpw})
                        self.conn.commit()
                        self.checkandgoquery()
                        self.fill_dropdown_server_box()
                        self.create_server_table_widget()
                        self.fill_server_table_widget()
                        self.gui.label_output_window.append(
                            f"Server successfully inserted with Alias: {asd_alias}")
                        self.gui.progressbar_map_changer.setProperty(
                            "value", 100)
                        time.sleep(0.2)
                        self.gui.progressbar_map_changer.setProperty(
                            "value", 0)
                    else:
                        raise Exception
            except Exception:
                self.gui.progressbar_map_changer.setProperty("value", 100)
                time.sleep(0.2)
                self.gui.progressbar_map_changer.setProperty("value", 0)
                self.gui.TabWidget_Main_overall.setCurrentWidget(
                    self.gui.Tab_Server)
                asd_alias = ""
                self.gui.server_alias.setText(asd_alias)
                self.gui.server_ip.setText(asd_transferip)
                self.gui.server_query.setText(asd_transferqport)
                self.gui.server_rconport.setText(asd_transferrport)
                self.gui.server_rconpw.setText(asd_transferrpw)
                self.gui.label_db_console.append(
                    "Could not add Server, it is not responding or Alias already exists\nPlease manually enter an Alias and click Add!")
    # Modify a server in DB

    def server_modify(self):
        val_alias = self.gui.server_alias.text()
        print(self.unique_modifier_id)
        if self.unique_modifier_id == "":
            val_id = ""
        else:
            val_id = self.unique_modifier_id
        if val_alias and val_id:
            val_ipaddress = self.gui.server_ip.text()
            val_queryport = self.gui.server_query.text()
            val_rconport = self.gui.server_rconport.text()
            val_rconpw = self.gui.server_rconpw.text()
            # Check IP
            self.regexip = r'''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-5][0-9]|[0-1]?[0-9][0-9]?)$'''
            self.regexport = r'''^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$'''
            self.c.execute("select alias FROM server")
            check_alias = self.c.fetchall()
            self.c.execute(
                "select alias, ipaddress, queryport, rconport, rconpw from server where id=:fid", {'fid': val_id})
            check_changes = self.c.fetchone()
            check_changes_alias = check_changes[0]
            check_changes_ip = check_changes[1]
            check_changes_qport = str(check_changes[2])
            check_changes_rport = str(check_changes[3])
            check_changes_rpw = check_changes[4]
            self.conn.commit()
            nothing_to_change = 0
            if val_alias == check_changes_alias and val_ipaddress == check_changes_ip == val_ipaddress and val_queryport == check_changes_qport and val_rconport == check_changes_rport and val_rconpw == check_changes_rpw:
                nothing_to_change = 1
            else:
                nothing_to_change = 0

            alias_nogocheck = 0
            alias_gocheck = 0
            for check in check_alias:
                for item in check:
                    if item and val_alias != item:
                        alias_gocheck = 1
                    else:
                        alias_nogocheck = 0

            if nothing_to_change == 1:
                self.gui.label_db_console.append(
                    "No changes made - nothing to do!")
            else:
                if alias_gocheck == 1 and alias_nogocheck == 0:
                    if val_ipaddress and (re.search(self.regexip, val_ipaddress)):
                        if val_queryport and (re.search(self.regexport, val_queryport)):
                            if val_rconport:
                                if (re.search(self.regexport, val_rconport)):
                                    if val_ipaddress and val_queryport and val_alias and val_id:
                                        try:
                                            self.c.execute("UPDATE server SET alias=:alias, ipaddress=:ipaddress, queryport=:queryport, rconport=:rconport, rconpw=:rconpw WHERE id=:mid", {
                                                           'alias': val_alias, 'ipaddress': val_ipaddress, 'queryport': val_queryport, 'rconport': val_rconport, 'rconpw': val_rconpw, 'mid': val_id})
                                            self.conn.commit()
                                            self.gui.label_db_console.append(
                                                "Server successfully updated")
                                        except sqlite3.Error as error:
                                            self.gui.label_db_console.append(
                                                "Failed to update server in database " + str(error))
                                    else:
                                        self.gui.label_db_console.append(
                                            "At least Alias, IP-Adress and Query Port have to contain a value!")
                                else:
                                    self.gui.label_db_console.append(
                                        val_rconport + " is no valid RCON Port - please check and retry!")
                            else:
                                if val_ipaddress and val_queryport and val_alias and val_id:
                                    try:
                                        self.c.execute("UPDATE server SET alias=:alias, ipaddress=:ipaddress, queryport=:queryport, rconport=:rconport, rconpw=:rconpw WHERE id=:mid", {
                                                       'alias': val_alias, 'ipaddress': val_ipaddress, 'queryport': val_queryport, 'rconport': val_rconport, 'rconpw': val_rconpw, 'mid': val_id})
                                        self.conn.commit()
                                        self.gui.label_db_console.append(
                                            "Server successfully updated")
                                    except sqlite3.Error as error:
                                        self.gui.label_db_console.append(
                                            "Failed to update server in database " + str(error))
                                else:
                                    self.gui.label_db_console.append(
                                        "At least Alias, IP-Adress and Query Port have to contain a value!")
                        else:
                            self.gui.label_db_console.append(
                                val_queryport + " is no valid Query Port - please check and retry!")
                    else:
                        self.gui.label_db_console.append(
                            val_ipaddress + " is no valid IP address - please check and retry!")
                else:
                    self.gui.label_db_console.append(
                        "Alias " + val_alias + " already exists in DB, please choose another one!")
            self.create_server_table_widget()
            self.fill_server_table_widget()
            self.fill_dropdown_server_box()
        else:
            self.gui.label_db_console.append("Server does not exist in DB - add it or choose a server first!")

    # Delete a Server from DB
    def server_delete(self):
        server_delete_id = self.unique_modifier_id
        if server_delete_id:
            start_update_id = int(server_delete_id) + 1
            self.c.execute("SELECT COALESCE(MAX(id), 0) FROM server")
            raw_end_update_id = self.c.fetchone()
            self.conn.commit()
            end_update_id = raw_end_update_id[0] + 1
            self.conn.commit()
            if start_update_id and end_update_id:
                try:
                    self.c.execute("DELETE FROM server WHERE id=:val_id", {
                                   'val_id': server_delete_id})
                    self.conn.commit()
                    for i in range(start_update_id, end_update_id):
                        seti = i - 1
                        self.c.execute("UPDATE server SET id=:vid WHERE id=:rowdid", {
                                       'vid': seti, 'rowdid': i})
                        self.conn.commit()
                    self.gui.label_db_console.append(
                        "Record successfully deleted")
                except sqlite3.Error as error:
                    self.gui.label_db_console.append(
                        "Failed to delete data from database " + str(error))
            else:
                self.gui.label_db_console.append(
                    "At least Alias has to contain a value!")
            self.fill_dropdown_server_box()
            self.create_server_table_widget()
            self.fill_server_table_widget()
        else:
            self.gui.label_db_console.append("Please choose a server first!")
        self.gui.server_alias.clear()
        self.gui.server_ip.clear()
        self.gui.server_query.clear()
        self.gui.server_rconport.clear()
        self.gui.server_rconpw.clear()
        self.gui.btn_server_delete.setEnabled(False)
        self.gui.btn_server_modify.setEnabled(False)

    # Import Database Routines
    def DB_import(self, db_action):
        if db_action == 'select_db':
            db_select_directory = (str(self.dbdir) + '\\db\\')
            self.data_path = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select Database', db_select_directory, '*.db',)
            self.gui.label_selected_db.setText(self.data_path[0])
            self.datapath = self.data_path[0]

        elif db_action == 'add_db':
            if self.datapath != None and self.datapath.endswith(".db"):
                self.gui.label_db_console.setText(
                    "Adding Server from " + self.datapath + " to current database")
                # Database connection setup for Importing
                dbimportdir = self.datapath
                connimport = sqlite3.connect(dbimportdir)
                cidb = connimport.cursor()
                cidb.execute(
                    "select alias,ipaddress,queryport,rconport,rconpw FROM server")
                dbimport_result = cidb.fetchall()
                connimport.commit()
                self.c.execute("select count(*) FROM server")
                dbcount_result = self.c.fetchone()
                self.conn.commit()
                importer_id = dbcount_result[0] + 1
                for import_result in dbimport_result:
                    import_id = importer_id
                    import_server_alias = import_result[0]
                    import_server_ip = import_result[1]
                    import_server_queryport = import_result[2]
                    import_server_rconport = import_result[3]
                    import_server_rconpw = import_result[4]
                    self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                                   'id': import_id, 'alias': import_server_alias, 'ipaddress': import_server_ip, 'queryport': import_server_queryport, 'rconport': import_server_rconport, 'rconpw': import_server_rconpw})
                    importer_id += 1
                self.conn.commit()
                self.gui.label_db_console.setText(
                    "Added Server from " + self.data_path[0] + " to current database")
                self.gui.label_selected_db.clear()
                self.fill_dropdown_server_box()
                self.create_server_table_widget()
                self.fill_server_table_widget()
                self.datapath = None
            else:
                self.gui.label_db_console.setText(
                    "Please select a database first!")

        elif db_action == 'replace_db':
            if self.datapath != None and self.datapath.endswith(".db"):
                self.gui.label_db_console.setText(
                    "Replacing Server from " + self.datapath + " in current database")
                # Database connection setup for Importing
                dbimportdir = self.datapath
                connimport = sqlite3.connect(dbimportdir)
                cidb = connimport.cursor()
                cidb.execute("select * FROM server")
                dbimport_result = cidb.fetchall()
                connimport.commit()
                try:
                    cidb.execute("select version FROM configuration")
                    dbi_result = cidb.fetchone()
                    old_db_version = float(dbi_result[0])
                    connimport.commit()
                except Exception:
                    old_db_version = None
                #
                # Show Import Dialog
                #

                def showImport_Dialog():
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                    msgBox.setIcon(QtWidgets.QMessageBox.Warning)
                    msgBox.setText(
                        "Really replace all servers in the current DB with the Servers from the given DB?\n\nConsider creating a backup of the DB file before clicking 'Yes':\n\n" + str(self.dbdir / 'db/isrt_data.db'))
                    msgBox.setWindowTitle("ISRT DB Import Warning")
                    msgBox.setStandardButtons(
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
                    msgBox.buttonClicked.connect(delete_and_import_db)
                    msgBox.exec()
                #
                # Delete All and replace
                #

                def delete_and_import_db(i):
                    if i.text() == "&Yes":
                        if old_db_version:
                            if old_db_version >= 0.8:
                                self.c.execute("DELETE FROM server")
                                self.conn.commit()
                                for import_result in dbimport_result:
                                    import_id = import_result[0]
                                    import_server_alias = import_result[1]
                                    import_server_ip = import_result[2]
                                    import_server_queryport = import_result[3]
                                    import_server_rconport = import_result[4]
                                    import_server_rconpw = import_result[5]
                                    self.c.execute("INSERT INTO server VALUES (:id, :alias, :ipaddress, :queryport, :rconport, :rconpw)", {
                                                   'id': import_id, 'alias': import_server_alias, 'ipaddress': import_server_ip, 'queryport': import_server_queryport, 'rconport': import_server_rconport, 'rconpw': import_server_rconpw})
                                self.conn.commit()
                                self.gui.label_db_console.setText(
                                    "Replaced Server from " + self.data_path[0] + " in current database")
                                self.gui.label_selected_db.clear()
                                self.fill_dropdown_server_box()
                                self.create_server_table_widget()
                                self.fill_server_table_widget()
                                self.datapath = None
                            elif old_db_version == 0.7:
                                self.c.execute("DELETE FROM server")
                                self.conn.commit()
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
                                self.conn.commit()
                                self.gui.label_db_console.setText(
                                    "Replaced Server from " + self.data_path[0] + " in current database")
                                self.gui.label_selected_db.clear()
                                self.fill_dropdown_server_box()
                                self.create_server_table_widget()
                                self.fill_server_table_widget()
                                self.datapath = None
                            else:
                                msg = QtWidgets.QMessageBox()
                                msg.setWindowIcon(
                                    QtGui.QIcon(".\\img/isrt.ico"))
                                msg.setIcon(QtWidgets.QMessageBox.Warning)
                                msg.setWindowTitle("ISRT Error Message")
                                msg.setText(
                                    "The database is from before v0.7, which cannot replace this version's DB.\n\nYou can import the old servers using 'Add'-Function in the Server Manager!")
                                msg.exec_()
                        else:
                            msg = QtWidgets.QMessageBox()
                            msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                            msg.setIcon(QtWidgets.QMessageBox.Warning)
                            msg.setWindowTitle("ISRT Error Message")
                            msg.setText(
                                "The database is from before v0.7, which cannot replace this version's DB.\n\nYou can import the old servers using 'Add'-Function in the Server Manager!")
                            msg.exec_()
                    else:
                        self.gui.label_db_console.setText("Import canceled!")
                        self.gui.label_selected_db.clear()

                showImport_Dialog()
            else:
                self.gui.label_db_console.setText(
                    "Please select a database first!")
    # Backup current Server-DB

    def create_db_backup(self):
        # Define a timestamp format for backup
        FORMAT = '%Y%m%d%H%M%S'
        db_backup_directory = (str(self.dbdir) + '/db/')
        db_source_filename = (db_backup_directory + 'isrt_data.db')
        db_backup_filename = (db_backup_directory +
                              datetime.now().strftime(FORMAT) + '_isrt_data.db')
        copy2(str(db_source_filename), str(db_backup_filename))
        dbb_filename = db_backup_filename.replace("\\", "/")
        self.gui.label_db_console.setText(
            "Backup created at: \n" + dbb_filename)
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # Map Manager
    #
    # Fill Map Manager Dropdown with DB data

    def fill_map_manager_dropdown(self):
        self.gui.dropdown_mapmgr_selector.clear()
        self.gui.btn_mapmgr_delete.setEnabled(False)
        self.gui.btn_mapmgr_save.setEnabled(False)
        self.c.execute("Select map_name from map_config ORDER by map_name")
        map_names_result = self.c.fetchall()
        for map_name in map_names_result:
            self.gui.dropdown_mapmgr_selector.addItem(map_name[0])
    # Fill Map Manager configuration Tab with DB data

    def fill_map_manager_conf_tab(self):
        def clear_map_conf_inserts():
            self.gui.chkbox_mapmgr_day.setEnabled(True)
            self.gui.chkbox_mapmgr_night.setEnabled(True)
            self.gui.chkbox_mapmgr_day.setChecked(False)
            self.gui.chkbox_mapmgr_night.setChecked(False)
            self.gui.le_mapmgr_scenario_cp.setEnabled(True)
            self.gui.le_mapmgr_scenario_cphc.setEnabled(True)
            self.gui.le_mapmgr_scenario_dom.setEnabled(True)
            self.gui.le_mapmgr_scenario_ffw.setEnabled(True)
            self.gui.le_mapmgr_scenario_fl.setEnabled(True)
            self.gui.le_mapmgr_scenario_pu.setEnabled(True)
            self.gui.le_mapmgr_scenario_ski.setEnabled(True)
            self.gui.le_mapmgr_scenario_cpins.setEnabled(True)
            self.gui.le_mapmgr_scenario_cphcins.setEnabled(True)
            self.gui.le_mapmgr_scenario_tdm.setEnabled(True)
            self.gui.le_mapmgr_scenario_ffe.setEnabled(True)
            self.gui.le_mapmgr_scenario_op.setEnabled(True)
            self.gui.le_mapmgr_scenario_puins.setEnabled(True)
            self.gui.le_mapmgr_alias.setText("")
            self.gui.le_mapmgr_name.setText("")
            self.gui.le_mapmgr_modid.setText("")
            self.gui.le_mapmgr_selected_day_image.setText("")
            self.gui.le_mapmgr_selected_night_image.setText("")
            self.gui.le_mapmgr_scenario_cp.setText("")
            self.gui.le_mapmgr_scenario_cphc.setText("")
            self.gui.le_mapmgr_scenario_dom.setText("")
            self.gui.le_mapmgr_scenario_ffw.setText("")
            self.gui.le_mapmgr_scenario_fl.setText("")
            self.gui.le_mapmgr_scenario_pu.setText("")
            self.gui.le_mapmgr_scenario_ski.setText("")
            self.gui.le_mapmgr_scenario_cpins.setText("")
            self.gui.le_mapmgr_scenario_cphcins.setText("")
            self.gui.le_mapmgr_scenario_tdm.setText("")
            self.gui.le_mapmgr_scenario_ffe.setText("")
            self.gui.le_mapmgr_scenario_op.setText("")
            self.gui.le_mapmgr_scenario_puins.setText("")
            self.gui.le_mapmgr_selected_day_image.setText("")
            self.gui.le_mapmgr_selected_night_image.setText("")
            self.gui.le_mapmgr_scenario_cp.setPlaceholderText(
                "Checkpoint Scenario Security")
            self.gui.le_mapmgr_scenario_cphc.setPlaceholderText(
                "Checkpoint Hardcore Scenario Security")
            self.gui.le_mapmgr_scenario_dom.setPlaceholderText(
                "Domination Scenario")
            self.gui.le_mapmgr_scenario_ffw.setPlaceholderText(
                "Firefight West Scenario")
            self.gui.le_mapmgr_scenario_fl.setPlaceholderText(
                "Frontline Scenario")
            self.gui.le_mapmgr_scenario_pu.setPlaceholderText(
                "Push Scenario Security")
            self.gui.le_mapmgr_scenario_ski.setPlaceholderText(
                "Skirmish Scenario")
            self.gui.le_mapmgr_scenario_cpins.setPlaceholderText(
                "Checkpoint Scenario Insurgents")
            self.gui.le_mapmgr_scenario_cphcins.setPlaceholderText(
                "Checkpoint Hardcore Scenario Insurgents")
            self.gui.le_mapmgr_scenario_tdm.setPlaceholderText(
                "Team Deathmatch Scenario")
            self.gui.le_mapmgr_scenario_ffe.setPlaceholderText(
                "Firefight East Scenario")
            self.gui.le_mapmgr_scenario_op.setPlaceholderText(
                "Outpost Scenario")
            self.gui.le_mapmgr_scenario_puins.setPlaceholderText(
                "Push Scenario Insurgents")
            self.gui.le_mapmgr_selected_day_image.setPlaceholderText(
                "Map Image Name Day")
            self.gui.le_mapmgr_selected_night_image.setPlaceholderText(
                "Map Image Name Night")
        clear_map_conf_inserts()
        self.selected_map_conf = self.gui.dropdown_mapmgr_selector.currentText()
        self.c.execute("select * from map_config where map_name=:selected_map",
                       {'selected_map': self.selected_map_conf})
        self.map_conf_result = self.c.fetchall()
        self.gui.label_db_console_2.append(
            f"Map {self.selected_map_conf} loaded")
        self.map_configuration = self.map_conf_result[0]
        self.map_modid = self.map_configuration[2]
        # Set the configuration in case the called map is a non-Standard map

        def set_map_mgr_conf_non_std():
            self.map_name = self.map_configuration[0]
            self.map_alias = self.map_configuration[1]
            self.map_modid = self.map_configuration[2]
            self.map_day = self.map_configuration[3]
            self.map_night = self.map_configuration[4]
            self.map_dn = (
                str(self.map_configuration[3]) + str(self.map_configuration[4]))
            self.map_day_pic_show = self.map_configuration[5]
            self.map_night_pic_temp = self.map_day_pic_show.split(".")
            self.map_night_pic_show = (
                self.map_night_pic_temp[0] + "_night.jpg")
            self.map_scenario_cphc = self.map_configuration[6]
            self.map_scenario_cphcins = self.map_configuration[7]
            self.map_scenario_cp = self.map_configuration[8]
            self.map_scenario_cpins = self.map_configuration[9]
            self.map_scenario_dom = self.map_configuration[10]
            self.map_scenario_ffe = self.map_configuration[11]
            self.map_scenario_ffw = self.map_configuration[12]
            self.map_scenario_fl = self.map_configuration[13]
            self.map_scenario_op = self.map_configuration[14]
            self.map_scenario_pu = self.map_configuration[15]
            self.map_scenario_puins = self.map_configuration[16]
            self.map_scenario_ski = self.map_configuration[17]
            self.map_scenario_tdm = self.map_configuration[18]
            self.map_self_added = self.map_configuration[19]
            self.gui.le_mapmgr_alias.setText(self.map_name)
            self.gui.le_mapmgr_name.setText(self.map_alias)

            self.gui.le_mapmgr_scenario_cp.setEnabled(True)
            self.gui.le_mapmgr_scenario_cphc.setEnabled(True)
            self.gui.le_mapmgr_scenario_dom.setEnabled(True)
            self.gui.le_mapmgr_scenario_ffw.setEnabled(True)
            self.gui.le_mapmgr_scenario_fl.setEnabled(True)
            self.gui.le_mapmgr_scenario_pu.setEnabled(True)
            self.gui.le_mapmgr_scenario_ski.setEnabled(True)
            self.gui.le_mapmgr_scenario_cpins.setEnabled(True)
            self.gui.le_mapmgr_scenario_cphcins.setEnabled(True)
            self.gui.le_mapmgr_scenario_tdm.setEnabled(True)
            self.gui.le_mapmgr_scenario_ffe.setEnabled(True)
            self.gui.le_mapmgr_scenario_op.setEnabled(True)
            self.gui.le_mapmgr_scenario_puins.setEnabled(True)
            self.gui.le_mapmgr_selected_day_image.setEnabled(False)
            self.gui.btn_mapmgr_select_day_image.setEnabled(False)
            self.gui.le_mapmgr_selected_night_image.setEnabled(False)
            self.gui.btn_mapmgr_select_night_image_2.setEnabled(False)
            self.gui.le_mapmgr_selected_night_image.setEnabled(False)
            self.gui.le_mapmgr_name.setEnabled(False)
            self.gui.btn_mapmgr_add.setEnabled(False)
            self.gui.btn_mapmgr_save.setEnabled(True)
            self.gui.chkbox_mapmgr_day.setEnabled(False)
            self.gui.chkbox_mapmgr_night.setEnabled(False)
            self.gui.le_mapmgr_alias.setEnabled(False)
            self.gui.le_mapmgr_modid.setEnabled(False)

            if self.map_self_added == 0:
                self.gui.btn_mapmgr_delete.setEnabled(False)

                if self.map_day == 1:
                    self.gui.le_mapmgr_selected_day_image.setText(
                        self.map_day_pic_show)
                    self.gui.img_view_day_map.setStyleSheet(
                        f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_day_pic_show});")
                else:
                    self.gui.img_view_day_map.setStyleSheet(
                        f"background-color: rgb(240, 240, 240); border-width: 0px; border-style: solid")
                    self.gui.le_mapmgr_selected_day_image.setText("")

                if self.map_night == 1:
                    self.gui.img_view_night_map.setStyleSheet(
                        f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_night_pic_show});")
                    self.gui.le_mapmgr_selected_night_image.setText(
                        self.map_night_pic_show)
                else:
                    self.gui.img_view_night_map.setStyleSheet(
                        f"background-color: rgb(240, 240, 240); border-width: 0px; border-style: solid")
                    self.gui.le_mapmgr_selected_night_image.setText("")

            else:
                self.gui.btn_mapmgr_delete.setEnabled(True)
                custom_image_folder = (
                    str(self.dbdir) + '\\img\\custom_map_pics\\')
                custom_day_pic_temp = (
                    str(self.dbdir) + '\\img\\custom_map_pics\\' + self.map_day_pic_show)
                custom_night_pic_temp = (
                    str(self.dbdir) + '\\img\\custom_map_pics\\' + self.map_night_pic_show)

                custom_day_pic = custom_day_pic_temp.replace("\\", "/")
                custom_night_pic = custom_night_pic_temp.replace("\\", "/")

                if self.map_day == 1:
                    self.gui.le_mapmgr_selected_day_image.setText(
                        self.map_day_pic_show)
                    self.gui.img_view_day_map.setStyleSheet(
                        f"border-image: url({custom_day_pic});")
                else:
                    self.gui.img_view_day_map.setStyleSheet(
                        f"border-image: url(:/map_view/img/maps/map_views.jpg);")
                    self.gui.btn_mapmgr_select_day_image.setEnabled(False)
                    self.gui.le_mapmgr_selected_day_image.setText("")

                if self.map_night == 1:
                    self.gui.img_view_night_map.setStyleSheet(
                        f"border-image: url({custom_night_pic});")
                    self.gui.le_mapmgr_selected_night_image.setText(
                        self.map_night_pic_show)
                else:
                    self.gui.img_view_night_map.setStyleSheet(
                        f"border-image: url(:/map_view/img/maps/map_views_night.jpg);")
                    self.gui.le_mapmgr_selected_night_image.setText("")
                    self.gui.btn_mapmgr_select_night_image_2.setEnabled(False)

            if self.map_modid == 0:
                self.gui.le_mapmgr_modid.setText("Std")
            else:
                self.gui.le_mapmgr_modid.setText(str(self.map_modid))

            if self.map_day == 1:
                self.gui.chkbox_mapmgr_day.setChecked(True)
            else:
                self.gui.chkbox_mapmgr_day.setChecked(False)

            if self.map_night == 1:
                self.gui.chkbox_mapmgr_night.setChecked(True)
            else:
                self.gui.chkbox_mapmgr_night.setChecked(False)

            if self.map_scenario_cphc:
                self.gui.le_mapmgr_scenario_cphc.setText(
                    self.map_scenario_cphc)
            else:
                self.gui.le_mapmgr_scenario_cphc.setPlaceholderText("N/A")

            if self.map_scenario_cp:
                self.gui.le_mapmgr_scenario_cp.setText(self.map_scenario_cp)
            else:
                self.gui.le_mapmgr_scenario_cp.setPlaceholderText("N/A")

            if self.map_scenario_cpins:
                self.gui.le_mapmgr_scenario_cpins.setText(
                    self.map_scenario_cpins)
            else:
                self.gui.le_mapmgr_scenario_cpins.setPlaceholderText("N/A")

            if self.map_scenario_cphcins:
                self.gui.le_mapmgr_scenario_cphcins.setText(
                    self.map_scenario_cphcins)
            else:
                self.gui.le_mapmgr_scenario_cphcins.setPlaceholderText("N/A")

            if self.map_scenario_dom:
                self.gui.le_mapmgr_scenario_dom.setText(self.map_scenario_dom)
            else:
                self.gui.le_mapmgr_scenario_dom.setPlaceholderText("N/A")

            if self.map_scenario_ffw:
                self.gui.le_mapmgr_scenario_ffw.setText(self.map_scenario_ffw)
            else:
                self.gui.le_mapmgr_scenario_ffw.setPlaceholderText("N/A")

            if self.map_scenario_ffe:
                self.gui.le_mapmgr_scenario_ffe.setText(self.map_scenario_ffe)
            else:
                self.gui.le_mapmgr_scenario_ffe.setPlaceholderText("N/A")

            if self.map_scenario_fl:
                self.gui.le_mapmgr_scenario_fl.setText(self.map_scenario_fl)
            else:
                self.gui.le_mapmgr_scenario_fl.setPlaceholderText("N/A")

            if self.map_scenario_pu:
                self.gui.le_mapmgr_scenario_pu.setText(self.map_scenario_pu)
            else:
                self.gui.le_mapmgr_scenario_pu.setPlaceholderText("N/A")

            if self.map_scenario_puins:
                self.gui.le_mapmgr_scenario_puins.setText(
                    self.map_scenario_puins)
            else:
                self.gui.le_mapmgr_scenario_puins.setPlaceholderText("N/A")

            if self.map_scenario_ski:
                self.gui.le_mapmgr_scenario_ski.setText(self.map_scenario_ski)
            else:
                self.gui.le_mapmgr_scenario_ski.setPlaceholderText("N/A")

            if self.map_scenario_op:
                self.gui.le_mapmgr_scenario_op.setText(self.map_scenario_op)
            else:
                self.gui.le_mapmgr_scenario_op.setPlaceholderText("N/A")

            if self.map_scenario_tdm:
                self.gui.le_mapmgr_scenario_tdm.setText(self.map_scenario_tdm)
            else:
                self.gui.le_mapmgr_scenario_tdm.setPlaceholderText("N/A")
        # Set the configuration in case the called map is a Standard map

        def set_map_mgr_conf_std():
            self.map_name = self.map_configuration[0]
            self.map_alias = self.map_configuration[1]
            self.map_day = self.map_configuration[3]
            self.map_night = self.map_configuration[4]
            self.map_dn = (
                str(self.map_configuration[3]) + str(self.map_configuration[4]))
            self.map_day_pic = self.map_configuration[5]
            self.map_night_pic_temp = self.map_day_pic.split(".")
            self.map_night_pic = (self.map_night_pic_temp[0] + "_night.jpg")
            self.map_scenario_cphc = self.map_configuration[6]
            self.map_scenario_cphcins = self.map_configuration[7]
            self.map_scenario_cp = self.map_configuration[8]
            self.map_scenario_cpins = self.map_configuration[9]
            self.map_scenario_dom = self.map_configuration[10]
            self.map_scenario_ffe = self.map_configuration[11]
            self.map_scenario_ffw = self.map_configuration[12]
            self.map_scenario_fl = self.map_configuration[13]
            self.map_scenario_op = self.map_configuration[14]
            self.map_scenario_pu = self.map_configuration[15]
            self.map_scenario_puins = self.map_configuration[16]
            self.map_scenario_ski = self.map_configuration[17]
            self.map_scenario_tdm = self.map_configuration[18]
            self.map_self_added = self.map_configuration[19]

            self.gui.le_mapmgr_scenario_cp.setEnabled(False)
            self.gui.le_mapmgr_scenario_cphc.setEnabled(False)
            self.gui.le_mapmgr_scenario_dom.setEnabled(False)
            self.gui.le_mapmgr_scenario_ffw.setEnabled(False)
            self.gui.le_mapmgr_scenario_fl.setEnabled(False)
            self.gui.le_mapmgr_scenario_pu.setEnabled(False)
            self.gui.le_mapmgr_scenario_ski.setEnabled(False)
            self.gui.le_mapmgr_scenario_cpins.setEnabled(False)
            self.gui.le_mapmgr_scenario_cphcins.setEnabled(False)
            self.gui.le_mapmgr_scenario_tdm.setEnabled(False)
            self.gui.le_mapmgr_scenario_ffe.setEnabled(False)
            self.gui.le_mapmgr_scenario_op.setEnabled(False)
            self.gui.le_mapmgr_scenario_puins.setEnabled(False)

            if self.map_self_added == 0:
                self.gui.btn_mapmgr_delete.setEnabled(False)
                self.gui.btn_mapmgr_add.setEnabled(False)
                self.gui.btn_mapmgr_save.setEnabled(False)
                self.gui.chkbox_mapmgr_day.setEnabled(False)
                self.gui.chkbox_mapmgr_night.setEnabled(False)
                self.gui.le_mapmgr_alias.setEnabled(False)
                self.gui.le_mapmgr_name.setEnabled(False)
                self.gui.le_mapmgr_modid.setEnabled(False)
                self.gui.le_mapmgr_selected_day_image.setEnabled(False)
                self.gui.btn_mapmgr_select_day_image.setEnabled(False)
                self.gui.le_mapmgr_selected_night_image.setEnabled(False)
                self.gui.btn_mapmgr_select_night_image_2.setEnabled(False)
            else:
                self.gui.btn_mapmgr_delete.setEnabled(True)

            self.gui.le_mapmgr_alias.setText(self.map_name)
            self.gui.le_mapmgr_name.setText(self.map_alias)

            if self.map_day == 1:
                self.gui.chkbox_mapmgr_day.setChecked(True)
            else:
                self.gui.chkbox_mapmgr_day.setChecked(False)

            if self.map_night == 1:
                self.gui.chkbox_mapmgr_night.setChecked(True)
            else:
                self.gui.chkbox_mapmgr_night.setChecked(False)

            if self.map_day == 1:
                self.gui.le_mapmgr_selected_day_image.setText(self.map_day_pic)
                self.gui.img_view_day_map.setStyleSheet(
                    f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_day_pic});")
            else:
                self.gui.img_view_day_map.setStyleSheet(
                    f"border-image: url(:/map_view/img/maps/map_views.jpg);")
                self.gui.btn_mapmgr_select_day_image.setEnabled(False)
                self.gui.le_mapmgr_selected_day_image.setText("")

            if self.map_night == 1:
                self.gui.img_view_night_map.setStyleSheet(
                    f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_night_pic});")
                self.gui.le_mapmgr_selected_night_image.setText(
                    self.map_night_pic)
            else:
                self.gui.img_view_night_map.setStyleSheet(
                    f"border-image: url(:/map_view/img/maps/map_views_night.jpg);")
                self.gui.le_mapmgr_selected_night_image.setText("")
                self.gui.btn_mapmgr_select_night_image_2.setEnabled(False)

            if self.map_scenario_cphc:
                self.gui.le_mapmgr_scenario_cphc.setText(
                    self.map_scenario_cphc)
            else:
                self.gui.le_mapmgr_scenario_cphc.setPlaceholderText("N/A")

            if self.map_scenario_cp:
                self.gui.le_mapmgr_scenario_cp.setText(self.map_scenario_cp)
            else:
                self.gui.le_mapmgr_scenario_cp.setPlaceholderText("N/A")

            if self.map_scenario_cpins:
                self.gui.le_mapmgr_scenario_cpins.setText(
                    self.map_scenario_cpins)
            else:
                self.gui.le_mapmgr_scenario_cpins.setPlaceholderText("N/A")

            if self.map_scenario_cphcins:
                self.gui.le_mapmgr_scenario_cphcins.setText(
                    self.map_scenario_cphcins)
            else:
                self.gui.le_mapmgr_scenario_cphcins.setPlaceholderText("N/A")

            if self.map_scenario_dom:
                self.gui.le_mapmgr_scenario_dom.setText(self.map_scenario_dom)
            else:
                self.gui.le_mapmgr_scenario_dom.setPlaceholderText("N/A")

            if self.map_scenario_ffw:
                self.gui.le_mapmgr_scenario_ffw.setText(self.map_scenario_ffw)
            else:
                self.gui.le_mapmgr_scenario_ffw.setPlaceholderText("N/A")

            if self.map_scenario_ffe:
                self.gui.le_mapmgr_scenario_ffe.setText(self.map_scenario_ffe)
            else:
                self.gui.le_mapmgr_scenario_ffe.setPlaceholderText("N/A")

            if self.map_scenario_fl:
                self.gui.le_mapmgr_scenario_fl.setText(self.map_scenario_fl)
            else:
                self.gui.le_mapmgr_scenario_fl.setPlaceholderText("N/A")

            if self.map_scenario_pu:
                self.gui.le_mapmgr_scenario_pu.setText(self.map_scenario_pu)
            else:
                self.gui.le_mapmgr_scenario_pu.setPlaceholderText("N/A")

            if self.map_scenario_puins:
                self.gui.le_mapmgr_scenario_puins.setText(
                    self.map_scenario_puins)
            else:
                self.gui.le_mapmgr_scenario_puins.setPlaceholderText("N/A")

            if self.map_scenario_ski:
                self.gui.le_mapmgr_scenario_ski.setText(self.map_scenario_ski)
            else:
                self.gui.le_mapmgr_scenario_ski.setPlaceholderText("N/A")

            if self.map_scenario_op:
                self.gui.le_mapmgr_scenario_op.setText(self.map_scenario_op)
            else:
                self.gui.le_mapmgr_scenario_op.setPlaceholderText("N/A")

            if self.map_scenario_tdm:
                self.gui.le_mapmgr_scenario_tdm.setText(self.map_scenario_tdm)
            else:
                self.gui.le_mapmgr_scenario_tdm.setPlaceholderText("N/A")

        # Set the correct ID for Standard Maps
        if self.map_modid == 0:
            self.gui.le_mapmgr_modid.setText("Std")
            set_map_mgr_conf_std()
        else:
            self.gui.le_mapmgr_modid.setText(str(self.map_modid))
            set_map_mgr_conf_non_std()

        self.gui.le_mapmgr_scenario_cp.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_cphc.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_dom.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_ffw.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_fl.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_pu.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_ski.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_cpins.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_cphcins.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_tdm.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_ffe.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_op.setCursorPosition(1)
        self.gui.le_mapmgr_scenario_puins.setCursorPosition(1)
    # Function to clear the map configuration page

    def clear_map_manager(self):
        self.gui.dropdown_mapmgr_selector.clear()
        self.gui.btn_mapmgr_delete.setEnabled(False)
        self.gui.btn_mapmgr_add.setEnabled(True)
        self.gui.btn_mapmgr_save.setEnabled(True)
        self.fill_map_manager_dropdown()
        self.gui.le_mapmgr_alias.setEnabled(True)
        self.gui.le_mapmgr_name.setEnabled(True)
        self.gui.le_mapmgr_modid.setEnabled(True)
        self.gui.le_mapmgr_selected_day_image.setEnabled(True)
        self.gui.btn_mapmgr_select_day_image.setEnabled(True)
        self.gui.le_mapmgr_selected_night_image.setEnabled(True)
        self.gui.btn_mapmgr_select_night_image_2.setEnabled(True)
        self.gui.chkbox_mapmgr_day.setEnabled(True)
        self.gui.chkbox_mapmgr_night.setEnabled(True)
        self.gui.chkbox_mapmgr_day.setChecked(False)
        self.gui.chkbox_mapmgr_night.setChecked(False)
        self.gui.le_mapmgr_scenario_cp.setEnabled(True)
        self.gui.le_mapmgr_scenario_cphc.setEnabled(True)
        self.gui.le_mapmgr_scenario_dom.setEnabled(True)
        self.gui.le_mapmgr_scenario_ffw.setEnabled(True)
        self.gui.le_mapmgr_scenario_fl.setEnabled(True)
        self.gui.le_mapmgr_scenario_pu.setEnabled(True)
        self.gui.le_mapmgr_scenario_ski.setEnabled(True)
        self.gui.le_mapmgr_scenario_cpins.setEnabled(True)
        self.gui.le_mapmgr_scenario_cphcins.setEnabled(True)
        self.gui.le_mapmgr_scenario_tdm.setEnabled(True)
        self.gui.le_mapmgr_scenario_ffe.setEnabled(True)
        self.gui.le_mapmgr_scenario_op.setEnabled(True)
        self.gui.le_mapmgr_scenario_puins.setEnabled(True)
        self.gui.le_mapmgr_alias.setText("")
        self.gui.le_mapmgr_name.setText("")
        self.gui.le_mapmgr_modid.setText("")
        self.gui.le_mapmgr_selected_day_image.setText("")
        self.gui.le_mapmgr_selected_night_image.setText("")
        self.gui.le_mapmgr_scenario_cp.setText("")
        self.gui.le_mapmgr_scenario_cphc.setText("")
        self.gui.le_mapmgr_scenario_dom.setText("")
        self.gui.le_mapmgr_scenario_ffw.setText("")
        self.gui.le_mapmgr_scenario_fl.setText("")
        self.gui.le_mapmgr_scenario_pu.setText("")
        self.gui.le_mapmgr_scenario_ski.setText("")
        self.gui.le_mapmgr_scenario_cpins.setText("")
        self.gui.le_mapmgr_scenario_cphcins.setText("")
        self.gui.le_mapmgr_scenario_tdm.setText("")
        self.gui.le_mapmgr_scenario_ffe.setText("")
        self.gui.le_mapmgr_scenario_op.setText("")
        self.gui.le_mapmgr_scenario_puins.setText("")
        self.gui.le_mapmgr_selected_day_image.setText("")
        self.gui.le_mapmgr_selected_night_image.setText("")
        self.gui.le_mapmgr_scenario_cp.setPlaceholderText(
            "Checkpoint Scenario Security")
        self.gui.le_mapmgr_scenario_cphc.setPlaceholderText(
            "Checkpoint Hardcore Scenario Security")
        self.gui.le_mapmgr_scenario_dom.setPlaceholderText(
            "Domination Scenario")
        self.gui.le_mapmgr_scenario_ffw.setPlaceholderText(
            "Firefight West Scenario")
        self.gui.le_mapmgr_scenario_fl.setPlaceholderText("Frontline Scenario")
        self.gui.le_mapmgr_scenario_pu.setPlaceholderText(
            "Push Scenario Security")
        self.gui.le_mapmgr_scenario_ski.setPlaceholderText("Skirmish Scenario")
        self.gui.le_mapmgr_scenario_cpins.setPlaceholderText(
            "Checkpoint Scenario Insurgents")
        self.gui.le_mapmgr_scenario_cphcins.setPlaceholderText(
            "Checkpoint Hardcore Scenario Insurgents")
        self.gui.le_mapmgr_scenario_tdm.setPlaceholderText(
            "Team Deathmatch Scenario")
        self.gui.le_mapmgr_scenario_ffe.setPlaceholderText(
            "Firefight East Scenario")
        self.gui.le_mapmgr_scenario_op.setPlaceholderText("Outpost Scenario")
        self.gui.le_mapmgr_scenario_puins.setPlaceholderText(
            "Push Scenario Insurgents")
        self.gui.le_mapmgr_selected_day_image.setPlaceholderText(
            "Map Image Name Day")
        self.gui.le_mapmgr_selected_night_image.setPlaceholderText(
            "Map Image Name Night")
        self.gui.img_view_day_map.setStyleSheet(
            "border-image: url(:/img/img/day.jpg);")
        self.gui.img_view_night_map.setStyleSheet(
            "border-image: url(:/img/img/night.jpg);")
    # Save modified map in DB

    def save_existing_map(self):
        self.gui.label_db_console_2.clear()
        self.check_val_update_map_error = 0

        def get_changed_variables():
            self.val_map_alias = self.gui.le_mapmgr_name.text()

            self.c.execute("select map_alias from map_config")
            map_aliases = self.c.fetchall()
            self.conn.commit()
            self.map_already_there = 0
            for alias_check in map_aliases:
                if self.val_map_alias == alias_check[0]:
                    self.map_already_there = 1

            if self.map_already_there == 0:
                self.check_val_update_map_error = 599
                self.gui.label_db_console_2.append(
                    "Map does not exist in DB - add it first!")

            self.val_map_cphc = self.gui.le_mapmgr_scenario_cphc.text()
            self.val_map_cphcins = self.gui.le_mapmgr_scenario_cphcins.text()
            self.val_map_cp = self.gui.le_mapmgr_scenario_cp.text()
            self.val_map_cpins = self.gui.le_mapmgr_scenario_cpins.text()
            self.val_map_dom = self.gui.le_mapmgr_scenario_dom.text()
            self.val_map_ffe = self.gui.le_mapmgr_scenario_ffe.text()
            self.val_map_ffw = self.gui.le_mapmgr_scenario_ffw.text()
            self.val_map_fl = self.gui.le_mapmgr_scenario_fl.text()
            self.val_map_op = self.gui.le_mapmgr_scenario_op.text()
            self.val_map_pu = self.gui.le_mapmgr_scenario_pu.text()
            self.val_map_puins = self.gui.le_mapmgr_scenario_puins.text()
            self.val_map_ski = self.gui.le_mapmgr_scenario_ski.text()
            self.val_map_tdm = self.gui.le_mapmgr_scenario_tdm.text()

        def check_if_map_info_complete_change():
            if (self.gui.le_mapmgr_scenario_cp.text() == "" and
                self.gui.le_mapmgr_scenario_cpins.text() == "" and
                self.gui.le_mapmgr_scenario_cphc.text() == "" and
                self.gui.le_mapmgr_scenario_cphcins.text() == "" and
                self.gui.le_mapmgr_scenario_dom.text() == "" and
                self.gui.le_mapmgr_scenario_tdm.text() == "" and
                self.gui.le_mapmgr_scenario_ffw.text() == "" and
                self.gui.le_mapmgr_scenario_ffe.text() == "" and
                self.gui.le_mapmgr_scenario_fl.text() == "" and
                self.gui.le_mapmgr_scenario_op.text() == "" and
                self.gui.le_mapmgr_scenario_pu.text() == "" and
                self.gui.le_mapmgr_scenario_puins.text() == "" and
                    self.gui.le_mapmgr_scenario_ski.text() == ""):
                self.gui.label_db_console_2.append(
                    "You have to provide at least one map scenario!")
                self.check_val_update_map_error += 161

        get_changed_variables()
        check_if_map_info_complete_change()

        def update_changed_map_vars():
            self.c.execute("UPDATE map_config SET checkpointhardcore=:checkpointhardcore, checkpointhardcore_ins=:checkpointhardcore_ins, checkpoint=:checkpoint, checkpoint_ins=:checkpoint_ins, domination=:domination, firefight_east=:firefight_east, firefight_west=:firefight_west, frontline=:frontline, outpost=:outpost, push=:push, push_ins=:push_ins, skirmish=:skirmish, teamdeathmatch=:teamdeathmatch WHERE map_alias=:map_alias",
                           {'map_alias': self.val_map_alias, 'checkpointhardcore': self.val_map_cphc, 'checkpointhardcore_ins': self.val_map_cphcins, 'checkpoint': self.val_map_cp, 'checkpoint_ins': self.val_map_cpins, 'domination': self.val_map_dom, 'firefight_east': self.val_map_ffe, 'firefight_west': self.val_map_ffw, 'frontline': self.val_map_fl, 'outpost': self.val_map_op, 'push': self.val_map_pu, 'push_ins': self.val_map_puins, 'skirmish': self.val_map_ski, 'teamdeathmatch': self.val_map_tdm})
            self.conn.commit()

        # Check for any errors in the above methods and if 0 really add map
        if self.check_val_update_map_error == 0:
            self.gui.label_db_console_2.clear()
            update_changed_map_vars()
            self.gui.label_db_console_2.append(
                "Map successfully updated in database!")
        # If errors throw message and error code
        else:
            icondir = Path(__file__).absolute().parent
            warningmsg = QtWidgets.QMessageBox()
            warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
            warningmsg.setWindowTitle("ISRT Map Manager Warning")
            warningmsg.setWindowIcon(
                QtGui.QIcon(str(icondir / 'img/isrt.ico')))
            warningmsg.setText(
                f"Something went wrong while updating the map variables.\nPlease check the error message in the console!\n\nError Code: {self.check_val_update_map_error}")
            warningmsg.addButton(warningmsg.Ok)
            warningmsg.exec_()
    # Select map Pics

    def select_map_pic(self, map_light):
        if map_light == "day":
            img_day_select_directory = (str(self.dbdir) + '\\img\\')
            self.day_data_path = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select Image File', img_day_select_directory, '*.jpg',)
            self.gui.le_mapmgr_selected_day_image.setText(
                self.day_data_path[0])
            self.day_datapath = self.day_data_path[0]
            img_night_select_directory = (self.day_data_path[0])
        elif map_light == "night":
            img_night_select_directory = (str(self.dbdir) + '\\img\\')
            self.night_data_path = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Select Image File', img_night_select_directory, '*.jpg',)
            self.gui.le_mapmgr_selected_night_image.setText(
                self.night_data_path[0])
            self.night_datapath = self.night_data_path[0]
    # Add new Map to Map database

    def add_new_map(self):
        self.gui.label_db_console_2.clear()
        self.check_val_add_map_error = 0
        # Read the new Map variables and assign them

        def read_new_map_vars():
            self.map_name = self.gui.le_mapmgr_alias.text()
            self.map_alias = self.gui.le_mapmgr_name.text()
            self.map_modid = self.gui.le_mapmgr_modid.text()
            self.map_day_temp = self.gui.chkbox_mapmgr_day.isChecked()
            self.map_night_temp = self.gui.chkbox_mapmgr_night.isChecked()
            self.map_day_pic = self.gui.le_mapmgr_selected_day_image.text()
            self.map_night_pic_temp = self.gui.le_mapmgr_selected_night_image.text()
            self.map_night_pic = self.gui.le_mapmgr_selected_night_image.text()
            self.map_scenario_cphc = self.gui.le_mapmgr_scenario_cphc.text()
            self.map_scenario_cphcins = self.gui.le_mapmgr_scenario_cphcins.text()
            self.map_scenario_cp = self.gui.le_mapmgr_scenario_cp.text()
            self.map_scenario_cpins = self.gui.le_mapmgr_scenario_cpins.text()
            self.map_scenario_dom = self.gui.le_mapmgr_scenario_dom.text()
            self.map_scenario_ffe = self.gui.le_mapmgr_scenario_ffe.text()
            self.map_scenario_ffw = self.gui.le_mapmgr_scenario_ffw.text()
            self.map_scenario_fl = self.gui.le_mapmgr_scenario_fl.text()
            self.map_scenario_op = self.gui.le_mapmgr_scenario_op.text()
            self.map_scenario_pu = self.gui.le_mapmgr_scenario_pu.text()
            self.map_scenario_puins = self.gui.le_mapmgr_scenario_puins.text()
            self.map_scenario_ski = self.gui.le_mapmgr_scenario_ski.text()
            self.map_scenario_tdm = self.gui.le_mapmgr_scenario_tdm.text()
            self.map_self_added = 1

            if self.map_day_temp == True:
                self.map_day = 1
            else:
                self.map_day = 0
            if self.map_night_temp == True:
                self.map_night = 1
            else:
                self.map_night = 0

            self.map_dn = (str(self.map_day) + str(self.map_night))
        # Check for blanks in the Map Name/Alias and ModID

        def check_for_blanks_in_vars():
            res_check_blanks_alias = bool(re.search(r"\s", self.map_alias))
            res_check_blanks_id = bool(re.search(r"\s", self.map_modid))
            if res_check_blanks_alias == True:
                self.gui.label_db_console_2.append(
                    "The map alias contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 731
            if res_check_blanks_id == True:
                self.gui.label_db_console_2.append(
                    "The map mod ID contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 732

            res_check_blanks_cp = bool(re.search(r"\s", self.map_scenario_cp))
            res_check_blanks_cphcins = bool(
                re.search(r"\s", self.map_scenario_cphcins))
            res_check_blanks_cphc = bool(
                re.search(r"\s", self.map_scenario_cphc))
            res_check_blanks_cpins = bool(
                re.search(r"\s", self.map_scenario_cpins))
            res_check_blanks_dom = bool(
                re.search(r"\s", self.map_scenario_dom))
            res_check_blanks_ffe = bool(
                re.search(r"\s", self.map_scenario_ffe))
            res_check_blanks_ffw = bool(
                re.search(r"\s", self.map_scenario_ffw))
            res_check_blanks_fl = bool(re.search(r"\s", self.map_scenario_fl))
            res_check_blanks_op = bool(re.search(r"\s", self.map_scenario_op))
            res_check_blanks_pu = bool(re.search(r"\s", self.map_scenario_pu))
            res_check_blanks_puins = bool(
                re.search(r"\s", self.map_scenario_puins))
            res_check_blanks_ski = bool(
                re.search(r"\s", self.map_scenario_ski))
            res_check_blanks_tdm = bool(
                re.search(r"\s", self.map_scenario_tdm))

            if res_check_blanks_cp == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Checkpoint Security contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 601
            if res_check_blanks_cpins == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Checkpoint Insurgenty contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 602
            if res_check_blanks_cphc == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Checkpoint Hardcore Security contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 604
            if res_check_blanks_cphcins == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Checkpoint Hardcore Insurgents contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 604
            if res_check_blanks_dom == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Domination contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 605
            if res_check_blanks_ffe == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Firefight East contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 606
            if res_check_blanks_ffw == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Firefight West contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 607
            if res_check_blanks_fl == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Frontline contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 608
            if res_check_blanks_op == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Outpost contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 609
            if res_check_blanks_pu == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Push Security contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 610
            if res_check_blanks_puins == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Push Insurgents contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 611
            if res_check_blanks_ski == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Skirmish contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 612
            if res_check_blanks_tdm == True:
                self.gui.label_db_console_2.append(
                    "The map scenario for Team Death Match contains a blank space - remove it and try again!")
                self.check_val_add_map_error = 613

        # Check if all required information has been entered

        def check_if_map_info_complete():
            if self.map_name:
                pass
            else:
                self.gui.label_db_console_2.append(
                    "Please enter an alias for the map!")
                self.check_val_add_map_error += 110

            if self.map_alias:
                pass
            else:
                self.gui.label_db_console_2.append(
                    "Please enter a name for the map!")
                self.check_val_add_map_error += 120

            if self.map_modid:
                pass
            else:
                self.gui.label_db_console_2.append(
                    "Please enter the MOD.io ID for the map!")
                self.check_val_add_map_error += 130

            if self.map_modid:
                check_numbers = str(self.map_modid)
                if check_numbers.isnumeric() == False:
                    self.gui.label_db_console_2.append(
                        "The Mod.io ID is not numeric - please verify and try again!")
                    self.check_val_add_map_error = 777

            if self.gui.chkbox_mapmgr_day.isChecked() or self.gui.chkbox_mapmgr_night.isChecked():
                pass
            else:
                self.gui.label_db_console_2.append(
                    "Select one lighting scenario at least!")
                self.check_val_add_map_error += 140

            if self.map_day == 1 and self.map_day_pic == "":
                self.gui.label_db_console_2.append(
                    "Please provide a day map pic, if you select day as lighting scenario!")
                self.check_val_add_map_error += 150

            if self.map_night == 1 and self.map_night_pic == "":
                self.gui.label_db_console_2.append(
                    "Please provide a night map pic, if you select night as lighting scenario!")
                self.check_val_add_map_error += 160

            if (self.gui.le_mapmgr_scenario_cp.text() == "" and
                self.gui.le_mapmgr_scenario_cpins.text() == "" and
                self.gui.le_mapmgr_scenario_cphc.text() == "" and
                self.gui.le_mapmgr_scenario_cphcins.text() == "" and
                self.gui.le_mapmgr_scenario_dom.text() == "" and
                self.gui.le_mapmgr_scenario_tdm.text() == "" and
                self.gui.le_mapmgr_scenario_ffw.text() == "" and
                self.gui.le_mapmgr_scenario_ffe.text() == "" and
                self.gui.le_mapmgr_scenario_fl.text() == "" and
                self.gui.le_mapmgr_scenario_op.text() == "" and
                self.gui.le_mapmgr_scenario_pu.text() == "" and
                self.gui.le_mapmgr_scenario_puins.text() == "" and
                    self.gui.le_mapmgr_scenario_ski.text() == ""):
                self.gui.label_db_console_2.append(
                    "You have to provide at least one map scenario!")
                self.check_val_add_map_error += 161

            if self.map_day_pic:
                res_day_pic_check = bool(re.search(r".jpg", self.map_day_pic))
                res_day_pic_check2 = bool(re.search(r".JPG", self.map_day_pic))
                if res_day_pic_check == False and res_day_pic_check2 == False:
                    self.gui.label_db_console_2.append(
                        "Please provide a JPG file with the ending .jpg as day image!")
                    self.check_val_add_map_error += 254
                day_image = pilimg.open(self.map_day_pic)
                wid, hgt = day_image.size
                day_width = str(wid)
                day_height = str(hgt)
                day_image_size = (day_width[0:2] + "x" + day_height[0:2])
                if day_image_size != "25x15":
                    self.gui.label_db_console_2.append(
                        "The map image does not have the correct size => 25X x 15X pixel!")
                    self.check_val_add_map_error = 531

            if self.map_night_pic:
                res_night_pic_check = bool(
                    re.search(r".jpg", self.map_night_pic))
                res_night_pic_check2 = bool(
                    re.search(r".JPG", self.map_night_pic))
                if res_night_pic_check == False and res_night_pic_check2 == False:
                    self.gui.label_db_console_2.append(
                        "Please provide a JPG file with the ending .jpg as night image!")
                    self.check_val_add_map_error += 201
                night_image = pilimg.open(self.map_night_pic)
                wid, hgt = night_image.size
                night_width = str(wid)
                night_height = str(hgt)
                night_image_size = (night_width[0:2] + "x" + night_height[0:2])
                if night_image_size != "25x15":
                    self.gui.label_db_console_2.append(
                        "The map image does not have the correct size => 25X x 15X pixel!")
                    self.check_val_add_map_error = 571
        # Check if the map name or alias are already in the database

        def check_if_already_existing():
            check_name = self.map_name
            check_alias = self.map_alias
            self.c.execute("select map_name,map_alias from map_config")
            self.conn.commit()
            result_check_name_alias = self.c.fetchall()
            for check_names_and_aliases in result_check_name_alias:
                if check_names_and_aliases[0] == check_name:
                    self.gui.label_db_console_2.append(
                        "Map Alias already exists, please choose another one!")
                    self.check_val_add_map_error += 810
                if check_names_and_aliases[1] == check_alias:
                    self.gui.label_db_console_2.append(
                        "Map Name already exists, please choose another one!")
                    self.check_val_add_map_error += 811
        # Copy the map images to the custom folder, if all checks above completed seccuessfully

        def copy_pics():
            target_image_folder = (
                str(self.dbdir) + '\\img\\custom_map_pics\\')
            self.target_day_image_file = (
                target_image_folder + self.map_alias + ".jpg")
            self.target_night_image_file = (
                target_image_folder + self.map_alias + "_night.jpg")
            if self.map_day_pic and self.target_day_image_file and self.map_day == 1:
                try:
                    copy2(self.map_day_pic, self.target_day_image_file)
                    self.gui.img_view_day_map.setStyleSheet(
                        f"border-image: url({self.map_day_pic});")
                    self.gui.le_mapmgr_selected_day_image.setText(
                        self.map_alias + ".jpg")
                except PermissionError:
                    icondir = Path(__file__).absolute().parent
                    warningmsg = QtWidgets.QMessageBox()
                    warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
                    warningmsg.setWindowTitle("ISRT Map Manager Warning")
                    warningmsg.setWindowIcon(
                        QtGui.QIcon(str(icondir / 'img/isrt.ico')))
                    warningmsg.setText(
                        "Permission Error!\nSomething went wrong while copying the images. Please check the correct\naccess to the source and target directory!")
                    warningmsg.addButton(warningmsg.Ok)
                    self.check_val_add_map_error = 991
                    warningmsg.exec_()
            if self.map_night_pic and self.target_night_image_file and self.map_night == 1:
                try:
                    copy2(self.map_night_pic, self.target_night_image_file)
                    self.gui.img_view_night_map.setStyleSheet(
                        f"border-image: url({self.map_night_pic});")
                    self.gui.le_mapmgr_selected_night_image.setText(
                        self.map_alias + "_night.jpg")
                except PermissionError:
                    icondir = Path(__file__).absolute().parent
                    warningmsg = QtWidgets.QMessageBox()
                    warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
                    warningmsg.setWindowTitle("ISRT Map Manager Warning")
                    warningmsg.setWindowIcon(
                        QtGui.QIcon(str(icondir / 'img/isrt.ico')))
                    warningmsg.setText(
                        "Permission Error!\nSomething went wrong while copying the images. Please check the correct\naccess to the source and target directory!")
                    warningmsg.addButton(warningmsg.Ok)
                    self.check_val_add_map_error = 992
                    warningmsg.exec_()
        # Call the above preliminary functions
        read_new_map_vars()
        check_for_blanks_in_vars()
        check_if_map_info_complete()
        check_if_already_existing()
        # Define what needs to be done to add the map to the database

        def add_new_map_to_database():
            if self.target_day_image_file:
                day_pic_array = self.target_day_image_file.split("\\")
                self.day_pic_name = day_pic_array[-1]
            if self.target_night_image_file:
                night_pic_array = self.target_night_image_file.split("\\")
                self.night_pic = night_pic_array[-1]
                self.night_pic_name = night_pic_array[-1]

            def assign_new_map_variables():
                self.val_map_name = self.map_name
                self.val_map_alias = self.map_alias
                self.val_map_modid = self.map_modid
                self.val_map_day = self.map_day
                self.val_map_night = self.map_night
                self.val_map_pic = self.day_pic_name
                self.val_map_cphc = self.map_scenario_cphc
                self.val_map_cphcins = self.map_scenario_cphcins
                self.val_map_cp = self.map_scenario_cp
                self.val_map_cpins = self.map_scenario_cpins
                self.val_map_dom = self.map_scenario_dom
                self.val_map_ffe = self.map_scenario_ffe
                self.val_map_ffw = self.map_scenario_ffw
                self.val_map_fl = self.map_scenario_fl
                self.val_map_op = self.map_scenario_op
                self.val_map_pu = self.map_scenario_pu
                self.val_map_puins = self.map_scenario_puins
                self.val_map_ski = self.map_scenario_ski
                self.val_map_tdm = self.map_scenario_tdm
                self.val_map_self_added = self.map_self_added

            assign_new_map_variables()

            self.c.execute("INSERT INTO map_config VALUES (:map_name, :map_alias, :modid, :day, :night, :map_pic, :checkpointhardcore, :checkpointhardcore_ins, :checkpoint, :checkpoint_ins, :domination, :firefight_east, :firefight_west, :frontline, :outpost, :push, :push_ins, :skirmish, :teamdeathmatch, :self_added)",
                           {'map_name': self.val_map_name, 'map_alias': self.val_map_alias, 'modid': self.val_map_modid, 'day': self.val_map_day, 'night': self.val_map_night, 'map_pic': self.day_pic_name, 'checkpointhardcore': self.val_map_cphc, 'checkpointhardcore_ins': self.val_map_cphcins, 'checkpoint': self.val_map_cp, 'checkpoint_ins': self.val_map_cpins, 'domination': self.val_map_dom, 'firefight_east': self.val_map_ffe, 'firefight_west': self.val_map_ffw, 'frontline': self.val_map_fl, 'outpost': self.val_map_op, 'push': self.val_map_pu, 'push_ins': self.val_map_puins, 'skirmish': self.val_map_ski, 'teamdeathmatch': self.val_map_tdm, 'self_added': self.val_map_self_added})
            self.conn.commit()

        # Check for any errors in the above methods and if 0 really add map
        if self.check_val_add_map_error == 0:
            self.gui.label_db_console_2.clear()
            copy_pics()
            self.gui.label_db_console_2.append("Images copied!")
            add_new_map_to_database()
            self.gui.dropdown_mapmgr_selector.clear()
            self.fill_map_manager_dropdown()
            self.gui.label_db_console_2.append(
                "Map successfully added to database - DB reloaded!")
            self.gui.le_mapmgr_alias.setEnabled(False)
            self.gui.le_mapmgr_name.setEnabled(False)
            self.gui.le_mapmgr_modid.setEnabled(False)
            self.gui.chkbox_mapmgr_day.setEnabled(False)
            self.gui.chkbox_mapmgr_night.setEnabled(False)
            self.gui.btn_mapmgr_add.setEnabled(False)
            self.gui.btn_mapmgr_select_day_image.setEnabled(False)
            self.gui.btn_mapmgr_select_night_image_2.setEnabled(False)
            self.gui.le_mapmgr_selected_day_image.setEnabled(False)
            self.gui.le_mapmgr_selected_night_image.setEnabled(False)
            self.gui.btn_mapmgr_save.setEnabled(True)
            self.gui.btn_mapmgr_delete.setEnabled(True)
        # If errors throw message and error code
        else:
            icondir = Path(__file__).absolute().parent
            warningmsg = QtWidgets.QMessageBox()
            warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
            warningmsg.setWindowTitle("ISRT Map Manager Warning")
            warningmsg.setWindowIcon(
                QtGui.QIcon(str(icondir / 'img/isrt.ico')))
            warningmsg.setText(
                f"Something went wrong while importing the map.\nPlease check the error message in the console!\n\nError Code: {self.check_val_add_map_error}")
            warningmsg.addButton(warningmsg.Ok)
            warningmsg.exec_()
    # Delete Map from Mapmanager

    def delete_custom_map(self):
        self.gui.label_db_console_2.clear()
        to_be_deleted_map = self.gui.le_mapmgr_name.text()
        self.c.execute("select night from map_config where map_alias=:tbd_map", {
                       'tbd_map': to_be_deleted_map})
        temp_night = self.c.fetchone()
        self.conn.commit()
        is_night_there = temp_night[0]

        daypic = (to_be_deleted_map + ".jpg")

        if is_night_there == 1:
            nightpic = (to_be_deleted_map + "_night.jpg")
        else:
            nightpic = ""

        self.c.execute("select map_alias from map_config")
        map_aliases = self.c.fetchall()
        self.conn.commit()
        self.map_already_there = 0
        for alias_check in map_aliases:
            if to_be_deleted_map == alias_check[0]:
                self.map_already_there = 1

        if to_be_deleted_map and self.map_already_there == 1:
            try:
                self.c.execute("delete from map_config where map_alias=:map_alias_delete", {
                               'map_alias_delete': to_be_deleted_map})
                self.conn.commit()
                self.gui.label_db_console_2.append(
                    f"Map {to_be_deleted_map} deleted from database!")
            except Exception:
                self.gui.label_db_console_2.append(
                    f"There was an error deleting {to_be_deleted_map} from database!")
            if daypic:
                custom_image_folder_delete = (
                    str(self.dbdir) + '\\img\\custom_map_pics\\')
                custom_day_pic_delete = (custom_image_folder_delete + daypic)
                try:
                    os.remove(custom_day_pic_delete)
                    self.gui.label_db_console_2.append(
                        f"Map day image deleted from hard drive!")
                except FileNotFoundError:
                    self.gui.label_db_console_2.append(
                        f"Map image {custom_day_pic_delete} not found - ignoring!")
            if nightpic:
                custom_image_folder_delete = (
                    str(self.dbdir) + '\\img\\custom_map_pics\\')
                custom_night_pic_delete = (
                    custom_image_folder_delete + nightpic)
                try:
                    os.remove(custom_night_pic_delete)
                    self.gui.label_db_console_2.append(
                        f"Map night image deleted from hard drive!")
                except FileNotFoundError:
                    self.gui.label_db_console_2.append(
                        f"Map image {custom_day_pic_delete} not found - ignoring!")

            self.gui.dropdown_mapmgr_selector.clear()
            self.fill_map_manager_dropdown()
            self.clear_map_manager()
        else:
            icondir = Path(__file__).absolute().parent
            warningmsg = QtWidgets.QMessageBox()
            warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
            warningmsg.setWindowTitle("ISRT Map Manager Warning")
            warningmsg.setWindowIcon(
                QtGui.QIcon(str(icondir / 'img/isrt.ico')))
            warningmsg.setText(
                "No map chosen for deletion or map does not exist in DB.\nPlease select a customly added map first!")
            warningmsg.addButton(warningmsg.Ok)
            warningmsg.exec_()
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''
    # Exit App and special Handling Routines
    #
    # Check status of configuration of refresh trigger

    def get_configuration_from_DB_and_set_settings(self):
        self.c.execute('''select btn1_name, btn1_command,
                    btn2_name, btn2_command,
                    btn3_name, btn3_command,
                    btn4_name, btn4_command,
                    btn5_name, btn5_command,
                    btn6_name, btn6_command,
                    btn7_name, btn7_command,
                    btn8_name, btn8_command,
                    btn9_name, btn9_command,
                    btn10_name, btn10_command,
                    btn11_name, btn11_command
                    from configuration''')
        dbbutton_conf = self.c.fetchall()
        self.conn.commit()
        dbbutton_conf_strip = dbbutton_conf[0]
        self.gui.label_button_name_2.setText(dbbutton_conf_strip[2])
        self.gui.label_command_button_2.setText(dbbutton_conf_strip[3])
        self.gui.label_button_name_3.setText(dbbutton_conf_strip[4])
        self.gui.label_command_button_3.setText(dbbutton_conf_strip[5])
        self.gui.label_button_name_5.setText(dbbutton_conf_strip[8])
        self.gui.label_command_button_5.setText(dbbutton_conf_strip[9])
        self.gui.label_button_name_6.setText(dbbutton_conf_strip[10])
        self.gui.label_command_button_6.setText(dbbutton_conf_strip[11])
        self.gui.label_button_name_7.setText(dbbutton_conf_strip[12])
        self.gui.label_command_button_7.setText(dbbutton_conf_strip[13])
        self.gui.label_button_name_8.setText(dbbutton_conf_strip[14])
        self.gui.label_command_button_8.setText(dbbutton_conf_strip[15])
        self.gui.label_button_name_9.setText(dbbutton_conf_strip[16])
        self.gui.label_command_button_9.setText(dbbutton_conf_strip[17])
        self.gui.label_button_name_10.setText(dbbutton_conf_strip[18])
        self.gui.label_command_button_10.setText(dbbutton_conf_strip[19])
        self.c.execute("select quitbox from configuration")
        quitbox_setting = self.c.fetchone()
        self.conn.commit()
        if quitbox_setting[0] == 1:
            self.gui.chkbox_close_question.setChecked(True)
        else:
            self.gui.chkbox_close_question.setChecked(False)
        self.c.execute("select check_updates from configuration")
        update_setting = self.c.fetchone()
        self.conn.commit()
        if update_setting[0] == 1:
            self.gui.chkbox_check_updates.setChecked(True)
        else:
            self.gui.chkbox_check_updates.setChecked(False)
    # Save changed settings

    def save_settings(self):
        # Assign new vairbales for check and update
        new_btn2_name_var = self.gui.label_button_name_2.text()
        new_btn2_command_var = self.gui.label_command_button_2.text()
        new_btn3_name_var = self.gui.label_button_name_3.text()
        new_btn3_command_var = self.gui.label_command_button_3.text()
        new_btn5_name_var = self.gui.label_button_name_5.text()
        new_btn5_command_var = self.gui.label_command_button_5.text()
        new_btn6_name_var = self.gui.label_button_name_6.text()
        new_btn6_command_var = self.gui.label_command_button_6.text()
        new_btn7_name_var = self.gui.label_button_name_7.text()
        new_btn7_command_var = self.gui.label_command_button_7.text()
        new_btn8_name_var = self.gui.label_button_name_8.text()
        new_btn8_command_var = self.gui.label_command_button_8.text()
        new_btn9_name_var = self.gui.label_button_name_9.text()
        new_btn9_command_var = self.gui.label_command_button_9.text()
        new_btn10_name_var = self.gui.label_button_name_10.text()
        new_btn10_command_var = self.gui.label_command_button_10.text()
        #
        # Check new RCON commands for validity
        #

        def assess_command_var(new_button_command):
            self.positive_command_check = 0
            if (new_button_command.startswith("exit") or
                new_button_command.startswith("quit") or
                new_button_command.startswith("listplayers") or
                new_button_command.startswith("help") or
                new_button_command.startswith("kick") or
                new_button_command.startswith("permban") or
                new_button_command.startswith("travel") or
                new_button_command.startswith("ban") or
                new_button_command.startswith("banid") or
                new_button_command.startswith("listbans") or
                new_button_command.startswith("unban") or
                new_button_command.startswith("say") or
                new_button_command.startswith("restartround") or
                new_button_command.startswith("maps") or
                new_button_command.startswith("scenarios") or
                new_button_command.startswith("travelscenario") or
                new_button_command.startswith("gamemodeproperty") or
                    new_button_command.startswith("listgamemodeproperties")):
                self.positive_command_check = 1
            else:
                self.positive_command_check = 0
        # Check and update new Button 2 name
        if new_btn2_name_var and self.button2_name != new_btn2_name_var:
            self.c.execute("UPDATE configuration SET btn2_name=:btn2name", {
                           'btn2name': new_btn2_name_var})
            self.conn.commit()
            self.button2_name = new_btn2_name_var
            self.gui.btn_main_drcon_listbans.setText(new_btn2_name_var)
            self.gui.btn_main_drcon_listbans_definition.setText(
                new_btn2_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 2 command
        if new_btn2_command_var and self.button2_command != new_btn2_command_var:
            new_button_command = new_btn2_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn2_command=:btn2command", {
                               'btn2command': new_btn2_command_var})
                self.conn.commit()
                self.button2_command = new_btn2_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn2_command_var} is no valid RCON command for Button 2! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 3 name
        if new_btn3_name_var and self.button3_name != new_btn3_name_var:
            self.c.execute("UPDATE configuration SET btn3_name=:btn3name", {
                           'btn3name': new_btn3_name_var})
            self.conn.commit()
            self.button3_name = new_btn3_name_var
            self.gui.btn_main_drcon_listmaps.setText(new_btn3_name_var)
            self.gui.btn_main_drcon_listmaps_definition.setText(
                new_btn3_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 3 command
        if new_btn3_command_var and self.button3_command != new_btn3_command_var:
            new_button_command = new_btn3_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn3_command=:btn3command", {
                               'btn3command': new_btn3_command_var})
                self.conn.commit()
                self.button3_command = new_btn3_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn3_command_var} is no valid RCON command for Button 3! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 5 name
        if new_btn5_name_var and self.button5_name != new_btn5_name_var:
            self.c.execute("UPDATE configuration SET btn5_name=:btn5name", {
                           'btn5name': new_btn5_name_var})
            self.conn.commit()
            self.button5_name = new_btn5_name_var
            self.gui.btn_main_drcon_restartround.setText(new_btn5_name_var)
            self.gui.btn_main_drcon_restartround_definition.setText(
                new_btn5_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 5 command
        if new_btn5_command_var and self.button5_command != new_btn5_command_var:
            new_button_command = new_btn5_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn5_command=:btn5command", {
                               'btn5command': new_btn5_command_var})
                self.conn.commit()
                self.button5_command = new_btn5_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn5_command_var} is no valid RCON command for Button 5! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 6 name
        if new_btn6_name_var and self.button6_name != new_btn6_name_var:
            self.c.execute("UPDATE configuration SET btn6_name=:btn6name", {
                           'btn6name': new_btn6_name_var})
            self.conn.commit()
            self.button6_name = new_btn6_name_var
            self.gui.btn_main_drcon_showgamemode.setText(new_btn6_name_var)
            self.gui.btn_main_drcon_showgamemode_definition.setText(
                new_btn6_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 6 command
        if new_btn6_command_var and self.button6_command != new_btn6_command_var:
            new_button_command = new_btn6_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn6_command=:btn6command", {
                               'btn6command': new_btn6_command_var})
                self.conn.commit()
                self.button6_command = new_btn6_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn6_command_var} is no valid RCON command for Button 6! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 7 name
        if new_btn7_name_var and self.button7_name != new_btn7_name_var:
            self.c.execute("UPDATE configuration SET btn7_name=:btn7name", {
                           'btn7name': new_btn7_name_var})
            self.conn.commit()
            self.button7_name = new_btn7_name_var
            self.gui.btn_main_drcon_showaidiff.setText(new_btn7_name_var)
            self.gui.btn_main_drcon_showaidiff_definition.setText(
                new_btn7_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 7 command
        if new_btn7_command_var and self.button7_command != new_btn7_command_var:
            new_button_command = new_btn7_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn7_command=:btn7command", {
                               'btn7command': new_btn7_command_var})
                self.conn.commit()
                self.button7_command = new_btn7_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn7_command_var} is no valid RCON command for Button 7! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 8 name
        if new_btn8_name_var and self.button8_name != new_btn8_name_var:
            self.c.execute("UPDATE configuration SET btn8_name=:btn8name", {
                           'btn8name': new_btn8_name_var})
            self.conn.commit()
            self.button8_name = new_btn8_name_var
            self.gui.btn_main_drcon_showsupply.setText(new_btn8_name_var)
            self.gui.btn_main_drcon_showsupply_definition.setText(
                new_btn8_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 8 command
        if new_btn8_command_var and self.button8_command != new_btn8_command_var:
            new_button_command = new_btn8_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn8_command=:btn8command", {
                               'btn8command': new_btn8_command_var})
                self.conn.commit()
                self.button8_command = new_btn8_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn8_command_var} is no valid RCON command for Button 8! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 9 name
        if new_btn9_name_var and self.button9_name != new_btn9_name_var:
            self.c.execute("UPDATE configuration SET btn9_name=:btn9name", {
                           'btn9name': new_btn9_name_var})
            self.conn.commit()
            self.button9_name = new_btn9_name_var
            self.gui.btn_main_drcon_roundlimit.setText(new_btn9_name_var)
            self.gui.btn_main_drcon_roundlimit_definition.setText(
                new_btn9_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 9 command
        if new_btn9_command_var and self.button9_command != new_btn9_command_var:
            new_button_command = new_btn9_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn9_command=:btn9command", {
                               'btn9command': new_btn9_command_var})
                self.conn.commit()
                self.button9_command = new_btn9_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn9_command_var} is no valid RCON command for Button 9! \n\n Please try again!")
                msg.exec_()
        # Check and update new Button 10 name
        if new_btn10_name_var and self.button10_name != new_btn10_name_var:
            self.c.execute("UPDATE configuration SET btn10_name=:btn10name", {
                           'btn10name': new_btn10_name_var})
            self.conn.commit()
            self.button10_name = new_btn10_name_var
            self.gui.btn_main_drcon_showroundtime.setText(new_btn10_name_var)
            self.gui.btn_main_drcon_showroundtime_definition.setText(
                new_btn10_name_var)
            self.gui.label_saving_indicator.setText("Saved!")
        # Check and update new Button 10 command
        if new_btn10_command_var and self.button10_command != new_btn10_command_var:
            new_button_command = new_btn10_command_var
            assess_command_var(new_button_command)
            if self.positive_command_check == 1:
                self.c.execute("UPDATE configuration SET btn10_command=:btn10command", {
                               'btn10command': new_btn10_command_var})
                self.conn.commit()
                self.button10_command = new_btn10_command_var
                self.gui.label_saving_indicator.setText("Saved!")
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("ISRT Error Message")
                msg.setText(
                    f"Something went wrong: \n\n {new_btn10_command_var} is no valid RCON command for Button 10! \n\n Please try again!")
                msg.exec_()
        # Refresh the Settings in clicking save!
        self.c.execute("select quitbox from configuration")
        self.conn.commit()
        quitbox_result = self.c.fetchone()
        if self.gui.chkbox_close_question.isChecked():
            check_quitapp = 1
        else:
            check_quitapp = 0
        if quitbox_result[0] != check_quitapp:
            if self.gui.chkbox_close_question.isChecked():
                self.c.execute("UPDATE configuration SET quitbox=1")
                self.conn.commit()
            else:
                self.c.execute("UPDATE configuration SET quitbox=0")
                self.conn.commit()
            self.gui.label_saving_indicator.setText("Saved!")
        self.c.execute("select check_updates from configuration")
        self.conn.commit()
        update_result = self.c.fetchone()
        if self.gui.chkbox_check_updates.isChecked():
            check_updateapp = 1
        else:
            check_updateapp = 0
        if update_result[0] != check_updateapp:
            if self.gui.chkbox_check_updates.isChecked():
                self.c.execute("UPDATE configuration SET check_updates=1")
                self.conn.commit()
            else:
                self.c.execute("UPDATE configuration SET check_updates=0")
                self.conn.commit()
            self.gui.label_saving_indicator.setText("Saved!")
        self.get_configuration_from_DB_and_set_settings()
    # Copy2Clipboard

    def copy2clipboard(self):
        copyvar = self.gui.label_output_window.text()
        QtWidgets.QApplication.clipboard().setText(copyvar)
    # Exit using the break command

    def closeEvent(self, event):
        self.c.execute("select quitbox from configuration")
        self.conn.commit()
        quitbox_result = self.c.fetchone()
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
    '''
    ------------------------------------------------------------------
    ------------------------------------------------------------------
    '''


# Main program
#
# Call program class
if __name__ == "__main__":
    # Define path to installation
    installdir = Path(__file__).absolute().parent
    # Database connection setup
    dbfile = (str(installdir / 'db/isrt_data.db'))
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    # Grep or define start variables
    c.execute(
        "select startcounter, version, client_id, show_rn, import, check_updates from configuration")
    check_startvars = c.fetchall()
    startvars = check_startvars[0]
    conn.commit()
    startcounter = startvars[0]
    current_version = str(startvars[1])
    client_id = startvars[2]
    show_rn = startvars[3]
    show_importer = startvars[4]
    check_updates_ok = startvars[5]
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
            client_hash = random.getrandbits(128)
            FORMAT = '%Y%m%d%H%M%S'
            datestamp = datetime.now().strftime(FORMAT)
            client_os = platform.system()
            client_id_new = ("ISRT_" + current_version + "_" +
                             client_os + "_" + datestamp + "_" + str(client_hash))
            c.execute("UPDATE configuration SET client_id=:cid",
                      {'cid': str(client_id_new)})
            conn.commit()
            client_id = client_id_new
            register = f'http://www.isrt.info/version/regtest.php?clientid={client_id}'
            register_post = requests.post(register)
        else:
            # Check if Client ID is already existing
            if client_id == "" or client_id == None:
                client_hash = random.getrandbits(128)
                FORMAT = '%Y%m%d%H%M%S'
                datestamp = datetime.now().strftime(FORMAT)
                client_os = platform.system()
                client_id_new = ("ISRT_" + current_version + "_" +
                                 client_os + "_" + datestamp + "_" + str(client_hash))
                c.execute("update configuration set client_id=:cid",
                          {'cid': str(client_id_new)})
                conn.commit()
                client_id = client_id_new
                register = f'http://www.isrt.info/version/register.php?clientid={client_id}'
                register_post = requests.post(register)
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
        rn_window = QtWidgets.QWidget()
        db_window = QtWidgets.QWidget()
        mgui = maingui()
        mgui.show()
        conn.close()

        # Check for Updates if configuration allows it
        if check_updates_ok == 1:
            r = urllib.request.urlopen(
                "http://www.isrt.info/version/version_check.txt")
            for line in r.readlines():
                line = line.decode("utf-8")
                line = line.strip('\n')
                new_version = line
            if new_version:
                pass
            else:
                new_version = current_version
            # If new version available show Messagebox
            if check_updates_ok == 1 and new_version > current_version:
                def open_website():
                    os.system(
                        f'start %windir%\\explorer.exe "http://www.isrt.info/?page_id=50"')
                icondir = Path(__file__).absolute().parent
                updatemsg = QtWidgets.QMessageBox()
                updatemsg.setIcon(QtWidgets.QMessageBox.Information)
                updatemsg.setWindowTitle("ISRT Update Notification")
                updatemsg.setWindowIcon(QtGui.QIcon(
                    str(icondir / 'img/isrt.ico')))
                updatemsg.setText(
                    f'A new version of ISRT is available\n\nCurrent Version: {current_version}\nLatest Version: {new_version}\n\nClick on Download to get it!')
                download_button = updatemsg.addButton(
                    "Download", updatemsg.ActionRole)
                download_button.clicked.connect(open_website)
                updatemsg.addButton(updatemsg.Ok)
                updatemsg.exec_()

        if running_dev_mode == 1:
            if running_dev_mode_dbi == 1:
                db_gui = dbgui()
                db_gui.show()
            if running_dev_mode_rn == 1:
                rngui = rngui()
                rngui.show()
        else:
            # Check if DB Importer shall be shown or not
            if show_importer == 1:
                db_gui = dbgui()
                db_gui.show()
            # Check if Release Notes shall be shown or not
            if show_rn == 1:
                rngui = rngui()
                rngui.show()

        # Restart on first DB-Import

        def restart_program():
            python = sys.executable
            os.execl(python, python, * sys.argv)
        sys.exit(app.exec_())
    else:
        # Show Error that app is already running
        app = QtWidgets.QApplication(sys.argv)
        msg = QtWidgets.QMessageBox()
        msg.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("ISRT Error Message")
        msg.setText("ISRT is already running - exiting!")
        msg.exec_()
        conn.close()
