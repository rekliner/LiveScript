from Tkinter import *
from tkFileDialog import * 
import os
import json
from tkFont import Font

class ck_control_panel():
    def __init__(self, parent):
        self.parent = parent
        self.is_open = False
        self.temp_setlist = []
        self.programs = []
        for i in range(17):
            self.programs.append(1)
    
    def open(self):
        if self.is_open == False:
            self.window = Toplevel(self.parent)
        self.window.geometry("370x380+" + str(self.parent.control_panel_xpos) + "+" + str(self.parent.control_panel_ypos))  
        self.window.wm_title("CK control panel")
        self.window.configure(bg="black")
        print("loading control window")
        self.window.protocol('WM_DELETE_WINDOW', self.cp_close)
        self.pgm_box = []
        self.pgm_down = []
        self.pgm_up = []
        self.inst_button = []
        self.k1 = []
        self.k2 = []
        self.fish = []
        self.fishman_strings = ['All','E','A','D','G','B','e']
        
        self.font_big = Font(family="Ariel", size=24)
        self.font_med = Font(family="Ariel", size=18)

        self.button_play = Button(self.window, text="Play", command=lambda: self.parent.q(self.parent.ls.playback(['play'])),bg="#003366", fg="white", width=5)
        self.button_play.grid(row=5, column=1)
        self.button_stop = Button(self.window, text="Stop", command=lambda: self.parent.q(self.parent.ls.playback(['stop'])),bg="#003366", fg="white", width=5)
        self.button_stop.grid(row=5, column=2)
        
        #self.sv = StringVar()
        #self.sv.trace("w", lambda name, index, mode, sv=self.sv: self.text_changed())
        
        self.loops_button = Button(self.window, text="Loops", command=lambda: self.parent.q(self.parent.ls.select(["Loops",1])),bg="#003366", fg="white", width=5)
        self.loops_button.grid(row=1, column=7)
        
        row_offset = 2
        for i,instrument in enumerate(['Kontakt','GuitarIn','Massive','FM8']):
            print ("br",i,instrument)
            self.inst_button.append(Button(self.window, text=instrument, command=lambda l_inst = instrument: self.parent.q(self.parent.ls.select([l_inst])),bg="#003366", fg="white", width=len(instrument)))
            self.inst_button[i].grid(row=i+row_offset, column=7)
            self.pgm_up.append(Button(self.window, text="Next\nPgm", command=lambda li = i: self.program_button(li,1),bg="#003366", fg="white", width=5))
            self.pgm_up[i].grid(row=i+row_offset, column=6)
            self.pgm_box.append(Entry(self.window, width=3,exportselection=False, bg="black", fg="lightblue", font=self.font_big, insertbackground="white")) #, textvariable = self.sv, borderwidth=0) 
            self.pgm_box[i].grid(row=i+row_offset, column=5,sticky=W)
            self.pgm_box[i].insert(0,"1")
            self.pgm_down.append(Button(self.window, text="Prev\nPgm", command=lambda li = i: self.program_button(li,-1),bg="#003366", fg="white", width=5))
            self.pgm_down[i].grid(row=i+row_offset, column=4)
            self.k2.append(Button(self.window, text="K2", command=lambda l_inst = instrument: self.parent.q(self.parent.ls.output(['KeysIn2',l_inst])),bg="#003366", fg="white", width=5))
            self.k2[i].grid(row=i+row_offset, column=3)
            self.k1.append(Button(self.window, text="K1", command=lambda l_inst = instrument: self.parent.q(self.parent.ls.output(['KeysIn1',l_inst])),bg="#003366", fg="white", width=5))
            self.k1[i].grid(row=i+row_offset, column=2)
            self.fish.append(Button(self.window, text="Fish", command=lambda l_inst = instrument: self.parent.q(self.parent.ls.output(['Fishman',l_inst])),bg="#003366", fg="white", width=5))
            self.fish[i].grid(row=i+row_offset, column=1)
 

        self.window.focus_set()
        
    def cp_close(self):
        self.parent.control_panel_xpos = self.window.winfo_x()
        self.parent.control_panel_ypos = self.window.winfo_y()
        self.parent.save_prefs()
        self.window.destroy()

    def program_change(self,pgm,ch):
        self.programs[ch] = pgm
        self.pgm_box[ch].delete(0,END)
        self.pgm_box[ch].insert(0,str(self.programs[ch]))

    def program_button(self,ch,delta):
        if ch == 0:
            #fucking kontakt
            self.programs[0]+=delta
            self.parent.ls.outsub(['keysin2',self.programs[0]])
            self.program_change(self.programs[0],ch)
        else:
            self.parent.ls.pgm([self.programs[ch] + delta,ch])
    
