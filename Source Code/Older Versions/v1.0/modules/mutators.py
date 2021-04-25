'''
ISRT - Insurgency Sandstorm RCON Tool
In case of questions: support@isrt.info
Website: http://www.isrt.info
This is open Source, you may use, copy, modify it as you wish - feel free!
Module element of ISRT
------------------------------------------------------------------
Mutator Manager
------------------------------------------------------------------'''

def reset_presets(self):
    self.gui.dropdown_mutator_1_1.setCurrentText("None")
    self.gui.dropdown_mutator_1_2.setCurrentText("None")
    self.gui.dropdown_mutator_1_3.setCurrentText("None")
    self.gui.dropdown_mutator_1_4.setCurrentText("None")
    self.gui.dropdown_mutator_2_1.setCurrentText("None")
    self.gui.dropdown_mutator_2_2.setCurrentText("None")
    self.gui.dropdown_mutator_2_3.setCurrentText("None")
    self.gui.dropdown_mutator_2_4.setCurrentText("None")
    self.gui.dropdown_mutator_3_1.setCurrentText("None")
    self.gui.dropdown_mutator_3_2.setCurrentText("None")
    self.gui.dropdown_mutator_3_3.setCurrentText("None")
    self.gui.dropdown_mutator_3_4.setCurrentText("None")
    self.gui.dropdown_mutator_4_1.setCurrentText("None")
    self.gui.dropdown_mutator_4_2.setCurrentText("None")
    self.gui.dropdown_mutator_4_3.setCurrentText("None")
    self.gui.dropdown_mutator_4_4.setCurrentText("None")

def set_presets(self):
    if self.gui.btn_mutator_preset_1.isChecked():
        self.gui.btn_mutator_preset_2.setEnabled(False)
        self.gui.btn_mutator_preset_3.setEnabled(False)
        self.gui.btn_mutator_preset_4.setEnabled(False)



        self.c.execute("select p11, p12, p13, p14 from mutators")
        mutators = []
        mut_add = ""
        self.command_mutators = ""
        mut_preset1_res = self.c.fetchone()
        for muts in mut_preset1_res:
            if muts == "None" or muts == "":
                pass
            else:
                mutators.append(muts)
        length = len(mutators)
        if length == 0:
            mut_add = ""
        elif length == 1:
            mut_add = mutators[0]
        elif length == 2:
            mut_add = (mutators[0] + "," + mutators[1])
        elif length == 3:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2])
        elif length == 4:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2] + "," + mutators[3])

        if mut_add != "":
            self.command_mutators = ("?Mutators=" + mut_add)
        else:
            self.command_mutators = ""

    elif self.gui.btn_mutator_preset_2.isChecked():
        self.gui.btn_mutator_preset_1.setEnabled(False)
        self.gui.btn_mutator_preset_3.setEnabled(False)
        self.gui.btn_mutator_preset_4.setEnabled(False)



        self.c.execute("select p21, p22, p23, p24 from mutators")
        mutators = []
        mut_add = ""
        self.command_mutators = ""
        mut_preset2_res = self.c.fetchone()
        for muts in mut_preset2_res:
            if muts == "None" or muts == "":
                pass
            else:
                mutators.append(muts)
        length = len(mutators)
        if length == 0:
            mut_add = ""
        elif length == 1:
            mut_add = mutators[0]
        elif length == 2:
            mut_add = (mutators[0] + "," + mutators[1])
        elif length == 3:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2])
        elif length == 4:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2] + "," + mutators[3])

        if mut_add != "":
            self.command_mutators = ("?Mutators=" + mut_add)
        else:
            self.command_mutators = ""
    elif self.gui.btn_mutator_preset_3.isChecked():


        self.c.execute("select p31, p32, p33, p34 from mutators")
        mutators = []
        mut_add = ""
        self.command_mutators = ""
        mut_preset3_res = self.c.fetchone()
        for muts in mut_preset3_res:
            if muts == "None" or muts == "":
                pass
            else:
                mutators.append(muts)
        length = len(mutators)
        if length == 0:
            mut_add = ""
        elif length == 1:
            mut_add = mutators[0]
        elif length == 2:
            mut_add = (mutators[0] + "," + mutators[1])
        elif length == 3:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2])
        elif length == 4:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2] + "," + mutators[3])
        if mut_add != "":
            self.command_mutators = ("?Mutators=" + mut_add)
        else:
            self.command_mutators = ""

        self.gui.btn_mutator_preset_1.setEnabled(False)
        self.gui.btn_mutator_preset_2.setEnabled(False)
        self.gui.btn_mutator_preset_4.setEnabled(False)
    elif self.gui.btn_mutator_preset_4.isChecked():
        self.gui.btn_mutator_preset_1.setEnabled(False)
        self.gui.btn_mutator_preset_2.setEnabled(False)
        self.gui.btn_mutator_preset_3.setEnabled(False)


        self.c.execute("select p41, p42, p43, p44 from mutators")
        mutators = []
        mut_add = ""
        self.command_mutators = ""
        mut_preset4_res = self.c.fetchone()
        for muts in mut_preset4_res:
            if muts == "None" or muts == "":
                pass
            else:
                mutators.append(muts)
        length = len(mutators)
        if length == 0:
            mut_add = ""
        elif length == 1:
            mut_add = mutators[0]
        elif length == 2:
            mut_add = (mutators[0] + "," + mutators[1])
        elif length == 3:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2])
        elif length == 4:
            mut_add = (mutators[0] + "," + mutators[1] + "," + mutators[2] + "," + mutators[3])
        if mut_add != "":
            self.command_mutators = ("?Mutators=" + mut_add)
        else:
            self.command_mutators = ""
    else:
        self.gui.btn_mutator_preset_1.setEnabled(True)
        self.gui.btn_mutator_preset_2.setEnabled(True)
        self.gui.btn_mutator_preset_3.setEnabled(True)
        self.gui.btn_mutator_preset_4.setEnabled(True)

def set_disable_all(self):
    if self.gui.chkbx_disable_mutators.isChecked():
        self.gui.btn_mutator_preset_1.setChecked(False)
        self.gui.btn_mutator_preset_2.setChecked(False)
        self.gui.btn_mutator_preset_3.setChecked(False)
        self.gui.btn_mutator_preset_4.setChecked(False)
        self.gui.btn_mutator_preset_1.setEnabled(False)
        self.gui.btn_mutator_preset_2.setEnabled(False)
        self.gui.btn_mutator_preset_3.setEnabled(False)
        self.gui.btn_mutator_preset_4.setEnabled(False)
        self.command_mutators = "?Mutators=?"
    else:
        if self.btn_preset1_active == "1":
            self.gui.btn_mutator_preset_1.setEnabled(True)

        if self.btn_preset2_active == "1":
            self.gui.btn_mutator_preset_2.setEnabled(True)

        if self.btn_preset3_active == "1":
            self.gui.btn_mutator_preset_3.setEnabled(True)

        if self.btn_preset4_active == "1":
            self.gui.btn_mutator_preset_4.setEnabled(True)
        self.command_mutators = ""
