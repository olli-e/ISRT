'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
Configuration Settings
------------------------------------------------------------------'''
import re
from PyQt5 import QtGui, QtWidgets

def get_it(self):
    # Define the custom buttons
    self.username_kick_ban = ""
    self.c.execute('''select btn1_name, btn1_command,
                btn2_name, btn2_command,
                btn3_name, btn3_command
                from cust_buttons''')
    dbbutton_conf = self.c.fetchall()
    self.conn.commit()
    dbbutton_conf_strip = dbbutton_conf[0]
    self.gui.label_button_name_1.setText(dbbutton_conf_strip[0])
    self.gui.label_command_button_1.setText(dbbutton_conf_strip[1])
    self.gui.label_button_name_2.setText(dbbutton_conf_strip[2])
    self.gui.label_command_button_2.setText(dbbutton_conf_strip[3])
    self.gui.label_button_name_3.setText(dbbutton_conf_strip[4])
    self.gui.label_command_button_3.setText(dbbutton_conf_strip[5])

    # Get relevant infos from DB for the next settings
    self.c.execute("select quitbox, check_updates, timeout, pref_mode, timer, pref_server, show_gamemode, high_ping, map_group from configuration")
    qb_cu_to_setting = self.c.fetchone()
    self.conn.commit()

    # Define if the Quitbox shoud be shown
    if qb_cu_to_setting[0] == 1:
        self.gui.chkbox_close_question.setChecked(True)
    else:
        self.gui.chkbox_close_question.setChecked(False)

    # Define if the program should check for updates in start
    if qb_cu_to_setting[1] == 1:
        self.gui.chkbox_check_updates.setChecked(True)
    else:
        self.gui.chkbox_check_updates.setChecked(False)

    # Define the Query timeout setting
    if qb_cu_to_setting[2] == 0.6:
        self.timeout = 0.6
        self.gui.dropdown_timeout.setCurrentText("0.6")
    elif qb_cu_to_setting[2] == 1:
        self.timeout = 1
        self.gui.dropdown_timeout.setCurrentText("1")
    elif qb_cu_to_setting[2] == 1.5:
        self.timeout = 1.5
        self.gui.dropdown_timeout.setCurrentText("1.5")
    elif qb_cu_to_setting[2] == 2:
        self.timeout = 2
        self.gui.dropdown_timeout.setCurrentText("2")

    # Get preferred Gamemode
    personal_pref_mode = qb_cu_to_setting[3]
    if personal_pref_mode == "" or personal_pref_mode is None or personal_pref_mode == " ":
        self.gui.dropdown_pref_mode.setCurrentText("Select preferred Gamemode")
        self.gui.dropdown_pref_mode.setCurrentIndex(-1)
    else:
        self.gui.dropdown_pref_mode.setCurrentText(personal_pref_mode)

    # Get favourite Server
    self.c.execute(
        "select alias FROM server")
    alias_list_res = self.c.fetchall()
    self.conn.commit()
    self.gui.dropdown_pref_server.clear()
    self.gui.dropdown_pref_server.addItem("None")

    for uh in alias_list_res:
        self.gui.dropdown_pref_server.addItem(uh[0])
    self.personal_pref_server = qb_cu_to_setting[5]

    if self.personal_pref_server == "" or self.personal_pref_server is None or self.personal_pref_server == " ":
        self.gui.dropdown_pref_server.setCurrentText("Select favourite Server")
        self.gui.dropdown_pref_server.setCurrentIndex(-1)
    else:
        self.gui.dropdown_pref_server.setCurrentText(self.personal_pref_server)

    # Get Monitor Refresh Timer
    self.refreshtimer = qb_cu_to_setting[4]
    self.gui.dropdown_refresh_timer.setCurrentText(str(self.refreshtimer))

    # Get Show Gamemode in Monitor
    self.show_gamemode_indicator = qb_cu_to_setting[6]
    if self.show_gamemode_indicator == 1:
        self.gui.dropdown_show_gamemode.setCurrentText("Yes")
    else:
        self.gui.dropdown_show_gamemode.setCurrentText("No")

    # Get High Ping setting
    self.high_ping = qb_cu_to_setting[7]
    self.gui.dropdown_highping.setCurrentText(str(self.high_ping))

    # Get Map group setting
    self.map_group = qb_cu_to_setting[8]
    self.gui.dropdown_pref_maps.setCurrentText(str(self.map_group))

    # Get Mutator Settings
    self.c.execute(
        "select mutators FROM mutators ORDER by mutators")
    mutators_set = self.c.fetchone()
    self.conn.commit()
    self.gui.textbox_mutators.setText(mutators_set[0])

    self.gui.dropdown_mutator_1_1.clear()
    self.gui.dropdown_mutator_1_2.clear()
    self.gui.dropdown_mutator_1_3.clear()
    self.gui.dropdown_mutator_1_4.clear()
    self.gui.dropdown_mutator_2_1.clear()
    self.gui.dropdown_mutator_2_2.clear()
    self.gui.dropdown_mutator_2_3.clear()
    self.gui.dropdown_mutator_2_4.clear()
    self.gui.dropdown_mutator_3_1.clear()
    self.gui.dropdown_mutator_3_2.clear()
    self.gui.dropdown_mutator_3_3.clear()
    self.gui.dropdown_mutator_3_4.clear()
    self.gui.dropdown_mutator_4_1.clear()
    self.gui.dropdown_mutator_4_2.clear()
    self.gui.dropdown_mutator_4_3.clear()
    self.gui.dropdown_mutator_4_4.clear()

    self.gui.dropdown_mutator_1_1.addItem("None")
    self.gui.dropdown_mutator_1_2.addItem("None")
    self.gui.dropdown_mutator_1_3.addItem("None")
    self.gui.dropdown_mutator_1_4.addItem("None")
    self.gui.dropdown_mutator_2_1.addItem("None")
    self.gui.dropdown_mutator_2_2.addItem("None")
    self.gui.dropdown_mutator_2_3.addItem("None")
    self.gui.dropdown_mutator_2_4.addItem("None")
    self.gui.dropdown_mutator_3_1.addItem("None")
    self.gui.dropdown_mutator_3_2.addItem("None")
    self.gui.dropdown_mutator_3_3.addItem("None")
    self.gui.dropdown_mutator_3_4.addItem("None")
    self.gui.dropdown_mutator_4_1.addItem("None")
    self.gui.dropdown_mutator_4_2.addItem("None")
    self.gui.dropdown_mutator_4_3.addItem("None")
    self.gui.dropdown_mutator_4_4.addItem("None")

    self.mutator_list = mutators_set[0].split(",")
    if self.mutator_list and self.mutator_list[0] != "":
        for muta in self.mutator_list:
            self.gui.dropdown_mutator_1_1.addItem(muta)
            self.gui.dropdown_mutator_1_2.addItem(muta)
            self.gui.dropdown_mutator_1_3.addItem(muta)
            self.gui.dropdown_mutator_1_4.addItem(muta)
            self.gui.dropdown_mutator_2_1.addItem(muta)
            self.gui.dropdown_mutator_2_2.addItem(muta)
            self.gui.dropdown_mutator_2_3.addItem(muta)
            self.gui.dropdown_mutator_2_4.addItem(muta)
            self.gui.dropdown_mutator_3_1.addItem(muta)
            self.gui.dropdown_mutator_3_2.addItem(muta)
            self.gui.dropdown_mutator_3_3.addItem(muta)
            self.gui.dropdown_mutator_3_4.addItem(muta)
            self.gui.dropdown_mutator_4_1.addItem(muta)
            self.gui.dropdown_mutator_4_2.addItem(muta)
            self.gui.dropdown_mutator_4_3.addItem(muta)
            self.gui.dropdown_mutator_4_4.addItem(muta)

    self.c.execute(
        "select p11, p12, p13, p14, p21, p22, p23, p24, p31, p32, p33, p34, p41, p42, p43, p44 FROM mutators")
    mutator_presets = self.c.fetchall()
    self.command_mutators = ""
    mut_pres = mutator_presets[0]
    self.conn.commit()
    self.gui.dropdown_mutator_1_1.setCurrentText(mut_pres[0])
    self.gui.dropdown_mutator_1_2.setCurrentText(mut_pres[1])
    self.gui.dropdown_mutator_1_3.setCurrentText(mut_pres[2])
    self.gui.dropdown_mutator_1_4.setCurrentText(mut_pres[3])
    self.gui.dropdown_mutator_2_1.setCurrentText(mut_pres[4])
    self.gui.dropdown_mutator_2_2.setCurrentText(mut_pres[5])
    self.gui.dropdown_mutator_2_3.setCurrentText(mut_pres[6])
    self.gui.dropdown_mutator_2_4.setCurrentText(mut_pres[7])
    self.gui.dropdown_mutator_3_1.setCurrentText(mut_pres[8])
    self.gui.dropdown_mutator_3_2.setCurrentText(mut_pres[9])
    self.gui.dropdown_mutator_3_3.setCurrentText(mut_pres[10])
    self.gui.dropdown_mutator_3_4.setCurrentText(mut_pres[11])
    self.gui.dropdown_mutator_4_1.setCurrentText(mut_pres[12])
    self.gui.dropdown_mutator_4_2.setCurrentText(mut_pres[13])
    self.gui.dropdown_mutator_4_3.setCurrentText(mut_pres[14])
    self.gui.dropdown_mutator_4_4.setCurrentText(mut_pres[15])

    if mut_pres[0] == "None" and mut_pres[1] == "None" and mut_pres[3] == "None" and mut_pres[3] == "None":
        self.gui.btn_mutator_preset_1.setEnabled(False)
        self.btn_preset1_active = "0"
    else:
        self.gui.btn_mutator_preset_1.setEnabled(True)
        self.btn_preset1_active = "1"
    if mut_pres[4] == "None" and mut_pres[5] == "None" and mut_pres[6] == "None" and mut_pres[7] == "None":
        self.gui.btn_mutator_preset_2.setEnabled(False)
        self.btn_preset2_active = "0"
    else:
        self.gui.btn_mutator_preset_2.setEnabled(True)
        self.btn_preset2_active = "1"
    if mut_pres[8] == "None" and mut_pres[9] == "None" and mut_pres[10] == "None" and mut_pres[11] == "None":
        self.gui.btn_mutator_preset_3.setEnabled(False)
        self.btn_preset3_active = "0"
    else:
        self.gui.btn_mutator_preset_3.setEnabled(True)
        self.btn_preset3_active = "1"
    if mut_pres[12] == "None" and mut_pres[13] == "None" and mut_pres[14] == "None" and mut_pres[15] == "None":
        self.gui.btn_mutator_preset_4.setEnabled(False)
        self.btn_preset4_active = "0"
    else:
        self.gui.btn_mutator_preset_4.setEnabled(True)
        self.btn_preset4_active = "1"


# Save changed settings
def save_it(self):
    # Assign new vairbales for check and update
    new_btn1_name_var = self.gui.label_button_name_1.text()
    new_btn1_command_var = self.gui.label_command_button_1.text()
    new_btn2_name_var = self.gui.label_button_name_2.text()
    new_btn2_command_var = self.gui.label_command_button_2.text()
    new_btn3_name_var = self.gui.label_button_name_3.text()
    new_btn3_command_var = self.gui.label_command_button_3.text()

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

    # Check and update new Button 1 name
    if new_btn1_name_var and self.button1_name != new_btn1_name_var:
        self.c.execute("UPDATE cust_buttons SET btn1_name=:btn1name", {
                    'btn1name': new_btn1_name_var})
        self.conn.commit()
        self.button1_name = new_btn1_name_var
        self.gui.btn_cust_1.setText(new_btn1_name_var)
        self.gui.btn_cust_1_definition.setText(
            new_btn1_name_var)
        self.gui.label_saving_indicator.setText("Saved!")
    # Check and update new Button 1 command
    if new_btn1_command_var and self.button2_command != new_btn1_command_var:
        new_button_command = new_btn1_command_var
        assess_command_var(new_button_command)
        if self.positive_command_check == 1:
            self.c.execute("UPDATE cust_buttons SET btn1_command=:btn1command", {
                        'btn1command': new_btn1_command_var})
            self.conn.commit()
            self.button1_command = new_btn1_command_var
            self.gui.label_saving_indicator.setText("Saved!")
        else:
            msg10 = QtWidgets.QMessageBox()
            msg10.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
            msg10.setIcon(QtWidgets.QMessageBox.Critical)
            msg10.setWindowTitle("ISRT Error Message")
            msg10.setText(
                f"Something went wrong: \n\n {new_btn1_command_var} is no valid RCON command for Button 1! \n\n Please try again!")
            msg10.exec_()

    # Check and update new Button 2 name
    if new_btn2_name_var and self.button3_name != new_btn2_name_var:
        self.c.execute("UPDATE cust_buttons SET btn2_name=:btn2name", {
                    'btn2name': new_btn2_name_var})
        self.conn.commit()
        self.button2_name = new_btn2_name_var
        self.gui.btn_cust_2.setText(new_btn2_name_var)
        self.gui.btn_cust_2_definition.setText(
            new_btn2_name_var)
        self.gui.label_saving_indicator.setText("Saved!")
    # Check and update new Button 2 command
    if new_btn2_command_var and self.button2_command != new_btn2_command_var:
        new_button_command = new_btn2_command_var
        assess_command_var(new_button_command)
        if self.positive_command_check == 1:
            self.c.execute("UPDATE cust_buttons SET btn2_command=:btn2command", {
                        'btn2command': new_btn2_command_var})
            self.conn.commit()
            self.button2_command = new_btn2_command_var
            self.gui.label_saving_indicator.setText("Saved!")
        else:
            msg11 = QtWidgets.QMessageBox()
            msg11.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
            msg11.setIcon(QtWidgets.QMessageBox.Critical)
            msg11.setWindowTitle("ISRT Error Message")
            msg11.setText(
                f"Something went wrong: \n\n {new_btn2_command_var} is no valid RCON command for Button 2! \n\n Please try again!")
            msg11.exec_()

    # Check and update new Button 3 name
    if new_btn3_name_var and self.button3_name != new_btn3_name_var:
        self.c.execute("UPDATE cust_buttons SET btn3_name=:btn3name", {
                    'btn3name': new_btn3_name_var})
        self.conn.commit()
        self.button3_name = new_btn3_name_var
        self.gui.btn_cust_3.setText(new_btn3_name_var)
        self.gui.btn_cust_3_definition.setText(
            new_btn3_name_var)
        self.gui.label_saving_indicator.setText("Saved!")
    # Check and update new Button 3 command
    if new_btn3_command_var and self.button3_command != new_btn3_command_var:
        new_button_command = new_btn3_command_var
        assess_command_var(new_button_command)
        if self.positive_command_check == 1:
            self.c.execute("UPDATE cust_buttons SET btn3_command=:btn3command", {
                        'btn3command': new_btn3_command_var})
            self.conn.commit()
            self.button3_command = new_btn3_command_var
            self.gui.label_saving_indicator.setText("Saved!")
        else:
            msg12 = QtWidgets.QMessageBox()
            msg12.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
            msg12.setIcon(QtWidgets.QMessageBox.Critical)
            msg12.setWindowTitle("ISRT Error Message")
            msg12.setText(
                f"Something went wrong: \n\n {new_btn3_command_var} is no valid RCON command for Button 5! \n\n Please try again!")
            msg12.exec_()


    # Setting for quitbox on or off
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

    # Setting for update check on start
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

    # Timeout changes
    self.c.execute("select timeout from configuration")
    self.conn.commit()
    timeout_result = self.c.fetchone()
    check_timeout = self.gui.dropdown_timeout.currentText()
    if timeout_result[0] != check_timeout:
        self.c.execute("UPDATE configuration SET timeout=:newtimeout", {'newtimeout': check_timeout})
        self.conn.commit()
        self.gui.label_saving_indicator.setText("Saved!")


    # Preferred Gamemode setting
    self.c.execute("select pref_mode from configuration")
    self.conn.commit()
    pref_mode_result = self.c.fetchone()
    current_pref_mode = self.gui.dropdown_pref_mode.currentText()
    if pref_mode_result[0] != current_pref_mode:
        self.c.execute("UPDATE configuration SET pref_mode=:newmode", {'newmode': current_pref_mode})
        self.conn.commit()
        self.gui.label_saving_indicator.setText("Saved!")

    # Preferred Map Group setting
    self.c.execute("select map_group from configuration")
    self.conn.commit()
    map_group_result = self.c.fetchone()
    map_group_result_new = self.gui.dropdown_pref_maps.currentText()
    if map_group_result[0] != map_group_result_new:
        self.c.execute("UPDATE configuration SET map_group=:newmg", {'newmg': map_group_result_new})
        self.conn.commit()
        self.gui.label_saving_indicator.setText("Saved!")

    # Refresh Timer setting
    self.c.execute("select timer from configuration")
    self.conn.commit()
    timer_result = self.c.fetchone()
    current_refresh_timer = self.gui.dropdown_refresh_timer.currentText()
    if timer_result[0] != current_refresh_timer:
        self.c.execute("UPDATE configuration SET timer=:newtimer", {'newtimer': current_refresh_timer})
        self.conn.commit()
        self.gui.label_saving_indicator.setText("Saved!")

    # Update Pref Server List
    new_pref_server = self.gui.dropdown_pref_server.currentText()
    if new_pref_server:
        try:
            self.c.execute(
                "UPDATE configuration SET pref_server=:nprefserver", {'nprefserver': new_pref_server})
            self.conn.commit()
        except Exception:
            self.gui.label_saving_indicator.setText("Error - Preferred Server could not be saved - resetting!")
            self.gui.label_saving_indicator.setStyleSheet("color: red;")

    # Update High ping
    new_high_ping = self.gui.dropdown_highping.currentText()
    if new_high_ping:
        try:
            self.c.execute(
                "UPDATE configuration SET high_ping=:newhigh_ping", {'newhigh_ping': new_high_ping})
            self.conn.commit()
        except Exception:
            self.gui.label_saving_indicator.setText("Error - High Ping could not be saved - resetting!")
            self.gui.label_saving_indicator.setStyleSheet("color: red;")

    # Update Mutators List
    new_mutators = self.gui.textbox_mutators.toPlainText()
    res_check_blanks_mut = bool(re.search(r"\s", new_mutators))
    if res_check_blanks_mut is True:
        self.gui.label_saving_indicator.setText("Error - Mutator List not saved - contians blank spaces - resetting!")
        self.gui.label_saving_indicator.setStyleSheet("color: red;")
    else:

        self.c.execute(
            "UPDATE mutators SET mutators=:mutators", {'mutators': new_mutators})
        self.conn.commit()

        new_11 = self.gui.dropdown_mutator_1_1.currentText()
        new_12 = self.gui.dropdown_mutator_1_2.currentText()
        new_13 = self.gui.dropdown_mutator_1_3.currentText()
        new_14 = self.gui.dropdown_mutator_1_4.currentText()
        new_21 = self.gui.dropdown_mutator_2_1.currentText()
        new_22 = self.gui.dropdown_mutator_2_2.currentText()
        new_23 = self.gui.dropdown_mutator_2_3.currentText()
        new_24 = self.gui.dropdown_mutator_2_4.currentText()
        new_31 = self.gui.dropdown_mutator_3_1.currentText()
        new_32 = self.gui.dropdown_mutator_3_2.currentText()
        new_33 = self.gui.dropdown_mutator_3_3.currentText()
        new_34 = self.gui.dropdown_mutator_3_4.currentText()
        new_41 = self.gui.dropdown_mutator_4_1.currentText()
        new_42 = self.gui.dropdown_mutator_4_2.currentText()
        new_43 = self.gui.dropdown_mutator_4_3.currentText()
        new_44 = self.gui.dropdown_mutator_4_4.currentText()

        self.c.execute(
            "UPDATE mutators SET p11=:np11, p12=:np12, p13=:np13, p14=:np14, p21=:np21, p22=:np22, p23=:np23, p24=:np24, p31=:np31, p32=:np32, p33=:np33, p34=:np34, p41=:np41, p42=:np42, p43=:np43, p44=:np44",
            {'np11': new_11, 'np12': new_12, 'np13': new_13, 'np14': new_14, 'np21': new_21, 'np22': new_22, 'np23': new_23, 'np24': new_24, 'np31': new_31, 'np32': new_32, 'np33': new_33, 'np34': new_34, 'np41': new_41, 'np42': new_42, 'np43': new_43, 'np44': new_44})
        self.conn.commit()
        self.gui.label_saving_indicator.setText("Saved!")
        self.gui.label_saving_indicator.setStyleSheet("color: green;")


    new_show_gamemode = self.gui.dropdown_show_gamemode.currentText()

    if new_show_gamemode == "Yes":
        new_gamemode_int = 1
        self.c.execute(
            "UPDATE configuration SET show_gamemode=:showgamemode", {'showgamemode': new_gamemode_int})
        self.conn.commit()
    else:
        new_gamemode_int = 0
        self.c.execute(
            "UPDATE configuration SET show_gamemode=:showgamemode", {'showgamemode': new_gamemode_int})
        self.conn.commit()

    get_it(self)


# Reload pref_server
def reload_pref_server(self):
    self.c.execute(
        "select alias FROM server")
    alias_list_res = self.c.fetchall()
    self.conn.commit()
    self.c.execute("select pref_server from configuration")
    iqb_cu_to_setting = self.c.fetchone()
    self.conn.commit()
    self.gui.dropdown_pref_server.clear()
    self.gui.dropdown_pref_server.addItem("None")
    for uh in alias_list_res:
        self.gui.dropdown_pref_server.addItem(uh[0])
    self.personal_pref_server = iqb_cu_to_setting[0]
    self.gui.dropdown_pref_server.setCurrentText(self.personal_pref_server)
    