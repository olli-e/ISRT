'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
Query Manager
------------------------------------------------------------------'''
import socket
import re

from PyQt5 import QtWidgets, QtGui
import bin.SourceQuery as sq # pylint: disable=import-error
import modules.map_manager as maps # pylint: disable=import-error
import modules.query as query # pylint: disable=import-error

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
            query.queryserver(self, self.serverhost, self.queryport)
            if query.queryserver: # pylint: disable=using-constant-test
                query.get_listplayers_fancy(self)
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
                    query.queryserver(self, self.serverhost, self.queryport)
                    if query.queryserver: # pylint: disable=using-constant-test
                        query.get_listplayers_fancy(self)
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
def queryserver(self, serverhost, queryport):  # pylint: disable=unused-argument
    self.serverhost = serverhost
    self.queryport = queryport
    self.gui.label_output_window.clear()
    self.server = sq.SourceQuery(serverhost, int(queryport), float(self.timeout))
    self.serverinfo = self.server.get_info()

    if self.serverinfo is not False:
        self.serverrules = (self.server.get_rules())
        self.ranked = self.serverrules['RankedServer_b']
        self.coop = self.serverrules['Coop_b']
        self.mods = self.serverrules['Mutated_b']
        self.day = self.serverrules['Day_b']

        self.pwcheck = self.serverinfo['Password']
        self.vaccheck = self.serverinfo['Secure']

        if self.mods == "true":
            self.mutatorids = self.serverrules['Mutators_s']
        else:
            self.mutatorids = "None"

        if self.ranked == "true":
            self.serverrankedcheck = "Yes"
        else:
            self.serverrankedcheck = "No"

        if self.coop == "true":
            self.servercoopcheck = "Coop"
        else:
            self.servercoopcheck = "Versus"

        if self.day == "true":
            self.lighting_map = "Day"
        else:
            self.lighting_map = "Night"

        self.gui.le_gamemode.setText(
            str(self.serverrules['GameMode_s']) + " (" + str(self.servercoopcheck) + ")")

        self.gui.le_mods.setText(str(self.mutatorids))

        self.gui.le_mods.setToolTip(str(self.mutatorids))

        self.gui.le_mods.setCursorPosition(1)

        #Creating a list for mutator-IDs to identify installed maps
        if self.mods == "true":
            self.mutator_id_list = (
                self.serverrules['ModList_s'].split(','))
        else:
            self.mutator_id_list = 0

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

        self.gui.le_servername.setText(
            str(self.serverinfo['Hostname']))

        self.gui.le_serverip_port.setText(
            str(serverhost) + ":" + str(self.serverinfo['GamePort']))

        self.gui.le_vac.setText(
            str(self.servervaccheck) + "/" + str(self.serverrankedcheck))

        self.gui.le_players.setText(
            str(self.serverinfo['Players']) + "/" + str(self.serverinfo['MaxPlayers']))

        self.gui.le_ping.setText(str(self.serverinfo['Ping']))

        self.gui.le_map.setText(
            str(self.serverinfo['Map']) + " (" + self.lighting_map + ")")
        self.server.disconnect()
    else:
        self.mutator_id_list = 0



    #
    # Create Map View Picture based on running map
    #

    def assign_map_view_pic(self):
        map_view_pic = str(self.serverinfo['Map'])
        self.c.execute("select map_pic FROM map_config WHERE map_alias=:map_view_result", {
                    'map_view_result': map_view_pic})
        dpmap_alias = self.c.fetchone()


        if dpmap_alias is not None:
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
                        "Unknown map or no Map Image available - referring to placeholder!")
                    self.gui.label_map_view.setStyleSheet(
                        "border-image: url(:map_thumbs/img/maps/thumbs/unknown.jpg); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
            else:
                if dpmap_alias:
                    custom_map_pic_temp = (
                        str(self.dbdir) + '\\img\\custom_map_pics\\' + mapview_pic)
                    custom_map_pic = custom_map_pic_temp.replace("\\", "/")
                    self.gui.label_map_view.setStyleSheet(
                        f"border-image: url({custom_map_pic}); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
                else:
                    self.gui.label_output_window.setText(
                        "Unknown map or no Map Image available - referring to placeholder!")
                    self.gui.label_map_view.setStyleSheet(
                        "border-image: url(:map_thumbs/img/maps/thumbs/unknown.jpg); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
        else:
            self.gui.label_map_view.setStyleSheet(
                "border-image: url(:map_thumbs/img/maps/thumbs/unknown.jpg); background-color: #f0f0f0;background-position: center;background-repeat: no-repeat;")
            self.gui.label_output_window.setText(
                "Unknown map or no Map Image available - referring to placeholder!")
    assign_map_view_pic(self)
    maps.fill_dropdown_map_box_main(self)

# Get fancy returned Playerlist .decode("utf-8"))
def get_listplayers_fancy(self):
    self.serverhost = self.gui.entry_ip.text()
    self.queryport = self.gui.entry_queryport.text()
    self.server_players = sq.SourceQuery(
        self.serverhost, int(self.queryport), float(self.timeout))
    row = 0
    self.gui.tbl_player_output.setRowCount(0)

    if self.server_players.get_players() is not False:
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
