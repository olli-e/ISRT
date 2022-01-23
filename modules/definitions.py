'''
ISRT - Insurgency Sandstorm RCON Tool
Website: https://github.com/olli-e/ISRT/releases
This is open Source, you may use, copy, modify it as you wish, but you may not create anything from or with my code,
that will earn you money - no selling of any kind of stuff with my code, not even parts of it!
Module element of ISRT
------------------------------------------------------------------
Definition of GUI and other basic elements
------------------------------------------------------------------'''
import os
import platform
import subprocess
import urllib.request
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from modules import config as conf # pylint: disable=import-error
import modules.definitions as my_def # pylint: disable=import-error
import modules.rcon as rcon # pylint: disable=import-error
import modules.query as query # pylint: disable=import-error
import modules.server_manager as server # pylint: disable=import-error
import modules.map_manager as maps # pylint: disable=import-error
import modules.mutators as mutator # pylint: disable=import-error
import modules.custom_elements as custom # pylint: disable=import-error


# Define buttons and menu items including their functionalities
def action_elements(self):
    self.gui.btn_copy_ip_port.clicked.connect(lambda: copy_ip_port(self))
    self.gui.btn_main_adminsay.clicked.connect(lambda: rcon.adminsay(self))
    self.gui.btn_delete_day_image.clicked.connect(lambda: maps.clear_map_image(self, "day"))
    self.gui.btn_delete_night_image.clicked.connect(lambda: maps.clear_map_image(self, "night"))
    self.gui.btn_kick.clicked.connect(lambda: rcon.kick(self))
    self.gui.btn_ban.clicked.connect(lambda: rcon.ban(self))
    self.gui.btn_perm_ban.clicked.connect(lambda: rcon.permban(self))
    self.gui.btn_unban.clicked.connect(lambda: rcon.unban(self))
    self.gui.btn_get_ids.clicked.connect(lambda: rcon.get_player_ids(self))
    self.gui.btn_main_exec_query.clicked.connect(lambda: query.checkandgoquery(self))
    self.gui.btn_main_clear_rcon.clicked.connect(lambda: rcon.clear_main_rcon(self))
    self.gui.btn_server_clear.clicked.connect(lambda: server.clear_server_manager(self))
    self.gui.btn_server_clear_db.clicked.connect(lambda: server.clear_db(self))
    self.gui.btn_server_delete_doubles.clicked.connect(lambda: server.dedupe(self))
    self.gui.btn_exec_open_bck_dir.clicked.connect(lambda: my_def.open_explorer(self))
    self.gui.btn_main_open_server_monitor.clicked.connect(lambda: my_def.call_monitor(self))
    self.gui.btn_main_exec_rcon.clicked.connect(lambda: rcon.checkandgorcon(self))
    self.gui.btn_cust_delete_selected.clicked.connect(
        lambda: custom.custom_command_clear_selected(self))
    self.gui.btn_cust_delete_all.clicked.connect(
        lambda: custom.custom_command_clear_all(self))
    self.gui.btn_save_settings.clicked.connect(lambda: conf.save_it(self))
    self.gui.btn_mapmgr_add.clicked.connect(lambda: maps.add_new_map(self))
    self.gui.btn_mapmgr_save.clicked.connect(lambda: maps.save_existing_map(self))
    self.gui.btn_mapmgr_select_day_image.clicked.connect(
        lambda: maps.select_map_pic(self, "day"))
    self.gui.btn_mapmgr_select_night_image_2.clicked.connect(
        lambda: maps.select_map_pic(self, "night"))
    self.gui.btn_mapmgr_delete.clicked.connect(lambda: maps.delete_custom_map(self))
    self.gui.btn_main_drcon_changemap.clicked.connect(lambda: rcon.map_changer(self))
    self.gui.btn_add_cust_command.clicked.connect(
        lambda: custom.add_custom_command_manually(self))
    self.gui.btn_exec_db_backup.clicked.connect(lambda: server.create_db_backup(self))
    self.gui.btn_main_add_server_db.clicked.connect(
        lambda: server.add_server_directly(self))
    self.gui.btn_mapmgr_clear.clicked.connect(lambda: maps.clear_map_manager(self))
    self.gui.btn_server_add.clicked.connect(lambda: server.server_add(self))
    self.gui.btn_server_modify.clicked.connect(lambda: server.server_modify(self))
    self.gui.btn_server_delete.clicked.connect(lambda: server.server_delete(self))
    self.gui.btn_delete_presets_1.clicked.connect(lambda: mutator.reset_preset1(self))
    self.gui.btn_delete_presets_2.clicked.connect(lambda: mutator.reset_preset2(self))
    self.gui.btn_delete_presets_3.clicked.connect(lambda: mutator.reset_preset3(self))
    self.gui.btn_delete_presets_4.clicked.connect(lambda: mutator.reset_preset4(self))
    self.gui.textbox_add_mutators.returnPressed.connect(lambda: conf.save_it(self))
    self.gui.btn_mutator_preset_1.clicked.connect(lambda: mutator.set_presets(self))
    self.gui.btn_mutator_preset_2.clicked.connect(lambda: mutator.set_presets(self))
    self.gui.btn_mutator_preset_3.clicked.connect(lambda: mutator.set_presets(self))
    self.gui.btn_mutator_preset_4.clicked.connect(lambda: mutator.set_presets(self))
    self.gui.btn_main_make_default.clicked.connect(lambda: make_default_server(self))
    self.gui.chkbx_disable_mutators.stateChanged.connect(lambda: mutator.set_disable_all(self))
    # DB Import Buttons and fields
    self.gui.btn_select_database.clicked.connect(
        lambda: server.DB_import(self, "select_db"))
    self.gui.btn_add_database.clicked.connect(
        lambda: server.DB_import(self, "add_db"))
    self.gui.btn_replace_database.clicked.connect(
        lambda: server.DB_import(self, "replace_db"))
    # Set dropdown actions
    self.gui.dropdown_select_server.activated[str].connect( # pylint: disable=unsubscriptable-object
        lambda: server.assign_server_values_list(self))
    self.gui.dropdown_custom_commands.activated[str].connect( # pylint: disable=unsubscriptable-object
        lambda: rcon.assign_custom_commands_values_list(self))
    # Map and option assignment
    self.gui.dropdown_select_travelscenario.activated[str].connect( # pylint: disable=unsubscriptable-object
        lambda: rcon.selected_map_switch(self))
    self.gui.dropdown_mapmgr_selector.activated[str].connect( # pylint: disable=unsubscriptable-object
        lambda: maps.fill_map_manager_conf_tab(self))
    # Return pressed actions
    self.gui.entry_ip.returnPressed.connect(lambda: query.checkandgoquery(self))
    self.gui.LE_add_custom_command.returnPressed.connect(
        lambda: custom.add_custom_command_manually(self))
    self.gui.entry_queryport.returnPressed.connect(lambda: query.checkandgoquery(self))
    self.gui.entry_rconport.returnPressed.connect(lambda: query.checkandgoquery(self))
    self.gui.entry_rconpw.returnPressed.connect(lambda: query.checkandgoquery(self))
    self.gui.label_button_name_1.returnPressed.connect(lambda: conf.save_it(self))
    self.gui.label_button_name_2.returnPressed.connect(lambda: conf.save_it(self))
    self.gui.label_button_name_3.returnPressed.connect(lambda: conf.save_it(self))
    self.gui.label_command_button_1.returnPressed.connect(
        lambda: conf.save_it(self))
    self.gui.label_command_button_2.returnPressed.connect(
        lambda: conf.save_it(self))
    self.gui.label_command_button_3.returnPressed.connect(
        lambda: conf.save_it(self))
    self.gui.label_rconcommand.returnPressed.connect(lambda: rcon.checkandgorcon(self))
    self.gui.server_alias.returnPressed.connect(lambda: server.server_modify(self))
    self.gui.server_ip.returnPressed.connect(lambda: server.server_modify(self))
    self.gui.server_query.returnPressed.connect(lambda: server.server_modify(self))
    self.gui.server_rconport.returnPressed.connect(lambda: server.server_modify(self))
    self.gui.server_rconpw.returnPressed.connect(lambda: server.server_modify(self))
    self.gui.tbl_player_output.clicked.connect(lambda: rcon.prepare_user_kick_ban(self))

# Set the Client ID
def clientid(self):
    self.c.execute("select client_id from configuration")
    client = self.c.fetchone()
    self.conn.commit()
    self.client_id = client[0]
    if self.client_id:
        self.gui.lbl_client_id.setText(f"Client-ID: {self.client_id}")
    else:
        self.gui.lbl_client_id.setText(
            "No Client ID defined yet - will be displayed automatically on next restart")

# Define static variables
def pre_vars(self):
    self.gui.label_saving_indicator.clear()
    self.unique_modifier_id = ""
    self.gui.btn_server_delete.setEnabled(False)
    self.gui.btn_server_modify.setEnabled(False)

# Setup Version number and set in Main Title
def set_version(self):
    self.c.execute("Select version, check_updates from configuration")
    version_temp = self.c.fetchone()
    self.conn.commit()
    version = ("v" + version_temp[0])
    current_version = version_temp[0]
    check_updates_ok = version_temp[1]

    # Check for Updates if configuration allows it
    if check_updates_ok == 1:

        try:
            r = urllib.request.urlopen(
            "https://raw.githubusercontent.com/olli-e/ISRT/v1.5_Final/update_indicator/version.txt")
        except Exception:
            r = None
            new_version = current_version

        if r:
            for line in r.readlines():
                line = line.decode("utf-8")
                line = line.strip('\n')
                new_version = line

        if new_version:
            pass
        else:
            new_version = current_version

        # If new version available show it
        def open_website():
            os.system(
                'start %windir%\\explorer.exe "https://github.com/olli-e/ISRT/releases"')

        if check_updates_ok == 1 and new_version > current_version:

            self.setWindowTitle(QtCore.QCoreApplication.translate("ISRT_Main_Window", f"ISRT - Insurgency Sandstorm RCON Tool {version}  (Update available)"))
            self.gui.lbl_update_info.setHidden(False)
        else:
            self.setWindowTitle(QtCore.QCoreApplication.translate("ISRT_Main_Window", f"ISRT - Insurgency Sandstorm RCON Tool {version}"))
            self.gui.lbl_update_info.setHidden(True)
    else:
            self.setWindowTitle(QtCore.QCoreApplication.translate("ISRT_Main_Window", f"ISRT - Insurgency Sandstorm RCON Tool {version}"))
            self.gui.lbl_update_info.setHidden(True)


    

# Open Explorer Backup Window
def open_explorer(self):
    fulldir = (str(self.dbdir / 'db/'))
    os.system(f'start %windir%\\explorer.exe "{fulldir}"')

# Setup ISRT Monitor Call
def call_monitor(self):
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

# Copy IP/Port to clipboard
def copy_ip_port(self):
    def clear_it_up():
        self.gui.label_output_window.clear()
    if self.gui.le_serverip_port.text() == "":
        self.gui.label_output_window.setText("Nothing to copy, select a server first!")
        wait_timer = QTimer()
        wait_timer.singleShot(2000, clear_it_up)
        wait_timer.start()
    else:
        QtWidgets.QApplication.clipboard().setText(self.gui.le_serverip_port.text())
        self.gui.label_output_window.setText("Copied Server-IP and Port to clipboard")
        wait_timer = QTimer()
        wait_timer.singleShot(2000, clear_it_up)
        wait_timer.start()

# Clear the Mutators list
def clear_default_mutators(self):
    self.gui.textbox_mutators.clear()
    mutator.reset_presets(self)
    conf.save_it(self)
    conf.get_it(self)

# Reget the mutators list from the DB
def reload_default_mutators(self):
    self.gui.textbox_mutators.clear()
    self.c.execute("select default_mutators from mutators")
    mutators_default_res = self.c.fetchall()
    mutators_default = mutators_default_res[0]
    self.gui.textbox_mutators.setText(mutators_default[0])
    self.conn.commit()
    conf.save_it(self)
    conf.get_it(self)

# Make the chosen server the default server
def make_default_server(self):

    new_pref_server_ip = self.gui.entry_ip.text()

    if self.gui.dropdown_select_server.currentText() == "Select Server" or self.gui.entry_ip.text() == "" or self.gui.entry_queryport.text() == "":

        self.gui.label_output_window.setText("Error - Please select a server or save the server to database first!")
    else:
        self.c.execute("select alias from server where ipaddress=:newprefip", {'newprefip': new_pref_server_ip})
        self.conn.commit()
        newpref_result = self.c.fetchone()
        if newpref_result is not None:
            try:
                self.c.execute("UPDATE configuration SET pref_server=:nprefserver", {'nprefserver': newpref_result[0]})
                self.conn.commit()
                self.gui.dropdown_pref_server.setCurrentText(newpref_result[0])
                self.gui.label_output_window.setText("Server successfully marked as Preferred Server!")
            except Exception:
                self.gui.label_output_window.setText("Error - Preferred Server could not be saved - resetting!")
        else:
            self.gui.label_output_window.setText("Error - Server is not in Database - please save it first!")  
        conf.save_it(self)

