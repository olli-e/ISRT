'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
Custom Commands and Buttons Settings
------------------------------------------------------------------'''
import time
import threading
from PyQt5 import QtWidgets, QtGui
import modules.rcon as rcon # pylint: disable=import-error
import modules.custom_elements as custom # pylint: disable=import-error

def refill_cust_dropdown_list(self):
    self.c.execute("select distinct commands FROM cust_commands")
    dh_alias = self.c.fetchall()
    self.gui.dropdown_custom_commands.clear()
    for row in dh_alias:
        self.gui.dropdown_custom_commands.addItems(row)
    self.conn.commit()

    self.c.execute("select distinct commands FROM cust_commands")
    dcust_alias = self.c.fetchall()
    self.gui.list_custom_commands_console.clear()
    for row in dcust_alias:
        self.gui.list_custom_commands_console.addItems(row)
    self.conn.commit()

def fill_dropdown_and_list(self):
    self.c.execute("select distinct commands FROM cust_commands")
    dh_alias = self.c.fetchall()
    self.gui.dropdown_custom_commands.clear()
    for row in dh_alias:
        self.gui.dropdown_custom_commands.addItems(row)
    self.conn.commit()

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

    # Get DB variables for custom buttons
    self.c.execute('''select btn1_name, btn1_command,
                        btn2_name, btn2_command,
                        btn3_name, btn3_command
                        from cust_buttons''')
    dbconf_cust = self.c.fetchall()
    self.conn.commit()
    dbconf_cust_strip = dbconf_cust[0]
    # Split Tuple and extract buttons names and commands
    self.button1_name = (dbconf_cust_strip[0])
    self.button1_command = (dbconf_cust_strip[1])
    self.button2_name = (dbconf_cust_strip[2])
    self.button2_command = (dbconf_cust_strip[3])
    self.button3_name = (dbconf_cust_strip[4])
    self.button3_command = (dbconf_cust_strip[5])

    # Assign variables (Button names and commands) to custom Buttons
    self.gui.btn_cust_1.setText(self.button1_name)
    self.gui.btn_cust_1_definition.setText(self.button1_name)
    self.gui.btn_cust_2.setText(self.button2_name)
    self.gui.btn_cust_2_definition.setText(self.button2_name)
    self.gui.btn_cust_3.setText(self.button3_name)
    self.gui.btn_cust_3_definition.setText(
        self.button3_name)

    self.gui.btn_cust_1.clicked.connect(
        lambda: rcon.direct_rcon_command(self, self.button1_command))
    self.gui.btn_cust_2.clicked.connect(
        lambda: rcon.direct_rcon_command(self, self.button2_command))
    self.gui.btn_cust_3.clicked.connect(
        lambda: rcon.direct_rcon_command(self, self.button3_command))

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
            msg2 = QtWidgets.QMessageBox()
            msg2.setWindowIcon(QtGui.QIcon(".\\img/isrt.ico"))
            msg2.setIcon(QtWidgets.QMessageBox.Critical)
            msg2.setWindowTitle("ISRT Error Message")
            msg2.setText(
                f"Something went wrong: \n\n {new__manual_custom_command} is no new valid custom RCON command! \n\n Please try again!")
            msg2.exec_()
    custom.refill_cust_dropdown_list(self)

# Clear all Custom Commands
def custom_command_clear_all(self):
    self.c.execute("DELETE from cust_commands")
    self.gui.list_custom_commands_console.clear()
    self.conn.commit()
    custom.refill_cust_dropdown_list(self)

# Clear selected commands from Custom commands
def custom_command_clear_selected(self):
    delete_commands = self.gui.list_custom_commands_console.selectedItems()
    if delete_commands:
        for row in delete_commands:
            self.c.execute("DELETE FROM cust_commands WHERE commands=:delcommand", {
                            'delcommand': row.text()})
    self.conn.commit()
    custom.refill_cust_dropdown_list(self)
    