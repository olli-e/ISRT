'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
ISRT Monitor
------------------------------------------------------------------'''
import sys
import sqlite3
from pathlib import Path
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer, Qt
from bin.isrt_monitor_gui import Ui_UI_Server_Monitor
from bin.isrt_monitor_gui2 import Ui_UI_Server_Monitor2
import bin.SourceQuery as sq

class Worker(QObject):
    starter = pyqtSignal()
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    server_queried = pyqtSignal(dict, dict, str, int, int, list)
    def run(self, rowcount, alias_list):
        self.starter.emit()
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
        self.c.execute("UPDATE configuration set blocker=1")
        self.conn.commit()
        counter = 0
        rowcount2 = rowcount
        if rowcount2 <= 0:
            rowcount2 += 1
        progress_multiplier = int(100/rowcount2)
        progress_value = int(progress_multiplier) + int(progress_multiplier)
        while counter <= rowcount:
            server_temp_alias = alias_list[counter]
            self.c.execute("SELECT ipaddress, queryport FROM server where alias=:temp_alias", {'temp_alias': server_temp_alias})
            monmap_ip = self.c.fetchone()
            self.c.execute("SELECT timeout FROM configuration")
            timeout_res = self.c.fetchone()
            self.conn.commit()
            serverhost = monmap_ip[0]
            queryport = monmap_ip[1]
            timeout = timeout_res[0]
            if timeout == 0.6:
                self.timeout = 0.6
            elif timeout == 1:
                self.timeout = 1
            elif timeout == 1.5:
                self.timeout = 1.5
            elif timeout == 2:
                self.timeout = 2
            try:
                server_info = sq.SourceQuery(serverhost, queryport, float(self.timeout))
                server_info.disconnect()
                info = server_info.get_info()
                rules = server_info.get_rules()
                players = server_info.get_players()
                online = 1
                self.progress.emit(progress_value)
                self.server_queried.emit(info, rules, serverhost, counter, online, players)
            except Exception:
                online = 0
                info = {}
                rules = {}
                players = []
                self.server_queried.emit(info, rules, serverhost, counter, online, players)
            counter = counter + 1
            progress_value = progress_value + progress_multiplier
        progress_value = 100
        self.progress.emit(progress_value)
        self.c.execute("UPDATE configuration set blocker=0")
        self.conn.commit()
        self.finished.emit()


class mongui(QtWidgets.QWidget):
    server_query_requested = pyqtSignal(int, list)
    timer_requested = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbdir = Path(__file__).absolute().parent
        self.conn = sqlite3.connect(str(self.dbdir / 'db/isrt_data.db'))
        self.c = self.conn.cursor()
        self.c.execute("select show_gamemode, mon_width, mon_height, high_ping from configuration")
        self.conn.commit()
        self.show_gamemode_temp = self.c.fetchone()
        self.show_gamemode = self.show_gamemode_temp[0]
        if self.show_gamemode == 1:
            self.mogui = Ui_UI_Server_Monitor()
        else:
            self.mogui = Ui_UI_Server_Monitor2()
        self.mogui.setupUi(self)
        self.setGeometry(150, 150, self.show_gamemode_temp[1], self.show_gamemode_temp[2])
        self.high_ping = self.show_gamemode_temp[3]
        self.mogui.mon_progress_bar.setValue(0)
        self.mogui.tbl_server_overview.setRowCount(0)
        if self.show_gamemode == 1:
            self.mogui.tbl_server_overview.setColumnWidth(0, 50)
            self.mogui.tbl_server_overview.setStyleSheet("padding: 3px;")
            self.mogui.tbl_server_overview.setColumnWidth(1, 230)
            self.mogui.tbl_server_overview.setColumnWidth(2, 130)
            self.mogui.tbl_server_overview.setColumnWidth(3, 130)
            self.mogui.tbl_server_overview.setColumnWidth(4, 150)
            self.mogui.tbl_server_overview.setColumnWidth(5, 50)
            self.mogui.tbl_server_overview.setColumnWidth(6, 50)
            self.mogui.tbl_server_overview.setColumnWidth(7, 100)
        else:
            self.mogui.tbl_server_overview.setColumnWidth(0, 50)
            self.mogui.tbl_server_overview.setStyleSheet("padding: 3px;")
            self.mogui.tbl_server_overview.setColumnWidth(1, 230)
            self.mogui.tbl_server_overview.setColumnWidth(2, 130)
            self.mogui.tbl_server_overview.setColumnWidth(3, 150)
            self.mogui.tbl_server_overview.setColumnWidth(4, 50)
            self.mogui.tbl_server_overview.setColumnWidth(5, 50)
            self.mogui.tbl_server_overview.setColumnWidth(6, 100)
        self.c.execute("select progressbar from configuration")
        self.conn.commit()
        self.progressbar_check = self.c.fetchone()
        if self.progressbar_check[0] == 1:
            self.mogui.chkbx_show_progressbar.setChecked(True)
        else:
            self.mogui.chkbx_show_progressbar.setChecked(False)
        self.c.execute("SELECT alias FROM server")
        self.conn.commit()
        for row, form in enumerate(self.c):
            row = row + 1
            self.mogui.tbl_server_overview.insertRow(row)
            for column, item in enumerate(form): # pylint: disable=unused-variable
                self.mogui.tbl_server_overview.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item)))
        self.server_alias_list = self.c.fetchall()
        self.mogui.chkbx_show_progressbar.stateChanged.connect(self.save_checkbox_state)
        self.start_timer()


    def save_checkbox_state(self):
        if self.mogui.chkbx_show_progressbar.isChecked():
            checkstate = 1
        else:
            checkstate = 0

        self.c.execute("select progressbar from configuration")
        self.conn.commit()
        check_progressbar = self.c.fetchone()
        if check_progressbar[0] != checkstate:
            self.c.execute("update configuration set progressbar=:newstate",{'newstate': checkstate})
            self.conn.commit()

    def start_timer(self):
        self.c.execute("select timer from configuration")
        self.conn.commit()
        self.refreshtimer_res = self.c.fetchone()
        self.refreshtimer = self.refreshtimer_res[0] * 1000
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_server_data)
        self.timer.start(self.refreshtimer)
        self.get_server_data()

    def get_server_data(self):

        self.mogui.mon_progress_bar.setValue(0)
        self.c.execute("SELECT alias FROM server")
        self.server_alias_checklist = self.c.fetchall()
        self.conn.commit()
        if self.server_alias_list != self.server_alias_checklist:
            self.mogui.tbl_server_overview.setRowCount(0)
            self.server_alias_list = self.server_alias_checklist
            for row, form in enumerate(self.server_alias_list):
                self.mogui.tbl_server_overview.insertRow(row)
                for column, item in enumerate(form): # pylint: disable=unused-variable
                    self.mogui.tbl_server_overview.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item)))
            self.mogui.mon_progress_bar.setValue(0)
        self.alias_list = []
        for server_alias in self.server_alias_checklist:
            value_temp = server_alias[0]
            self.alias_list.append(value_temp)
        rowcount = (self.mogui.tbl_server_overview.rowCount() - 1)
        self.prepare_list_query(self.alias_list, rowcount)

    def reportProgress(self, n):
        if self.mogui.chkbx_show_progressbar.isChecked():
            self.mogui.mon_progress_bar.setValue(n)
        else:
            self.mogui.mon_progress_bar.setValue(0)

    def prepare_list_query(self, alias_list, rowcount):
        self.alias_list = alias_list
        self.rowcount = rowcount
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.start_querying)
        self.server_query_requested.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.progress.connect(self.reportProgress)
        self.worker.server_queried.connect(self.add_data_to_table)
        self.thread.start()

    def start_querying(self):
        self.server_query_requested.emit(self.rowcount, self.alias_list)

    def add_data_to_table(self, n, m, o, p, q, z):
        self.serverhost = o
        self.counter = p
        self.resrules = m
        self.resinfo = n
        self.online = q
        self.players = z
        if self.online == 1:
            self.mogui.tbl_server_overview.item(self.counter, 1).setBackground(QtGui.QColor(240, 240, 240))
            self.mogui.tbl_server_overview.item(self.counter, 1).setForeground(QtGui.QColor(0, 0, 0))
            lighting_val = self.resrules['Day_b']
            if lighting_val == "true":
                lighting = "Day"
            else:
                lighting = "Night"
            item67 = QtWidgets.QTableWidgetItem("Up")
            item67.setFont(QtGui.QFont("MS Shell Dlg 2"))
            item67.setForeground(QtGui.QColor(0,180,0))
            item67.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.mogui.tbl_server_overview.setItem(self.counter, 0, item67)

            self.mogui.tbl_server_overview.setItem(self.counter, 2, QtWidgets.QTableWidgetItem(self.serverhost +":" + str(self.resinfo['GamePort'])))
            item1 = QtWidgets.QTableWidgetItem(self.resinfo['Map'] + " (" + lighting + ")")
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


            if self.show_gamemode == 1:
                item5 = QtWidgets.QTableWidgetItem(self.resrules['GameMode_s'])
                item5.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.mogui.tbl_server_overview.setItem(self.counter, 3, item5)

                self.mogui.tbl_server_overview.setItem(self.counter, 4, item1)

                if self.resinfo['Players'] == 0:
                    item2 = QtWidgets.QTableWidgetItem("%i/%i" % (self.resinfo['Players'], self.resinfo['MaxPlayers']))
                    item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.mogui.tbl_server_overview.setItem(self.counter, 5, item2)
                else:
                    item2 = QtWidgets.QTableWidgetItem("%i/%i" % (self.resinfo['Players'], self.resinfo['MaxPlayers']))
                    item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    item2.setFont(QtGui.QFont("MS Shell Dlg 2",weight=QtGui.QFont.Bold))
                    self.mogui.tbl_server_overview.setItem(self.counter, 5, item2)

                item4 = QtWidgets.QTableWidgetItem(str(self.resinfo['Ping']) + "ms")
                if self.resinfo['Ping'] >= int(self.high_ping):
                    item4 = QtWidgets.QTableWidgetItem(str(self.resinfo['Ping']) + "ms")
                    item4.setForeground(QtGui.QColor(190,0,0))
                else:
                    item4.setForeground(QtGui.QColor(0,150,0))

                item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.mogui.tbl_server_overview.setItem(self.counter, 6, item4)

                playerlist = ()
                counter = 0
                if len(self.players) != 0:
                    for player in self.players:
                        playername = (("{Name}".format(**player)))
                        if playername != "":
                            playerlist = playerlist + (playername, )
                        if playername == "":
                            counter += 1
                    if counter != 0:
                        playerlist = playerlist + (("+ " + str(counter) + " unknown"), )
                else:
                    playerlist = playerlist + ("No players", )

                result_names = ', '.join([''.join(sub) for sub in playerlist])
                item99 = QtWidgets.QTableWidgetItem(str(result_names))
                self.mogui.tbl_server_overview.setItem(self.counter, 7, item99)
            else:

                self.mogui.tbl_server_overview.setItem(self.counter, 3, item1)

                if self.resinfo['Players'] == 0:
                    item2 = QtWidgets.QTableWidgetItem("%i/%i" % (self.resinfo['Players'], self.resinfo['MaxPlayers']))
                    item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.mogui.tbl_server_overview.setItem(self.counter, 4, item2)
                else:
                    item2 = QtWidgets.QTableWidgetItem("%i/%i" % (self.resinfo['Players'], self.resinfo['MaxPlayers']))
                    item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    item2.setFont(QtGui.QFont("MS Shell Dlg 2",weight=QtGui.QFont.Bold))
                    self.mogui.tbl_server_overview.setItem(self.counter, 4, item2)

                item4 = QtWidgets.QTableWidgetItem(str(self.resinfo['Ping']) + "ms")
                if self.resinfo['Ping'] >= 80:
                    item4 = QtWidgets.QTableWidgetItem(str(self.resinfo['Ping']) + "ms")
                    item4.setForeground(QtGui.QColor(190,0,0))
                else:
                    item4.setForeground(QtGui.QColor(0,150,0))

                item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.mogui.tbl_server_overview.setItem(self.counter, 5, item4)

                playerlist = ()
                counter = 0
                if len(self.players) != 0:
                    for player in self.players:
                        playername = (("{Name}".format(**player)))
                        if playername != "":
                            playerlist = playerlist + (playername, )
                        if playername == "":
                            counter += 1
                    if counter != 0:
                        playerlist = playerlist + (("+ " + str(counter) + " unknown"), )
                else:
                    playerlist = playerlist + ("No players", )

                result_names = ', '.join([''.join(sub) for sub in playerlist])
                item99 = QtWidgets.QTableWidgetItem(str(result_names))
                self.mogui.tbl_server_overview.setItem(self.counter, 6, item99)

        else:
            if self.show_gamemode == 1:
                self.mogui.tbl_server_overview.setItem(self.counter, 2, QtWidgets.QTableWidgetItem(self.serverhost))
                self.mogui.tbl_server_overview.setItem(self.counter, 3, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 4, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 5, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 6, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 7, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.item(self.counter, 1).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 1).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 2).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 2).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 3).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 3).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 4).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 4).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 5).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 5).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 6).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 6).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 7).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 7).setForeground(QtGui.QColor(130,130,130))
            else:
                self.mogui.tbl_server_overview.setItem(self.counter, 2, QtWidgets.QTableWidgetItem(self.serverhost))
                self.mogui.tbl_server_overview.setItem(self.counter, 3, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 4, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 5, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.setItem(self.counter, 6, QtWidgets.QTableWidgetItem(""))
                self.mogui.tbl_server_overview.item(self.counter, 1).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 1).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 2).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 2).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 3).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 3).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 4).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 4).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 5).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 5).setForeground(QtGui.QColor(130,130,130))
                self.mogui.tbl_server_overview.item(self.counter, 6).setBackground(QtGui.QColor(210,210,210))
                self.mogui.tbl_server_overview.item(self.counter, 6).setForeground(QtGui.QColor(130,130,130))

            item66 = QtWidgets.QTableWidgetItem("Down")
            item66.setFont(QtGui.QFont("MS Shell Dlg 2"))
            item66.setForeground(QtGui.QColor(130,130,130))
            item66.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            item66.setBackground(QtGui.QColor(210,210,210))
            self.mogui.tbl_server_overview.setItem(self.counter, 0, item66)

    def closeEvent(self, event): # pylint: disable=unused-argument
        mon_width = self.width()
        mon_height = self.height()
        self.c.execute("UPDATE configuration set blocker=0")
        self.c.execute("update configuration set mon_width=:mon_width, mon_height=:mon_height", {'mon_width': mon_width, 'mon_height': mon_height})
        self.conn.commit()
        self.conn.close()
        self.close()

#Main definitions
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    UI_Server_Monitor = QtWidgets.QWidget()
    UI_Server_Monitor2 = QtWidgets.QWidget()
    ui = Ui_UI_Server_Monitor()
    ui2 = Ui_UI_Server_Monitor2()
    mogui = mongui()
    mogui.show()
    sys.exit(app.exec_())
