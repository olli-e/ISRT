'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
Server Manager
------------------------------------------------------------------'''
import re
import sqlite3
import time
from shutil import copy2
from datetime import datetime
from PyQt5 import QtGui, QtWidgets
import bin.SourceQuery as sq # pylint: disable=import-error
import modules.query as query # pylint: disable=import-error
import modules.config as conf # pylint: disable=import-error

def fill_server_elements(self):
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

    self.c.execute("select alias FROM server")
    dd_alias = self.c.fetchall()
    self.gui.dropdown_select_server.clear()
    for row in dd_alias:
        self.gui.dropdown_select_server.addItems(row)
    self.conn.commit()
    self.gui.dropdown_select_server.setPlaceholderText("Select Server")
    self.gui.dropdown_select_server.setCurrentIndex(-1)

    if self.personal_pref_server != "None":
        self.c.execute("SELECT ipaddress, queryport, rconport, rconpw FROM server where alias=:pref_alias", {
                                'pref_alias': self.personal_pref_server})
        pref_server_result = self.c.fetchone()
        self.conn.commit()
        if pref_server_result is not None:
            self.gui.dropdown_select_server.setCurrentText(self.personal_pref_server)
            self.gui.entry_ip.setText(pref_server_result[0])
            self.gui.entry_queryport.setText(str(pref_server_result[1]))
            self.gui.entry_rconport.setText(str(pref_server_result[2]))
            self.gui.entry_rconpw.setText(pref_server_result[3])
            query.checkandgoquery(self)

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
    conf.reload_pref_server(self)

# Clear the entire Server Manager GUI
def clear_server_manager(self):
    self.gui.server_alias.clear()
    self.gui.server_ip.clear()
    self.gui.server_query.clear()
    self.gui.server_rconport.clear()
    self.gui.server_rconpw.clear()
    self.gui.btn_server_delete.setEnabled(False)
    self.gui.btn_server_modify.setEnabled(False)

# Assign Server variables for Dropdown menu on selection
def assign_server_values_list(self):
    selection = self.gui.dropdown_select_server.currentText()

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
    query.checkandgoquery(self)

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
        if re.search(self.regexport, val_rconport):
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
    fill_server_elements(self)
    self.gui.btn_server_delete.setEnabled(False)
    self.gui.btn_server_modify.setEnabled(False)

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
        if asd_transferip and re.search(self.asd_regextransip, asd_transferip):
            go_addserver_ipcheck = 1
            if asd_transferqport and re.search(self.asd_regextransport, asd_transferqport):
                go_addserver_qpcheck = 1
                if asd_transferqport and re.search(self.asd_regextransport, asd_transferqport):
                    go_addserver_qpcheck = 1
                    if asd_transferrport:
                        if re.search(self.asd_regextransport, asd_transferrport):
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
            asd_server = sq.SourceQuery(
                asd_transferip, int(asd_transferqport), int(self.timeout))
            asd_serverinfo = asd_server.get_info()
            self.gui.progressbar_map_changer.setProperty("value", 66)
            asd_alias = (asd_serverinfo['Hostname'])
            asd_server.disconnect()
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
                    query.checkandgoquery(self)
                    fill_server_elements(self)
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
                if val_ipaddress and re.search(self.regexip, val_ipaddress):
                    if val_queryport and re.search(self.regexport, val_queryport):
                        if val_rconport:
                            if re.search(self.regexport, val_rconport):
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
        fill_server_elements(self)
    else:
        self.gui.label_db_console.append("Server does not exist in DB - add it or choose a server first!")

# Delete a Server from DB
def server_delete(self):
    self.c.execute("SELECT blocker from configuration")
    blocker_res = self.c.fetchone()
    self.conn.commit()
    runmoncheck = 0

    if blocker_res[0] == 1:
        runmoncheck = 1
    else:
        runmoncheck = 0

    server_delete_id = self.unique_modifier_id

    if server_delete_id and runmoncheck == 0:
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
        fill_server_elements(self)
    elif server_delete_id and runmoncheck == 1:
        self.gui.label_db_console.append("No server delete possible while monitor is querying - wait a second please!")
    else:
        self.gui.label_db_console.append("Please choose a server first!")
    self.gui.server_alias.clear()
    self.gui.server_ip.clear()
    self.gui.server_query.clear()
    self.gui.server_rconport.clear()
    self.gui.server_rconpw.clear()
    self.gui.btn_server_delete.setEnabled(False)
    self.gui.btn_server_modify.setEnabled(False)
    self.gui.tbl_server_manager.selectRow(int(server_delete_id))

# Import Database Routines
def DB_import(self, db_action):
    if db_action == 'select_db':
        db_select_directory = (str(self.dbdir) + '\\db\\')
        self.data_path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select Database', db_select_directory, '*.db',)
        self.gui.label_selected_db.setText(self.data_path[0])
        self.datapath = self.data_path[0]

    elif db_action == 'add_db':
        if self.datapath is not None and self.datapath.endswith(".db"):
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
            fill_server_elements(self)
            self.datapath = None
        else:
            self.gui.label_db_console.setText(
                "Please select a database first!")

    elif db_action == 'replace_db':
        if self.datapath is not None and self.datapath.endswith(".db"):
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
                            fill_server_elements(self)
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
                            fill_server_elements(self)
                            self.datapath = None
                        else:
                            msg8 = QtWidgets.QMessageBox()
                            msg8.setWindowIcon(
                                QtGui.QIcon(".\\img/isrt.ico"))
                            msg8.setIcon(QtWidgets.QMessageBox.Warning)
                            msg8.setWindowTitle("ISRT Error Message")
                            msg8.setText(
                                "The database is from before v0.7, which cannot replace this version's DB.\n\nYou can import the old servers using 'Add'-Function in the Server Manager!")
                            msg8.exec_()
                    else:
                        msg9 = QtWidgets.QMessageBox()
                        msg9.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
                        msg9.setIcon(QtWidgets.QMessageBox.Warning)
                        msg9.setWindowTitle("ISRT Error Message")
                        msg9.setText(
                            "The database is from before v0.7, which cannot replace this version's DB.\n\nYou can import the old servers using 'Add'-Function in the Server Manager!")
                        msg9.exec_()
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
    FORMAT2 = '%Y%m%d%H%M%S'
    db_backup_directory = (str(self.dbdir) + '/db/')
    db_source_filename = (db_backup_directory + 'isrt_data.db')
    db_backup_filename = (db_backup_directory +
                            datetime.now().strftime(FORMAT2) + '_isrt_data.db')
    copy2(str(db_source_filename), str(db_backup_filename))
    dbb_filename = db_backup_filename.replace("\\", "/")
    self.gui.label_db_console.setText(
        "Backup created at: \n" + dbb_filename)

# Delete all servers from DB
def clear_db(self):
    self.c.execute("DELETE from server")
    self.gui.tbl_server_manager.clear()
    self.conn.commit()
    self.gui.server_alias.clear()
    self.gui.server_ip.clear()
    self.gui.server_query.clear()
    self.gui.server_rconport.clear()
    self.gui.server_rconpw.clear()
    self.gui.btn_server_delete.setEnabled(False)
    self.gui.btn_server_modify.setEnabled(False)
    fill_server_elements(self)
    conf.reload_pref_server(self)

# Delete all servers from DB
def dedupe(self):
    self.c.execute("select ipaddress, queryport FROM server")
    list_server_res = self.c.fetchall()
    self.c.execute("SELECT Count(*) FROM server")
    rowcount = self.c.fetchone()
    self.conn.commit()
    singlets = set()
    unique_server_list = set()
    counter = 0
    for server_item in list_server_res:
        if server_item not in singlets:
            singlets.add(server_item)
            counter += 1

    final_rowcount = rowcount[0] - counter

    if final_rowcount != 0:
        for listitem in singlets:
            self.c.execute("select id, alias, ipaddress, queryport, rconport, rconpw FROM server WHERE ipaddress=:doubletteip and queryport=:doubletteqport", {'doubletteip': listitem[0], 'doubletteqport': listitem[1]})
            unique_server_infos = self.c.fetchone()
            self.conn.commit()
            unique_server_list.add(unique_server_infos)

        unique_server_list = list(unique_server_list)
        self.c.execute("delete from server")
        self.conn.commit()
        unique_server_list.sort()
        counter_id = 1
        for enter in unique_server_list:
            self.c.execute("insert into server values (:idn, :aliasn, :ipaddressn, :queryportn, :rconportn, :rconpwn)", {'idn': counter_id, 'aliasn': enter[1], 'ipaddressn': enter[2], 'queryportn': enter[3], 'rconportn': enter[4], 'rconpwn': enter[5]})
            self.conn.commit()
            counter_id += 1
        self.gui.label_db_console.append(
            f"{final_rowcount} duplicates removed!")
    else:
        self.gui.label_db_console.append(
            "Nothing to do!")

    self.gui.server_alias.clear()
    self.gui.server_ip.clear()
    self.gui.server_query.clear()
    self.gui.server_rconport.clear()
    self.gui.server_rconpw.clear()
    self.gui.btn_server_delete.setEnabled(False)
    self.gui.btn_server_modify.setEnabled(False)
    fill_server_elements(self)
    