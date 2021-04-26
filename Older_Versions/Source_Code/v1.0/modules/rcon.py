'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
RCON Manager
------------------------------------------------------------------'''
import time
import re
import urllib.request
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QTimer
import modules.rcon as rcon # pylint: disable=import-error
import modules.query as query # pylint: disable=import-error
import modules.custom_elements as custom # pylint: disable=import-error
from bin.rcon.console import Console # pylint: disable=import-error


# Clear the Main Rcon Line Button
def clear_main_rcon(self):
    self.gui.label_output_window.clear()
    self.gui.label_rconcommand.clear()

# Assign custom Commands variables for Dropdown menu
def assign_custom_commands_values_list(self):
    self.assign_custom_commands_values_list_text = self.gui.dropdown_custom_commands.currentText()
    selection = self.assign_custom_commands_values_list_text
    # Handover selected RCON Command
    self.gui.label_rconcommand.setText(selection)

# Map Changer Preparation - Selector
def selected_map_switch(self):
    self.selected_map = self.gui.dropdown_select_travelscenario.currentText()

    if self.selected_map != "---Standard Maps---" and self.selected_map != "---Custom Maps---":

        self.c.execute("select map_name FROM map_config WHERE map_alias=:var_selected_map", {
                        'var_selected_map': self.selected_map})
        dsma_name = self.c.fetchone()
        self.conn.commit()
        var_selected_map = (dsma_name[0])

        self.c.execute("select * from map_config where map_name=:varselmap",
                        {'varselmap': var_selected_map})
        dsmam_name = self.c.fetchall()

        self.conn.commit()
        dsmam_list = (dsmam_name[0])
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

        self.c.execute("select pref_mode from configuration")
        pref_mode_res = self.c.fetchone()
        preferred_mode = pref_mode_res[0]
        self.conn.commit()
        #Preferred gamemode!
        if preferred_mode and preferred_mode != "Select preferred Gamemode":
            self.gui.dropdown_select_gamemode.setCurrentText(preferred_mode)
        else:
            self.gui.dropdown_select_gamemode.setCurrentText("Select Gamemode and Side")
        self.gui.dropdown_select_lighting.setCurrentText("Day")
    else:
        self.gui.label_output_window.setText(
                "That is no map - please choose a correct map from the list!")

# Mapchanger
def map_changer(self):
    # Define required variables
    comm_mod_mutator = ""
    val_map = self.gui.dropdown_select_travelscenario.currentText()
    val_gamemode = self.gui.dropdown_select_gamemode.currentText()
    val_light = self.gui.dropdown_select_lighting.currentText()
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

    if val_map.startswith("Select") or val_map.startswith("--"):
        self.gui.label_output_window.setText(
            "This is not a valid map, please choose one first!")
    elif val_gamemode.startswith("Select"):
        self.gui.label_output_window.setText(
            "This is not a valid gamemode, please choose one first!")
    else:
        self.c.execute("select map_name FROM map_config WHERE map_alias=:sql_map_name", {
                        'sql_map_name': val_map})
        val_map_name = self.c.fetchone()
        val_map_name_result = (str(val_map_name[0]))
        query2 = ("select " + val_gamemode +
                    " FROM map_config WHERE map_name=:sqlmap_name")
        self.c.execute(query2, {'sqlmap_name': val_map_name_result})
        val_travel_name = self.c.fetchone()
        val_travel_name_result = (str(val_travel_name[0]))
        self.conn.commit()

        if val_gamemode == "checkpointhardcore_ins":
            val_gamemode = "checkpointhardcore"


        if self.command_mutators:
            comm_mod_mutator = self.command_mutators
        else:
            comm_mod_mutator = ""


        command = ("travel " + val_map_name_result + "?Scenario=" +
                    val_travel_name_result + "?Lighting=" + val_light + "?game=" + val_gamemode + comm_mod_mutator)


        if command:
            self.gui.label_rconcommand.setText(command)
        else:
            self.gui.label_output_window.setText(
                "Something went wrong with the Travel command, please check above and report it!")

        if self.gui.entry_rconpw.text() and self.gui.entry_rconport.text():

            rcon.checkandgorcon(self)
            waittimer = QTimer()
            waittimer.singleShot(2000, lambda: query.checkandgoquery(self))
            waittimer.start()

            self.gui.btn_mutator_preset_1.setChecked(False)
            self.gui.btn_mutator_preset_2.setChecked(False)
            self.gui.btn_mutator_preset_3.setChecked(False)
            self.gui.btn_mutator_preset_4.setChecked(False)

            if self.btn_preset1_active == "1":
                self.gui.btn_mutator_preset_1.setEnabled(True)

            if self.btn_preset2_active == "1":
                self.gui.btn_mutator_preset_2.setEnabled(True)

            if self.btn_preset3_active == "1":
                self.gui.btn_mutator_preset_3.setEnabled(True)

            if self.btn_preset4_active == "1":
                self.gui.btn_mutator_preset_4.setEnabled(True)

            self.gui.chkbx_disable_mutators.setChecked(False)

            self.gui.progressbar_map_changer.setProperty("value", 0)
        else:
            self.gui.label_output_window.setText("No RCON Password given or no valid RCON command - please retry!")

# Execute Admin Say
def adminsay(self):
    if self.gui.entry_ip.text() and self.gui.entry_rconport.text():
        qid = QtWidgets.QInputDialog.getText(
            self, "Input Dialog", "Enter Admin Message:")
        message = qid[0]
        retval = qid[1]
        if retval is True and message:
            saycommand = (f"say {message}")
            rcon.direct_rcon_command(self, saycommand)
    else:
        self.gui.label_output_window.setText(
            "You have to enter an IP-address and an RCON Port at least!")

# Lookup Steam ID
def lookup_id(self):
    lid = QtWidgets.QInputDialog.getText(
        self, "Input Dialog", 'Enter the Steam64 NetID, you want to lookup:\n(Example from "List Bans": 76561197961263369)')
    lookupid = lid[0]
    lretval = lid[1]
    playername = []
    profileurl = []
    self.gui.progressbar_map_changer.setValue(33)

    lookupid_check_blanks_mut = bool(re.search(r"\s", lookupid))

    if lookupid_check_blanks_mut is True:
        self.gui.label_output_window.setText(
                "Error, Player ID contains blanks, please check and retry!")
    elif lookupid.isnumeric() and len(lookupid) == 17:
        if lretval is True and lookupid:
            url = f"https://www.isrt.info/steamapi/steamid.php?steamid={lookupid}"
            steamid = urllib.request.urlopen(url)
            self.gui.progressbar_map_changer.setValue(66)
            for steamrequest in steamid.readlines():
                steamrequest = steamrequest.decode("utf-8")
                steamrequest = steamrequest.strip('\n')
                if "personaname" in steamrequest:
                    playername_raw = steamrequest.split('": "')
                    playername = playername_raw[1].split('"')
                else:
                    self.gui.label_output_window.setText(
                        "No Player name could be identified!")
                    break
                if "profileurl" in steamrequest:
                    profileurl_raw = steamrequest.split('": "')
                    profileurl = profileurl_raw[1].split('"')
                    break
            self.gui.progressbar_map_changer.setValue(100)

            if lookupid and playername and profileurl:

                self.gui.label_output_window.setText(
                    f"Steam64-ID: {lookupid}")
                self.gui.label_output_window.append(
                    f"Name: {playername[0]}")
                self.gui.label_output_window.append(
                    f"Profile-URL: {profileurl[0]}")
            else:
                self.gui.label_output_window.setText(
                        "No Player and ID name could be identified - check the validity of the Steam ID!")

        else:
            self.gui.label_output_window.setText(
                "No Player NetID given, ignoring!")
    else:
        self.gui.label_output_window.setText(
                "Error, Player ID is not fully numeric or not 17 numbers long - please check and retry!")

    self.gui.progressbar_map_changer.setValue(0)

# Prepare user kick/ban
def prepare_user_kick_ban(self):
    self.selected_user_row = self.gui.tbl_player_output.currentRow()
    self.kick_ban_username_temp = self.gui.tbl_player_output.item(self.selected_user_row, 1)
    self.username_kick_ban = self.kick_ban_username_temp.text()

# Execute Kick
def kick(self):
    if self.gui.entry_ip.text() and self.gui.entry_rconport.text() and self.gui.entry_rconpw.text():
        if self.username_kick_ban != "":
            qid = QtWidgets.QInputDialog.getText(
                self, "Input Dialog", f"Enter optional message to kick player: {self.username_kick_ban} ")
            kickmessage = qid[0]
            retval = qid[1]
            if retval is True and kickmessage:
                saycommand = (f'kick "{self.username_kick_ban}" "{kickmessage}"')
                rcon.direct_rcon_command(self, saycommand)
            self.username_kick_ban = ""
            waittimer = QTimer()
            waittimer.singleShot(1000, lambda: query.checkandgoquery(self))
            waittimer.start()
        else:
            self.gui.label_output_window.setText(
            "No Player to kick selected - choose one from the user list above, first!")
    else:
        self.gui.label_output_window.setText(
            "You have to enter an IP, RCON Port and Password!")

# Execute Ban
def ban(self):
    if self.gui.entry_ip.text() and self.gui.entry_rconport.text() and self.gui.entry_rconpw.text():
        if self.username_kick_ban != "":
            qid = QtWidgets.QInputDialog.getText(
                self, "Input Dialog", f"Enter optional message to ban player: {self.username_kick_ban} ")
            banmessage = qid[0]
            retval = qid[1]

            bantimes = ("5","10","30","60","180","360","720","1800","3600")
            #bid = QtWidgets.QInputDialog.getInt(
            #    self, "Input Dialog", f"Enter the amount of minutes to ban: {self.username_kick_ban} ")
            bid = QtWidgets.QInputDialog.getItem(
                self, "Input Dialog", f"Select the duration of the ban in minutes: {self.username_kick_ban} ", bantimes, 0, False)
            bantime = bid[0]
            bretval = bid[1]

            if retval is True and banmessage and bretval is True and bantime:
                saycommand = (f'ban "{self.username_kick_ban}" "{bantime}" "{banmessage}')
                rcon.direct_rcon_command(self, saycommand)
            self.username_kick_ban = ""
            waittimer = QTimer()
            waittimer.singleShot(1000, lambda: query.checkandgoquery(self))
            waittimer.start()
        else:
            self.gui.label_output_window.setText(
                "No Player to ban selected - choose one from the user list above, first!")
    else:
        self.gui.label_output_window.setText(
            "You have to enter an IP, RCON Port and Password!")

# Execute Perm Ban
def permban(self):
    if self.gui.entry_ip.text() and self.gui.entry_rconport.text() and self.gui.entry_rconpw.text():
        if self.username_kick_ban != "":
            qid = QtWidgets.QInputDialog.getText(
                self, "Input Dialog", f"Enter optional message to permanently ban player: {self.username_kick_ban} ")
            banmessage = qid[0]
            retval = qid[1]

            if retval is True and banmessage:
                saycommand = (f'permban "{self.username_kick_ban}" "{banmessage}"')
                rcon.direct_rcon_command(self, saycommand)
            self.username_kick_ban = ""
            waittimer = QTimer()
            waittimer.singleShot(1000, lambda: query.checkandgoquery(self))
            waittimer.start()
        else:
            self.gui.label_output_window.setText(
            "No Player to ban selected - choose one from the user list above, first!")
    else:
        self.gui.label_output_window.setText(
            "You have to enter an IP, RCON Port and Password!")

# Execute UnBan
def unban(self):
    if self.gui.entry_ip.text() and self.gui.entry_rconport.text() and self.gui.entry_rconpw.text():
        qid = QtWidgets.QInputDialog.getText(
            self, "Input Dialog", "Enter the NetID to unban player:\n(Click on \"List Bans\" to see all banned IDs)")
        unbanid = qid[0]
        retval = qid[1]
        if retval is True and unbanid != "":
            saycommand = (f'unban "{unbanid}"')
            rcon.direct_rcon_command(self, saycommand)
            unbanid = ""
            waittimer = QTimer()
            waittimer.singleShot(1000, lambda: query.checkandgoquery(self))
            waittimer.start()
        else:
            self.gui.label_output_window.setText(
                "No Player NetID given, ignoring!")
    else:
        self.gui.label_output_window.setText(
            "You have to enter an IP, RCON Port and Password!")

# Direct RCON Command handling
def direct_rcon_command(self, command):
    # Check if an rcon command is passed
    if command:
        self.gui.label_rconcommand.setText(command)
        rcon.checkandgorcon(self)
    else:
        self.gui.label_output_window.setText(
            "Something went wrong with the RCON command, please report it!")

# Check and Go RCON
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
        if self.gui.entry_rconpw.text() and (command_check.startswith("gamever") or command_check.startswith("quit") or command_check.startswith("exit") or command_check.startswith("help") or command_check.startswith("listplayers") or command_check.startswith("kick") or command_check.startswith("permban") or command_check.startswith("travel") or command_check.startswith("ban") or command_check.startswith("banid") or command_check.startswith("listbans") or command_check.startswith("unban") or command_check.startswith("say") or command_check.startswith("restartround") or command_check.startswith("maps") or command_check.startswith("scenarios") or command_check.startswith("travelscenario") or command_check.startswith("gamemodeproperty") or command_check.startswith("listgamemodeproperties")):
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
                            custom.refill_cust_dropdown_list(self)
                        try:
                            rcon.rconserver(
                                self, serverhost, rconpassword,  rconport, rconcommand)
                            progress_counter = 0
                            while progress_counter < 101:
                                progress_counter += 10
                                self.gui.progressbar_map_changer.setProperty(
                                "value", progress_counter)
                                time.sleep(0.02)
                            self.gui.progressbar_map_changer.setProperty(
                                "value", 0)
                        except Exception as e:
                            msg7 = QtWidgets.QMessageBox()
                            msg7.setWindowIcon(
                                QtGui.QIcon(".\\img/isrt.ico"))
                            msg7.setIcon(QtWidgets.QMessageBox.Critical)
                            msg7.setWindowTitle("ISRT Error Message")
                            msg7.setText("We encountered and error: \n\n" + str(
                                e) + "\n\nWrong IP, RCON Port, Command or Password?\nThe server may also be down - please check that!")
                            msg7.exec_()
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
            self.gui.label_output_window.setText("No RCON Password given or no valid RCON command - please retry!")
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

# Get PlayerIDs
def get_player_ids(self):
    rawcommand = "listplayers"
    rawconsole = ""
    self.raw_playerid_output = []
    if self.gui.le_players.text().split("/"):
        players = self.gui.le_players.text().split("/")
        players = int(players[0])
    else:
        players = 0
    if self.gui.entry_ip.text() and self.gui.entry_rconpw.text() and self.gui.entry_rconport.text():
        serverhost = str(self.gui.entry_ip.text())
        rconpassword = str(self.gui.entry_rconpw.text())
        rconport = int(self.gui.entry_rconport.text())
        console = Console(
            host=serverhost, password=rconpassword, port=rconport)
        rawconsole = (console.command(rawcommand))
        if rawconsole:
            self.raw_playerid_output = rawconsole.split(' | ')
        console.close()
        if self.raw_playerid_output != [] and players != 0:
            raw_playerid_output_cut = self.raw_playerid_output[5:]
            namecounter = 0
            idcounter = 1
            serverid = 1
            element_count = len(raw_playerid_output_cut)
            cycles = int(element_count / 5)

            for i in range(0,cycles): # pylint: disable=unused-variable
                playername = raw_playerid_output_cut[namecounter]
                playername = playername.strip('\t')
                playerid = raw_playerid_output_cut[idcounter]
                playerid = playerid.strip('\t')
                steam_id_length = len(playerid)
                namecounter += 5
                idcounter += 5
                if steam_id_length == 17 and playerid.isdigit():
                    self.gui.label_output_window.append("ServerID: " + str(serverid) + "   Name: " + playername + "   SteamID: " + playerid)
                    serverid += 1
        else:
            self.gui.label_output_window.append("No Players online")
    else:
        self.gui.label_output_window.append("RCON Port and password required for this function to work!")
