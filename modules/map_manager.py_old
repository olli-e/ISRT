'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
Map Manager
------------------------------------------------------------------'''
import re # pylint: disable=too-many-lines
import os
from pathlib import Path
from shutil import copy2, move
from PyQt5 import QtWidgets, QtGui
from PIL import Image as pilimg
import modules.map_manager as maps # pylint: disable=import-error


# Fill Dropdown Menu for Mapchanging from scratch
def fill_dropdown_map_box_main(self):
    self.c.execute(
        "select map_group FROM configuration")
    mg_select = self.c.fetchone()

    if mg_select[0] == "Standard Maps":
        self.c.execute(
            "select map_alias FROM map_config WHERE modid = '0' ORDER by Map_alias")
        dm_alias = self.c.fetchall()
        self.conn.commit()
        self.gui.dropdown_select_travelscenario.clear()
        self.gui.dropdown_select_gamemode.clear()
        self.gui.dropdown_select_lighting.clear()
        self.gui.dropdown_select_travelscenario.addItem(
                    "---Standard Maps---")
        for rowmaps in dm_alias:
            self.gui.dropdown_select_travelscenario.addItems(rowmaps)
        if self.mutator_id_list == 0:
            pass
        else:
            if self.mutator_id_list[0]:
                custom_maps_list = []
                self.gui.dropdown_select_travelscenario.addItem(
                    "---Custom Maps---")
                for custom_maps in self.mutator_id_list:
                    self.c.execute("select map_alias FROM map_config WHERE modid=:mod_id ORDER by Map_alias", {
                                    'mod_id': custom_maps})
                    dm2_alias = self.c.fetchone()
                    if dm2_alias is not None:
                        custom_maps_list.append(dm2_alias[0])
                    self.conn.commit()
                custom_maps_list.sort()
                for cmlist in custom_maps_list:
                    self.gui.dropdown_select_travelscenario.addItem(cmlist)
    else:
        if self.mutator_id_list == 0:
            pass
        else:
            self.gui.dropdown_select_travelscenario.clear()
            self.gui.dropdown_select_gamemode.clear()
            self.gui.dropdown_select_lighting.clear()
            if self.mutator_id_list[0]:
                custom_maps_list = []
                self.gui.dropdown_select_travelscenario.addItem(
                    "---Custom Maps---")
                for custom_maps in self.mutator_id_list:
                    self.c.execute("select map_alias FROM map_config WHERE modid=:mod_id ORDER by Map_alias", {
                                    'mod_id': custom_maps})
                    dm2_alias = self.c.fetchone()
                    if dm2_alias is not None:
                        custom_maps_list.append(dm2_alias[0])
                    self.conn.commit()
                custom_maps_list.sort()
                for cmlist in custom_maps_list:
                    self.gui.dropdown_select_travelscenario.addItem(cmlist)
            self.c.execute(
            "select map_alias FROM map_config WHERE modid = '0' ORDER by Map_alias")
            dm_alias = self.c.fetchall()
            self.conn.commit()
            self.gui.dropdown_select_travelscenario.addItem(
                        "---Standard Maps---")
            for rowmaps in dm_alias:
                self.gui.dropdown_select_travelscenario.addItems(rowmaps)

# Fill Map Manager Dropdown with DB data
def fill_map_manager_dropdown(self):
    self.gui.dropdown_mapmgr_selector.clear()
    self.gui.btn_mapmgr_delete.setEnabled(False)
    self.gui.btn_mapmgr_save.setEnabled(False)
    self.c.execute("Select map_alias from map_config ORDER by map_alias")
    map_alias_result = self.c.fetchall()
    for map_alias in map_alias_result:
        self.gui.dropdown_mapmgr_selector.addItem(map_alias[0])

# Function to clear the map configuration page
def clear_map_manager(self):
    self.gui.dropdown_mapmgr_selector.clear()
    self.gui.btn_mapmgr_delete.setEnabled(False)
    self.gui.btn_mapmgr_add.setEnabled(True)
    self.gui.btn_mapmgr_save.setEnabled(True)
    maps.fill_map_manager_dropdown(self)
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
    self.c.execute("select * from map_config where map_alias=:selected_map",
                    {'selected_map': self.selected_map_conf})
    self.map_conf_result = self.c.fetchall()
    self.gui.label_db_console_2.append(
        f"Map {self.selected_map_conf} loaded")
    self.map_configuration = self.map_conf_result[0]
    self.map_modid = self.map_configuration[2]
    # Set the configuration in case the called map is a non-Standard map

    def set_map_mgr_conf_non_std():
        self.map_alias = self.map_configuration[0]
        self.map_name = self.map_configuration[1]
        self.map_modid = self.map_configuration[2]
        self.map_day = self.map_configuration[3]
        self.map_night = self.map_configuration[4]
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
        self.gui.le_mapmgr_alias.setText(self.map_alias)
        self.gui.le_mapmgr_name.setText(self.map_name)

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
        self.gui.btn_mapmgr_delete.setEnabled(True)

        if self.map_self_added == 0:
            self.gui.le_mapmgr_selected_day_image.setEnabled(False)
            self.gui.btn_mapmgr_select_day_image.setEnabled(False)
            self.gui.le_mapmgr_selected_night_image.setEnabled(False)
            self.gui.btn_mapmgr_select_night_image_2.setEnabled(False)
            self.gui.le_mapmgr_selected_night_image.setEnabled(False)
            self.gui.le_mapmgr_name.setEnabled(False)
            self.gui.btn_mapmgr_add.setEnabled(False)
            self.gui.btn_delete_day_image.setEnabled(False)
            self.gui.btn_delete_night_image.setEnabled(False)
            self.gui.btn_mapmgr_save.setEnabled(True)
            self.gui.chkbox_mapmgr_day.setEnabled(False)
            self.gui.chkbox_mapmgr_night.setEnabled(False)
            self.gui.le_mapmgr_alias.setEnabled(False)
            self.gui.le_mapmgr_modid.setEnabled(False)

            if self.map_day == 1:
                self.gui.le_mapmgr_selected_day_image.setText(
                    self.map_day_pic_show)
                self.gui.img_view_day_map.setStyleSheet(
                    f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_day_pic_show});")
            else:
                self.gui.img_view_day_map.setStyleSheet(
                    "background-color: rgb(240, 240, 240); border-width: 0px; border-style: solid")
                self.gui.le_mapmgr_selected_day_image.setText("")

            if self.map_night == 1:
                self.gui.img_view_night_map.setStyleSheet(
                    f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_night_pic_show});")
                self.gui.le_mapmgr_selected_night_image.setText(
                    self.map_night_pic_show)
            else:
                self.gui.img_view_night_map.setStyleSheet(
                    "background-color: rgb(240, 240, 240); border-width: 0px; border-style: solid")
                self.gui.le_mapmgr_selected_night_image.setText("")

        else:
            self.gui.le_mapmgr_selected_day_image.setEnabled(True)
            self.gui.btn_mapmgr_select_day_image.setEnabled(True)
            self.gui.le_mapmgr_selected_night_image.setEnabled(True)
            self.gui.btn_mapmgr_select_night_image_2.setEnabled(True)
            self.gui.le_mapmgr_selected_night_image.setEnabled(True)
            self.gui.le_mapmgr_name.setEnabled(True)
            self.gui.btn_mapmgr_add.setEnabled(False)
            self.gui.btn_delete_day_image.setEnabled(True)
            self.gui.btn_delete_night_image.setEnabled(True)
            self.gui.btn_mapmgr_save.setEnabled(True)
            self.gui.chkbox_mapmgr_day.setEnabled(True)
            self.gui.chkbox_mapmgr_night.setEnabled(True)
            self.gui.le_mapmgr_alias.setEnabled(False)
            self.gui.le_mapmgr_modid.setEnabled(True)

            custom_day_pic_temp = (
                str(self.dbdir) + '\\img\\custom_map_pics\\' + self.map_day_pic_show)
            custom_night_pic_temp = (
                str(self.dbdir) + '\\img\\custom_map_pics\\' + self.map_night_pic_show)

            custom_day_pic = custom_day_pic_temp.replace("\\", "/")
            custom_night_pic = custom_night_pic_temp.replace("\\", "/")
            if self.map_day == 1:
                self.gui.le_mapmgr_selected_day_image.setText(
                    custom_day_pic)
                self.gui.img_view_day_map.setStyleSheet(
                    f"border-image: url({custom_day_pic});")
            else:
                self.gui.img_view_day_map.setStyleSheet(
                    "background-color: rgb(240, 240, 240); border-width: 0px; border-style: solid")
                self.gui.le_mapmgr_selected_day_image.setText("")


            if self.map_night == 1:
                self.gui.img_view_night_map.setStyleSheet(
                    f"border-image: url({custom_night_pic});")
                self.gui.le_mapmgr_selected_night_image.setText(
                    custom_night_pic)
            else:
                self.gui.img_view_night_map.setStyleSheet(
                    "background-color: rgb(240, 240, 240); border-width: 0px; border-style: solid")
                self.gui.le_mapmgr_selected_night_image.setText("")

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
        self.map_alias = self.map_configuration[0]
        self.map_name = self.map_configuration[1]
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

        self.gui.le_mapmgr_alias.setText(self.map_alias)
        self.gui.le_mapmgr_name.setText(self.map_name)

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
                "border-image: url(:/map_view/img/maps/map_views.jpg);")
            self.gui.btn_mapmgr_select_day_image.setEnabled(False)
            self.gui.le_mapmgr_selected_day_image.setText("")

        if self.map_night == 1:
            self.gui.img_view_night_map.setStyleSheet(
                f"border-image: url(:/map_thumbs/img/maps/thumbs/{self.map_night_pic});")
            self.gui.le_mapmgr_selected_night_image.setText(
                self.map_night_pic)
        else:
            self.gui.img_view_night_map.setStyleSheet(
                "border-image: url(:/map_view/img/maps/map_views_night.jpg);")
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

# Clear the map image
def clear_map_image(self, scenario):
    if scenario == "day":
        self.gui.le_mapmgr_selected_day_image.clear()
    elif scenario == "night":
        self.gui.le_mapmgr_selected_night_image.clear()

# Save modified map in DB
def save_existing_map(self):
    self.gui.label_db_console_2.clear()
    self.check_val_update_map_error = 0
    self.map_exists = 1

    def get_changed_variables():
        self.val_map_alias = self.gui.le_mapmgr_alias.text()

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

        self.val_map_chg_name = self.gui.le_mapmgr_name.text()
        self.val_map_chg_modid = self.gui.le_mapmgr_modid.text()

        self.map_day_temp = self.gui.chkbox_mapmgr_day.isChecked()
        self.map_night_temp = self.gui.chkbox_mapmgr_night.isChecked()
        self.map_day_pic = self.gui.le_mapmgr_selected_day_image.text()
        self.map_night_pic_temp = self.gui.le_mapmgr_selected_night_image.text()
        self.map_night_pic = self.gui.le_mapmgr_selected_night_image.text()

        if self.map_day_temp is True:
            self.map_day = 1
        else:
            self.map_day = 0
        if self.map_night_temp is True:
            self.map_night = 1
        else:
            self.map_night = 0

        if self.map_day_pic:
            res_check_backslash = bool(re.search(r"\\", self.map_day_pic))
            res_check_slash = bool(re.search(r"/", self.map_day_pic))
            if res_check_backslash is True:
                day_pic_array = self.map_day_pic.split("\\")
                self.day_pic_name = day_pic_array[-1]
            elif res_check_slash is True:
                day_pic_array = self.map_day_pic.split("/")
                self.day_pic_name = day_pic_array[-1]
            else:
                self.day_pic_name = self.map_day_pic

        if self.map_night_pic:
            res_check_backslash = bool(re.search(r"\\", self.map_night_pic))
            res_check_slash = bool(re.search(r"/", self.map_night_pic))
            if res_check_backslash is True:
                night_pic_array = self.map_night_pic.split("\\")
                self.night_pic_name = night_pic_array[-1]
            elif res_check_slash is True:
                night_pic_array = self.map_night_pic.split("/")
                self.night_pic_name = night_pic_array[-1]
            else:
                self.night_pic_name = self.map_night_pic

        if self.gui.le_mapmgr_selected_night_image.text() and self.gui.chkbox_mapmgr_night.isChecked() is False:
            self.gui.label_db_console_2.append(
            "You selected a night picture but no night lighting scenario - ignoring it unless lighting is selected or the selected image was cleared!")
            self.check_val_update_map_error = 1299

        if self.gui.le_mapmgr_selected_day_image.text() and self.gui.chkbox_mapmgr_day.isChecked() is False:
            self.gui.label_db_console_2.append(
            "You selected a day picture but no day lighting scenario - ignoring it unless lighting is selected or the selected image was cleared!")
            self.check_val_update_map_error = 1298


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
        if (self.gui.le_mapmgr_scenario_cp.text() == "" and # pylint: disable=too-many-boolean-expressions
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

    if self.map_exists == 1:
        self.c.execute("select self_added from map_config where map_alias=:map_alias", {'map_alias': self.map_alias})
        map_self_added_temp = self.c.fetchone()
        self.map_self_added = map_self_added_temp[0]
        self.conn.commit()
    else:
        self.map_self_added = 0


    def update_changed_map_vars():
        if self.map_self_added == 1:
            self.day_pic_name = (self.val_map_chg_name + ".jpg")
            self.c.execute("UPDATE map_config SET map_name=:map_name, modid=:modid, day=:day, night=:night, map_pic=:map_pic, checkpointhardcore=:checkpointhardcore, checkpointhardcore_ins=:checkpointhardcore_ins, checkpoint=:checkpoint, checkpoint_ins=:checkpoint_ins, domination=:domination, firefight_east=:firefight_east, firefight_west=:firefight_west, frontline=:frontline, outpost=:outpost, push=:push, push_ins=:push_ins, skirmish=:skirmish, teamdeathmatch=:teamdeathmatch WHERE map_alias=:map_alias",
                            {'map_alias': self.val_map_alias, 'map_name': self.val_map_chg_name, 'modid': self.val_map_chg_modid, 'day': self.map_day, 'night': self.map_night, 'map_pic': self.day_pic_name, 'checkpointhardcore': self.val_map_cphc, 'checkpointhardcore_ins': self.val_map_cphcins, 'checkpoint': self.val_map_cp, 'checkpoint_ins': self.val_map_cpins, 'domination': self.val_map_dom, 'firefight_east': self.val_map_ffe, 'firefight_west': self.val_map_ffw, 'frontline': self.val_map_fl, 'outpost': self.val_map_op, 'push': self.val_map_pu, 'push_ins': self.val_map_puins, 'skirmish': self.val_map_ski, 'teamdeathmatch': self.val_map_tdm})
            self.conn.commit()
        else:
            self.c.execute("UPDATE map_config SET map_name=:map_name, modid=:modid, day=:day, night=:night, checkpointhardcore=:checkpointhardcore, checkpointhardcore_ins=:checkpointhardcore_ins, checkpoint=:checkpoint, checkpoint_ins=:checkpoint_ins, domination=:domination, firefight_east=:firefight_east, firefight_west=:firefight_west, frontline=:frontline, outpost=:outpost, push=:push, push_ins=:push_ins, skirmish=:skirmish, teamdeathmatch=:teamdeathmatch WHERE map_alias=:map_alias",
                            {'map_alias': self.val_map_alias, 'map_name': self.val_map_chg_name, 'modid': self.val_map_chg_modid, 'day': self.map_day, 'night': self.map_night, 'checkpointhardcore': self.val_map_cphc, 'checkpointhardcore_ins': self.val_map_cphcins, 'checkpoint': self.val_map_cp, 'checkpoint_ins': self.val_map_cpins, 'domination': self.val_map_dom, 'firefight_east': self.val_map_ffe, 'firefight_west': self.val_map_ffw, 'frontline': self.val_map_fl, 'outpost': self.val_map_op, 'push': self.val_map_pu, 'push_ins': self.val_map_puins, 'skirmish': self.val_map_ski, 'teamdeathmatch': self.val_map_tdm})
            self.conn.commit()

    # Check for any errors in the above methods and if 0 really add map
    if self.check_val_update_map_error == 0:
        self.gui.label_db_console_2.clear()
        update_changed_map_vars()
        if self.map_self_added == 1:
            copy_pics(self)
        fill_map_manager_conf_tab(self)
        self.gui.label_db_console_2.append(
            "Map successfully updated in database!")
    # If errors throw message and error code
    else:
        icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
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

def copy_pics(self):

    self.map_alias = self.gui.le_mapmgr_alias.text()
    self.map_name = self.gui.le_mapmgr_name.text()

    if self.map_exists == 1:
        self.c.execute("select self_added from map_config where map_alias=:map_alias", {'map_alias': self.map_alias})
        map_self_added_temp = self.c.fetchall()
        map_self_added = map_self_added_temp[0]
        self.conn.commit()
    else:
        map_self_added = 0

    if map_self_added != 1:
        if self.map_day_pic:
            res_check_backslash = bool(re.search(r"\\", self.map_day_pic))
            res_check_slash = bool(re.search(r"/", self.map_day_pic))
            if res_check_backslash is True:
                day_pic_array = self.map_day_pic.split("\\")
                self.day_pic_name = day_pic_array[-1]
            elif res_check_slash is True:
                day_pic_array = self.map_day_pic.split("/")
                self.day_pic_name = day_pic_array[-1]
            else:
                self.day_pic_name = self.map_day_pic

        if self.map_night_pic:
            res_check_backslash = bool(re.search(r"\\", self.map_night_pic))
            res_check_slash = bool(re.search(r"/", self.map_night_pic))
            if res_check_backslash is True:
                night_pic_array = self.map_night_pic.split("\\")
                self.night_pic_name = night_pic_array[-1]
            elif res_check_slash is True:
                night_pic_array = self.map_night_pic.split("/")
                self.night_pic_name = night_pic_array[-1]
            else:
                self.night_pic_name = self.map_night_pic

    target_base_folder = (
        str(self.dbdir) + '\\img\\')
    target_image_folder = (
        str(self.dbdir) + '\\img\\custom_map_pics\\')
    isdirbase = os.path.isdir(target_base_folder)
    isdircp = os.path.isdir(target_image_folder)
    if isdirbase is False:
        try:
            os.mkdir(target_base_folder)
        except PermissionError:
            icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
            warningmsg = QtWidgets.QMessageBox()
            warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
            warningmsg.setWindowTitle("ISRT Map Manager Warning")
            warningmsg.setWindowIcon(
                QtGui.QIcon(str(icondir / 'img/isrt.ico')))
            warningmsg.setText(
                "Permission Error!\nSomething went wrong while copying the images. Please check the correct\naccess to the source and target directory!")
            warningmsg.addButton(warningmsg.Ok)
            warningmsg.exec_()

    if isdircp is False:
        try:
            os.mkdir(target_image_folder)
        except PermissionError:
            icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
            warningmsg = QtWidgets.QMessageBox()
            warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
            warningmsg.setWindowTitle("ISRT Map Manager Warning")
            warningmsg.setWindowIcon(
                QtGui.QIcon(str(icondir / 'img/isrt.ico')))
            warningmsg.setText(
                "Permission Error!\nSomething went wrong while copying the images. Please check the correct\naccess to the source and target directory!")
            warningmsg.addButton(warningmsg.Ok)
            warningmsg.exec_()

    self.target_day_image_file = (
        target_image_folder + self.map_name + ".jpg")
    self.target_night_image_file = (
        target_image_folder + self.map_name + "_night.jpg")

    if map_self_added == 0:


        if self.map_day_pic and self.target_day_image_file and self.map_day == 1:
            try:
                self.map_day_pic = self.map_day_pic.replace("\\", "/")
                self.target_day_image_file = self.target_day_image_file.replace("\\", "/")
                if self.map_day_pic != self.target_day_image_file:
                    copy2(self.map_day_pic, self.target_day_image_file)
                    self.gui.img_view_day_map.setStyleSheet(f"border-image: url({self.target_day_image_file});")
                    self.gui.le_mapmgr_selected_day_image.setText(
                        self.map_name + ".jpg")
            except PermissionError:
                icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
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
                self.map_night_pic = self.map_night_pic.replace("\\", "/")
                self.target_night_image_file = self.target_night_image_file.replace("\\", "/")
                if self.map_night_pic != self.target_night_image_file:
                    copy2(self.map_night_pic, self.target_night_image_file)
                    self.gui.img_view_night_map.setStyleSheet(
                        f"border-image: url({self.target_night_image_file});")
                    self.gui.le_mapmgr_selected_night_image.setText(
                        self.map_name + "_night.jpg")
            except PermissionError:
                icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
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


    else:
        if self.map_day_pic and self.target_day_image_file and self.map_day == 1:
            try:
                self.map_day_pic = self.map_day_pic.replace("\\", "/")
                self.target_day_image_file = self.target_day_image_file.replace("\\", "/")
                if self.map_day_pic != self.target_day_image_file:
                    move(self.map_day_pic, self.target_day_image_file)
                    self.gui.img_view_day_map.setStyleSheet(
                        f"border-image: url({self.target_day_image_file});")
                    self.gui.le_mapmgr_selected_day_image.setText(
                        self.map_name + ".jpg")
            except PermissionError:
                icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
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
                self.map_night_pic = self.map_night_pic.replace("\\", "/")
                self.target_night_image_file = self.target_night_image_file.replace("\\", "/")
                if self.map_night_pic != self.target_night_image_file:
                    move(self.map_night_pic, self.target_night_image_file)
                    self.gui.img_view_night_map.setStyleSheet(
                        f"border-image: url({self.target_night_image_file});")
                    self.gui.le_mapmgr_selected_night_image.setText(
                        self.map_name + "_night.jpg")
            except PermissionError:
                icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
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

# Add new Map to Map database
def add_new_map(self):
    self.gui.label_db_console_2.clear()
    self.check_val_add_map_error = 0
    self.map_exists = 0
    # Read the new Map variables and assign them

    def read_new_map_vars():
        self.map_alias = self.gui.le_mapmgr_alias.text()
        self.map_name = self.gui.le_mapmgr_name.text()
        self.map_modid = self.gui.le_mapmgr_modid.text()

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

        self.map_day_temp = self.gui.chkbox_mapmgr_day.isChecked()
        self.map_night_temp = self.gui.chkbox_mapmgr_night.isChecked()
        self.map_day_pic = self.gui.le_mapmgr_selected_day_image.text()
        self.map_night_pic_temp = self.gui.le_mapmgr_selected_night_image.text()
        self.map_night_pic = self.gui.le_mapmgr_selected_night_image.text()

        if self.map_day_temp is True:
            self.map_day = 1
        else:
            self.map_day = 0
        if self.map_night_temp is True:
            self.map_night = 1
        else:
            self.map_night = 0


    # Check for blanks in the Map Name/Alias and ModID

    def check_for_blanks_in_vars():
        res_check_blanks_name = bool(re.search(r"\s", self.map_name))
        res_check_blanks_id = bool(re.search(r"\s", self.map_modid))
        if res_check_blanks_name is True:
            self.gui.label_db_console_2.append(
                "The map name contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 731
        if res_check_blanks_id is True:
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

        if res_check_blanks_cp is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Checkpoint Security contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 601
        if res_check_blanks_cpins is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Checkpoint Insurgenty contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 602
        if res_check_blanks_cphc is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Checkpoint Hardcore Security contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 604
        if res_check_blanks_cphcins is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Checkpoint Hardcore Insurgents contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 604
        if res_check_blanks_dom is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Domination contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 605
        if res_check_blanks_ffe is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Firefight East contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 606
        if res_check_blanks_ffw is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Firefight West contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 607
        if res_check_blanks_fl is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Frontline contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 608
        if res_check_blanks_op is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Outpost contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 609
        if res_check_blanks_pu is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Push Security contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 610
        if res_check_blanks_puins is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Push Insurgents contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 611
        if res_check_blanks_ski is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Skirmish contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 612
        if res_check_blanks_tdm is True:
            self.gui.label_db_console_2.append(
                "The map scenario for Team Death Match contains a blank space - remove it and try again!")
            self.check_val_add_map_error = 613

    # Check if all required information has been entered
    def check_if_map_info_complete():
        if self.map_alias:
            pass
        else:
            self.gui.label_db_console_2.append(
                "Please enter an alias for the map!")
            self.check_val_add_map_error += 110

        if self.map_name:
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
            if check_numbers.isnumeric() is False:
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
            if res_day_pic_check is False and res_day_pic_check2 is False:
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
            if res_night_pic_check is False and res_night_pic_check2 is False:
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
        check_alias = self.map_alias
        check_name = self.map_name
        self.c.execute("select map_alias,map_name from map_config")
        self.conn.commit()
        result_check_name_alias = self.c.fetchall()
        for check_names_and_aliases in result_check_name_alias:
            if check_names_and_aliases[0] == check_alias:
                self.gui.label_db_console_2.append(
                    "Map Alias already exists, please choose another one!")
                self.check_val_add_map_error += 810
            if check_names_and_aliases[1] == check_name:
                self.gui.label_db_console_2.append(
                    "Map Name already exists, please choose another one!")
                self.check_val_add_map_error += 811

    # Call the above preliminary functions
    read_new_map_vars()
    check_for_blanks_in_vars()
    check_if_map_info_complete()
    check_if_already_existing()
    # Define what needs to be done to add the map to the database

    def add_new_map_to_database():

        def assign_new_map_variables():
            self.val_map_pic = (self.map_name + ".jpg")
            self.val_map_alias = self.map_alias
            self.val_map_name = self.map_name
            self.val_map_modid = self.map_modid
            self.val_map_day = self.map_day
            self.val_map_night = self.map_night
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

        self.c.execute("INSERT INTO map_config VALUES (:map_alias, :map_name, :modid, :day, :night, :map_pic, :checkpointhardcore, :checkpointhardcore_ins, :checkpoint, :checkpoint_ins, :domination, :firefight_east, :firefight_west, :frontline, :outpost, :push, :push_ins, :skirmish, :teamdeathmatch, :self_added)",
                        {'map_alias': self.val_map_alias, 'map_name': self.val_map_name, 'modid': self.val_map_modid, 'day': self.val_map_day, 'night': self.val_map_night, 'map_pic': self.val_map_pic, 'checkpointhardcore': self.val_map_cphc, 'checkpointhardcore_ins': self.val_map_cphcins, 'checkpoint': self.val_map_cp, 'checkpoint_ins': self.val_map_cpins, 'domination': self.val_map_dom, 'firefight_east': self.val_map_ffe, 'firefight_west': self.val_map_ffw, 'frontline': self.val_map_fl, 'outpost': self.val_map_op, 'push': self.val_map_pu, 'push_ins': self.val_map_puins, 'skirmish': self.val_map_ski, 'teamdeathmatch': self.val_map_tdm, 'self_added': self.val_map_self_added})
        self.conn.commit()

    # Check for any errors in the above methods and if 0 really add map
    if self.check_val_add_map_error == 0:
        self.gui.label_db_console_2.clear()
        copy_pics(self)
        self.gui.label_db_console_2.append("Images copied!")
        add_new_map_to_database()
        self.gui.dropdown_mapmgr_selector.clear()
        maps.fill_map_manager_dropdown(self)
        self.gui.label_db_console_2.append(
            "Map successfully added to database - DB reloaded!")
        self.gui.le_mapmgr_alias.setEnabled(False)
        self.gui.le_mapmgr_name.setEnabled(True)
        self.gui.le_mapmgr_modid.setEnabled(True)
        self.gui.chkbox_mapmgr_day.setEnabled(True)
        self.gui.chkbox_mapmgr_night.setEnabled(True)
        self.gui.btn_mapmgr_add.setEnabled(False)
        self.gui.btn_mapmgr_select_day_image.setEnabled(True)
        self.gui.btn_mapmgr_select_night_image_2.setEnabled(True)
        self.gui.le_mapmgr_selected_day_image.setEnabled(True)
        self.gui.le_mapmgr_selected_night_image.setEnabled(True)
        self.gui.btn_mapmgr_save.setEnabled(True)
        self.gui.btn_mapmgr_delete.setEnabled(True)
        clear_map_manager(self)
    # If errors throw message and error code
    else:
        icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
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
    to_be_deleted_map = self.gui.le_mapmgr_alias.text()
    to_be_deleted_map_name = self.gui.le_mapmgr_name.text()
    self.c.execute("select night from map_config where map_alias=:tbd_map", {
                    'tbd_map': to_be_deleted_map})
    temp_night = self.c.fetchone()
    self.conn.commit()
    is_night_there = temp_night[0]

    daypic = (to_be_deleted_map_name + ".jpg")

    if is_night_there == 1:
        nightpic = (to_be_deleted_map_name + "_night.jpg")
    else:
        nightpic = ""

    self.c.execute("select map_alias from map_config")
    map_alias = self.c.fetchall()
    self.conn.commit()
    self.map_already_there = 0
    for alias_check in map_alias:
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
                    "Map day image deleted from hard drive!")
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
                    "Map night image deleted from hard drive!")
            except FileNotFoundError:
                self.gui.label_db_console_2.append(
                    "Map image {custom_day_pic_delete} not found - ignoring!")

        self.gui.dropdown_mapmgr_selector.clear()
        maps.fill_map_manager_dropdown(self)
        maps.clear_map_manager(self)
    else:
        icondir = Path(__file__).absolute().parent # pylint: disable=redefined-outer-name
        warningmsg = QtWidgets.QMessageBox()
        warningmsg.setIcon(QtWidgets.QMessageBox.Critical)
        warningmsg.setWindowTitle("ISRT Map Manager Warning")
        warningmsg.setWindowIcon(
            QtGui.QIcon(str(icondir / 'img/isrt.ico')))
        warningmsg.setText(
            "No map chosen for deletion or map does not exist in DB.\nPlease select a customly added map first!")
        warningmsg.addButton(warningmsg.Ok)
        warningmsg.exec_()
