#/usr/bin/env python3
from OSC import OSCServer, OSCClient, OSCMessage, OSCBundle

import io
import sys
import glob
import os.path
from Tkinter import *
from tkFont import Font
import types
import re
import ast
import shlex
import time
from threading import Timer
import json
from ls_parser import ls
from ls_setlist_window import ls_setlist_window
#import imp
try:
    #imp.find_module('ck_control_panel')
    from ck_control_panel import ck_control_panel
    ck_ctl = True
except ImportError:
    ck_ctl = False
print ("ck ctl panel present: ",ck_ctl)

class liveScriptWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.exitFlag = False
        self.parent = parent    
        self.ck_ctl = ck_ctl
        self.is_locked = False
        self.is_muted = False
        self.lock_timer = None
        self.offset_time = 0.0
        self.current_song_name = ""
        self.tempo = 120.0
        self.signature_numerator = 4
        self.signature_denominator = 4
        self.song_saved = True
        self.arrQueue = []
        self.undoables = 0
        self.first_run = True
        self.setlist_window = None
        self.filler_words = ['slot','sl','scene','ch','channel','track']
        self.xpos = 870
        self.ypos = 420
        self.ls = ls(self)
        self.setlist = []
        self.setlist_file = "setlist.txt"
        self.setlist_window = ls_setlist_window(self)
        self.setlist_xpos = 150
        self.setlist_ypos = 350
        if ck_ctl:
            self.control_panel = ck_control_panel(self)
        self.control_panel_xpos = 0
        self.control_panel_ypos = 0
        self.prefs_file = "prefs.txt"
        self.load_prefs()

        parent.wm_title("LiveScript")
        parent.geometry("720x400+" + str(self.xpos) + "+" + str(self.ypos) )  
        parent.configure(bg="black")
        self.font_big = Font(family="Ariel", size=24)
        self.font_med = Font(family="Ariel", size=18)
        
        label_title = Label(parent, text="Name:", bg="black", fg="white")
        label_title.grid(row=0, column=0, sticky=E)
        self.sv = StringVar()
        self.sv.trace("w", lambda name, index, mode, sv=self.sv: self.text_changed())
        self.entry_title = Entry(parent, width=22,exportselection=False, bg="black", fg="lightblue", font=self.font_big, insertbackground="white", textvariable = self.sv, borderwidth=0) 
        self.entry_title.grid(row=0, column=1,sticky=W)
        self.label_count = Label(parent, text="0/0", bg="black", fg="white", font=self.font_med)
        self.label_count.grid(row=0, column=2, sticky=S)
        self.button_add = Button(parent, text="Add", command=self.scene_add,bg="#003366", fg="white", width=5)
        self.button_add.grid(row=0, column=3, sticky=S)
        self.button_del = Button(parent, text="Delete", command=self.scene_del,bg="#664433", fg="white", width=5)
        self.button_del.grid(row=0, column=4, padx=6, sticky=S)
        
        self.listbox_setlist = Listbox(parent, height=18,width=15,exportselection=False, bg="black", fg="white")
        self.listbox_setlist.grid(row=0, column=5, columnspan=2, rowspan=5, sticky=NW, pady=12)
        
        
        label_desc = Label(parent, text="Info:", bg="black", fg="white")
        label_desc.grid(row=1, column=0, sticky=E)
        self.sv2 = StringVar()
        self.sv2.trace("w", lambda name, index, mode, sv=self.sv2: self.text_changed())
        self.entry_desc = Entry(parent, width=22,exportselection=False, bg="black", fg="blue",  font=self.font_big, insertbackground="white", textvariable = self.sv2, borderwidth=0) 
        self.entry_desc.grid(row=1, column=1,sticky=NW)
        self.button_reload = Button(parent, text="Reload", command=self.reload,bg="#664433", fg="white", width=8)
        self.button_reload.grid(row=1, column=2, sticky=W, padx=0)
        self.button_move_up = Button(parent, text="Up", command=self.scene_up,bg="#333333", fg="white", width=5)
        self.button_move_up.grid(row=1, column=3, padx=6, pady=10)
        self.button_move_down = Button(parent, text="Down", command=self.scene_down,bg="#333333", fg="white", width=5)
        self.button_move_down.grid(row=1, column=4, padx=6, pady=10)

        self.button_undo = Button(parent, text="Undo", command=self.undo,bg="#003366", fg="white")
        self.button_undo.grid(row=2, column=0, sticky=N)
        self.text_scroll = Scrollbar(parent)
        self.text_script = Text(parent, height=14, width=50, bg="#333333", selectbackground="blue", fg="white", insertbackground="white", wrap=WORD)
        self.text_script.grid(row=2, column=1, rowspan=2,sticky=W)
        self.text_scroll.grid(row=2,column=2, sticky=N+S+W,rowspan=2)
        self.text_script.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.config(command=self.text_script.yview)
        self.text_script.tag_configure("even",background="#222222")
        self.text_script.tag_configure("odd",background="#000000")
        self.text_script.tag_configure("sel",bgstipple="@solid.xbm", borderwidth=1) #background="#cc0000",
        self.button_prev = Button(parent, text="Previous", command=self.prevScene,bg="#003366", fg="white", width=13, height=3)
        self.button_prev.grid(row=2, column=3, columnspan=2, sticky=N)

        self.button_undo_all = Button(parent, text="Undo\nAll", command=self.undo_all,bg="#003366", fg="white")
        self.button_undo_all.grid(row=3, column=0, sticky=N, pady=20)
        self.button_undo_all = Button(parent, text="Undo\n+\nRedo", command=self.undo_redo,bg="#003366", fg="white")
        self.button_undo_all.grid(row=3, column=0, sticky=S)
        self.button_next = Button(parent, text="Next", command=self.nextScene,bg="#003366", fg="white", height=9, width=13)
        self.button_next.grid(row=3, column=3, columnspan=2, sticky=S, pady=6)
        
        label_next = Label(parent, text="Next:", bg="black", fg="white")
        label_next.grid(row=4, column=0, sticky=E)
        self.label_next_title = Label(parent, text="(next scene)", bg="black", fg="#FF6666", font=self.font_big, width=21, anchor=W)
        self.label_next_title.grid(row=4, column=1, sticky=W)
        self.button_save = Button(parent, text="Save", command=self.saveSong,bg="green", fg="black", width=8)
        self.button_save.grid(row=4, column=2)
        self.button_mute = Button(parent, text="Mute", command=self.mute,bg="#333333", fg="white", width=13)
        self.button_mute.grid(row=4, column=3, columnspan=2)
        
        self.button_setlist = Button(parent, text="Setlist\nManager", command=self.setlist_window.open,bg="#003366", fg="white", width=13)
        self.button_setlist.grid(row=4, column=5, sticky=N)
        
        label_info2 = Label(parent, text="Info:", bg="black", fg="white")
        label_info2.grid(row=5, column=0, sticky=E)
        self.label_next_info = Label(parent, text="(next desc)", bg="black", fg="red",  font=self.font_big, width=21, anchor=W)
        self.label_next_info.grid(row=5, column=1, sticky=NW)
        self.button_send = Button(parent, text="Send", command=self.sendBox,bg="#003366", fg="white", width=8)
        self.button_send.grid(row=5, column=2)

        #self.liveTime = Label(parent, text="0")
        #self.liveTime.pack(side="top",anchor="n")
        self.button_play = Button(parent, text="Play", command=lambda: self.ls.playback(['foo','play'],True),bg="#003366", fg="white", width=5)
        self.button_play.grid(row=5, column=3)
        self.button_stop = Button(parent, text="Stop", command=lambda: self.ls.playback(['foo','stop'],True),bg="#003366", fg="white", width=5)
        self.button_stop.grid(row=5, column=4)
        if ck_ctl:
            self.button_stop = Button(parent, text="Ctl", command=self.control_panel.open,bg="#003366", fg="white", width=5)
            self.button_stop.grid(row=5, column=5)

        self.server = OSCServer( ("localhost", 9000) )
        self.server.timeout = 0
        self.timed_out = False
        self.server.addMsgHandler( "/livescript/next", self.nextScene )
        self.server.addMsgHandler( "/live/sync", self.update_sync )
        self.server.addMsgHandler( "/live/error", self.live_error )
        
        for crap in ['master/devices','startup','track/devices','track/device/param','return/devices','track/volume','track/select','track/send','tempo','metronome','play','track/state']:
            self.server.addMsgHandler( "/live/" + crap, self.foo )

        self.server.handle_timeout = types.MethodType(self.handle_timeout, self.server)
        self.client = OSCClient()
        self.client.connect( ("localhost", 9001) )

        self.scene_index = 0
        self.song_index = -1
        self.arrSong = []
        self.arrScene = []
        #self.setPath = "songs/"
        self.load_set()
            
    #def setlist_window_remove(self):
    #    self.setlist_window.destroy()
    #    self.setlist_window = None
        
    def foo(self,*args):
        pass
        
    def text_changed(self,*args):
        self.button_save.configure(bg="red",text="Save Me")

        
    def mute(self,*args):
        if self.is_muted:
            self.is_muted = False
            self.button_mute.configure(bg="#333333",text="Mute", fg="white")
        else:
            self.is_muted = True
            self.button_mute.configure(bg="red",text="Muted!")
    def update_sync(self,path, tags, args, source):
        network_lag = .01
        self.offset_time = args[2] - time.clock() + network_lag
        self.tempo = args[1]
        live_time = (time.clock() + self.offset_time ) / (self.signature_numerator / (self.tempo / 60.0))
        print(str(live_time)[0:5] + " time:" + str(args))
        
    def live_error(self,path, tags, args, source):
        print("live error! " + str(args))
        
    def load_prefs(self):
        if os.path.isfile(self.prefs_file):
            f = open(self.prefs_file,'r+')
            prefs_data = json.load(f)
            print("loading from prefs file")
            f.close()

            print(prefs_data)
            for pref in prefs_data:
                print(str(pref) + ":" + str(prefs_data[pref]))
                setattr(self, pref, prefs_data[pref])
                
                
        else:
            print("creating new prefs file")
            self.save_prefs()
            #prefs_data = json.loads('{"setlist_file":"setlist.txt"}')
            #prefs_data = {"setlist_file":"setlist.txt",}
            #json.dumps(prefs_data)
            
        
    def save_prefs(self):
        saveable_prefs = ['setlist_file','tempo','xpos','ypos','setlist_xpos','setlist_ypos','control_panel_xpos','control_panel_ypos']
        print("window at:" + str(self.parent.winfo_x()) + " x " + str(self.parent.winfo_y()))
        self.xpos = self.parent.winfo_x()
        self.ypos = self.parent.winfo_y()
#        if os.path.isfile(self.prefs_file):
        f = open(self.prefs_file,'w')
        print("saving to prefs file")
#        else:
#            print("creating new prefs file!")
#            f = open(self.prefs_file,'a')
        dict_prefs = {}
        for pref in saveable_prefs:
            dict_prefs[pref] = getattr(self,pref)
        f.write(json.dumps(dict_prefs))
        f.close()
        
    def load_set(self):
        if os.path.isfile(self.setlist_file):
            f = open(self.setlist_file,'r')
            setlist = json.load(f)
            print("loading from set file")
        else:
            print("creating new set file")
            f = open(self.setlist_file,'a')
            setlist = "empty set,"
            #ex.prefs = json.loads('{"mod":0}')
            #json.dump(ex.prefs, f)
        f.close()
        self.setlist = setlist #.split('\n')
        #ls.text_script.insert(END,ls.setlist)
        self.listbox_setlist.delete(0, END)
        self.setlist = []
        for song in setlist: #.split('\n'):
            #song = song.split(",")
            self.setlist.append(song)
            self.listbox_setlist.insert(END,song[0])
        self.listbox_setlist.selection_set(0)
        #print("setlist:" + str(self.setlist))
        
    def handle_timeout(self,server):
        self.timed_out = True
 
    def saveSong(self):
        self.arrSong[self.scene_index] = self.entry_title.get() + "," + self.entry_desc.get() + "," + self.text_script.get("1.0",END).replace('\n',',').replace('\r','').strip(',').strip(' ')
        #songFile = self.setPath + self.current_song_name + ".csv"
        songFile = self.setlist[self.song_index][1]
        f = open(songFile,'w')
        f.write('\n'.join(self.arrSong))
        print("saving to ",songFile)
        f.close()
        self.button_save.configure(bg="green",text="Saved")
        self.text_script.edit_modified(False)
        self.song_saved = True


    def loadSong(self):
        songFile = self.setlist[self.song_index][1]
        if os.path.isfile(songFile):
            f = open(songFile,'r+')
            self.arrSong = f.read().split('\n') #json.load(f)  we gonna json this bitch yet?
            #print("loading from song file" + str(self.arrSong))
            
        else:
            print("creating new song file")
            f = open(songFile,'a')
            self.arrSong = ["empty"]
            #ex.prefs = json.loads('{"mod":0}')
            #json.dump(ex.prefs, f)
        f.close()
        #ls.text_script.insert(END,ls.setlist)
        #ls.listbox_setlist.clear()
        self.scene_index = 0
        self.song_saved = True
        self.button_save.configure(bg="green", text="Saved")
        self.refreshScene()

    def scene_del(self,*arg):
        if len(self.arrSong) > 1:
            self.arrSong.pop(self.scene_index)
            if self.scene_index > 0:
                self.scene_index -= 1
            self.song_saved = False
            self.button_save.configure(bg="red",text="Save Me")
            self.refreshScene()

 
    def scene_add(self,*arg):
            new_scene = "New Scene,New Info"
            self.arrSong.insert(self.scene_index+1,new_scene)
            self.scene_index += 1
            self.song_saved = False
            self.button_save.configure(bg="red",text="Save Me")
            self.refreshScene()

    def scene_up(self,*arg):
        if self.scene_index < len(self.arrSong) - 1:
            self.arrSong.insert(self.scene_index + 1,self.arrSong.pop(self.scene_index))
            self.scene_index += 1
            self.song_saved = False
            self.button_save.configure(bg="red",text="Save Me")
            self.refreshScene()

    def scene_down(self,*arg):
        if self.scene_index > 0:
            self.arrSong.insert(self.scene_index - 1,self.arrSong.pop(self.scene_index))
            self.scene_index -= 1
            self.song_saved = False
            self.button_save.configure(bg="red",text="Save Me")
            self.refreshScene()

    def nextScene(self,*arg):
        if not self.is_locked:
            self.scene_index += 1
            if self.scene_index >= len(self.arrSong):
                print("end of song")
                if self.song_index + 1 < len(self.setlist):
                    self.song_index += 1
                else:
                    self.song_index = 0
                    
                self.scene_index = 0
                
                self.current_song_name = self.setlist[self.song_index][0]
                self.listbox_setlist.select_clear(0,END)
                self.listbox_setlist.selection_set(self.song_index)
                self.loadSong()
            else:
                self.refreshScene()
        else:
            self.locker(False)
 
    def reload(self,*arg):
        #self.locker(False)
        self.scene_index = 0
        self.loadSong()
 
    def prevScene(self):
        if self.scene_index < 1 :
            self.scene_index = len(self.arrSong) 
        self.scene_index = self.scene_index - 1
        self.refreshScene()
 
    def quit(self):
        self.server.close()
        self.parent.destroy()

    def locker(self,lock = False, lock_bars = 0):
        if lock:
            self.button_next.configure(bg = "red", text="Locked")
            #print("timer",lock_bars ,self.tempo ,self.signature_numerator,lock_bars * (self.signature_numerator / (self.tempo / 60.0))+ .1)
            self.lock_timer = Timer(lock_bars * (self.signature_numerator / (self.tempo / 60.0))+ .1, self.locker)
            self.lock_timer.start()
        else:
            self.button_next.configure(bg = "#003366", text="Next")
            if self.lock_timer != None:
                self.lock_timer.cancel() #= None
        print("lock",lock)
        self.is_locked = lock


        
    def refreshScene(self):
        print("-----------AND SCENE---------------------------")
        self.arrScene = self.arrSong[self.scene_index].split(",")
        if self.scene_index < (len(self.arrSong) - 1):
            nxt = self.arrSong[self.scene_index + 1].split(",")
        else:
            nxt = ["END OF SONG","(load next song)"]
            
            
            
        self.label_count.configure(text=str(self.scene_index +1) + "/" + str(len(self.arrSong)))
        self.text_script.delete('1.0', END)
        tag = "even"
        for line in self.arrScene[2:len(self.arrScene)]:
            self.text_script.insert(END,line+"\n",tag)
            tag = "even" if tag == "odd" else "odd"
        self.entry_title.delete(0, END)
        self.entry_title.insert(END,self.arrScene[0])
        self.entry_desc.delete(0, END)
        self.entry_desc.insert(END,self.arrScene[1])
        self.label_next_title.configure(text=nxt[0])
        self.label_next_info.configure(text=nxt[1])
        """
        for lsCmd in self.arrScene[2:len(self.arrScene)]:
            lsCmd = re.sub('\[([^\]]+)\]','',re.sub('[\s]+', ' ',lsCmd.lower().strip()))
            arrCmd = lsCmd.split(" ")
            
            #if there is a delay command make sure it's the last element
            delayCmds = [i for i, s in enumerate(arrCmd) if '+' in s]
            if delayCmds:
                barDelay = arrCmd.pop(delayCmds[0])
                print( "delay " + str(barDelay) + "bars: " + str(arrCmd))
                arrCmd.append(barDelay)
            try:
                result = getattr(self, 'ls_'+arrCmd[0])(arrCmd)
            except Exception, e:
                print('404! ' + str(e) + "\n" + str(arrCmd))
        """
        self.text_script.edit_modified(False)
        if self.song_saved:
            self.button_save.configure(bg="green", text="Saved")
        self.sendBox()
        
    def sendBox(self):
        try:
            txtScene = self.text_script.selection_get()          
            whole_box = False
        except:
        #    txtScene = ""
        #if len(txtScene) < 1:
            txtScene = self.text_script.get("1.0",END)
            whole_box = True
           
        if not self.is_muted or not whole_box:
            print("processing:",txtScene)
        else:
            print("(muted)")
        
        wait_time = 0
        self.undoables = 0
        if self.first_run:
            self.first_run = False
            return #dont send the patch at startup
        else:
            txtScene = re.sub('\[([^\]]+)\]','',txtScene.lower()) #remove comments and extra breaks, lower case
            for lsCmd in txtScene.split("\n"):
                lsCmd = re.sub('[\s]+', ' ',lsCmd.strip()) #remove extra space
                #lsCmd = re.sub('\[([^\]]+)\]','',re.sub('[\s]+', ' ',lsCmd.lower().strip()))
                #arrCmd = lsCmd.split(" ")
                arrCmd = shlex.split(lsCmd)
                if len(arrCmd) < 2:
                    #print("no valid cmd")
                    continue
                oscm = None
                #if there is a delay command only use the first one (they can be nested this way but that's dumb)
                delayCmds = [[i,s] for i, s in enumerate(arrCmd) if (s[0] == '+')]
                if delayCmds:
                    print(["delay",delayCmds])
                    if delayCmds[0][1][-1] == 'b': #if the last character is a b then the number is for beats, not bars
                        delayCmd = ['beats',int(delayCmds[0][1][1:-1])]
                    else:
                        delayCmd = ['bars',int(delayCmds[0][1][1:])]
                    arrCmd.pop(delayCmds[0][0])
                    #print( "delay " + str(barDelay) + "bars: " + str(arrCmd))
                    #arrCmd.append(barDelay)
                try:
                    if arrCmd[0] not in ["fade","playback","lock"]:
                        self.undoables += 1
                    if not self.is_muted or not whole_box and oscm !='\n':
                        oscm = getattr(self.ls, arrCmd[0])(arrCmd[1:])
                    if arrCmd[0].lower() == 'wait':
                        wait_time += arrCmd[1]
                    
                    if oscm is not None:
                        if delayCmds and whole_box and not self.is_muted:
                            #oscm.append(barDelay,'k')
                            secPerBeat = 1 / (self.tempo / 60.0)
                            secPerBar = self.signature_numerator * secPerBeat
                            live_time = (time.clock() + self.offset_time ) / (self.signature_numerator / (self.tempo / 60.0))
                            pctToNextBar = (1 - (live_time - int(live_time)))
                            secToNextBeat = (pctToNextBar * self.signature_numerator - int(pctToNextBar * self.signature_numerator)) * secPerBeat
                            secToNextBar = pctToNextBar * secPerBar
                            #secToNextBar = (self.signature_numerator - (live_time % self.signature_numerator)) * secPerBar / self.signature_numerator
                            if delayCmd[0] == 'beats':
                                secDelay = delayCmd[1] * secPerBeat + secToNextBeat + .01
                            else:
                                secDelay = delayCmd[1] * secPerBar + secToNextBar + .01
                            schTime = (time.clock() + self.offset_time + secDelay ) / (self.signature_numerator / (self.tempo / 60.0))

                            print(str(live_time)[0:5]+ " delay " + str( delayCmd[1]) +  delayCmd[0]  + str(oscm) + " del=" + str(schTime)[0:5] + " sec=" + str(secDelay)[:5] + " snb=" + str(secToNextBar)[:5])
                            self.q(oscm,secDelay)
                            #self.arrQueue.append([oscm,time.clock() + secDelay])
                            #Timer(secDelay, self.send, [oscm]).start()
                        else:
                            if not self.is_muted or not whole_box:
                                self.arrQueue.append([oscm,time.clock() + wait_time])
                                #self.send( oscm )
                except Exception, e:
                    print('cmd err! ' + str(e) + str(arrCmd))
                    
    def q(self,oscm, secDelay = 0):
        self.arrQueue.append([oscm,secDelay + time.clock()])
                
    def send(self,oscm):
        live_time = (time.clock() + self.offset_time ) / (self.signature_numerator / (self.tempo / 60.0))
        print(str(live_time)[0:6]  + ": "+ str(oscm)) #+ "/" + str(time.clock())[:5]
        self.client.send( oscm )

    def queue_poll(self):
        poll_time = 1
        for idx,arrCmd in enumerate(self.arrQueue):
            if arrCmd[1] <= time.clock():
                #print(str(time.clock()) + ": " + arrCmd[0])
                self.send(arrCmd[0])
                self.arrQueue.pop(idx)
        self.after(poll_time,self.queue_poll)
                
    def undo(self):
        oscm = self.ls.undo([])
        self.arrQueue.append([ oscm, 0 ])
        
    def undo_redo(self):
        self.undo_all()
        self.sendBox()
        
    def undo_all(self):
        #cmds_to_undo = tuple(["rec","play"])
        #undoable = []
        #undoable.extend(undo_add for undo_add in self.arrScene[2:] if (undo_add.strip().lower().startswith(cmds_to_undo)))
        print(str(self.undoables) + " undoables")
        if self.undoables == 0:
            self.undoables = 1
        oscm = self.ls.undo(["undo",self.undoables])
        self.arrQueue.append([ oscm,0] )
        

    def check_buttons(self):    
        if self.text_script.edit_modified() and self.button_save.cget('bg') != 'red':
            self.button_save.configure(bg="red",text="Save Me")
        try:
            #if self.current_song_name != self.listbox_setlist.get(self.listbox_setlist.curselection()[0]):
            #    self.current_song_name = self.listbox_setlist.get(self.listbox_setlist.curselection()[0])
            if self.song_index != self.listbox_setlist.curselection()[0]:
                self.song_index = self.listbox_setlist.curselection()[0]
                self.loadSong()
        except:
            print("somethings up with the listbox ",self.listbox_setlist.curselection()[0],self.current_song_name,self.listbox_setlist.get(self.listbox_setlist.curselection()[0]))
        self.after(1000,self.check_buttons)
        
    def on_quit(self):
        self.exitFlag = True
        self.save_prefs()
        #root.destroy()

def main():
    root = Tk()
    ls_window = liveScriptWindow(root)
    root.protocol("WM_DELETE_WINDOW", ls_window.on_quit)
    #print (json.dumps(ex.prefs))
    #print ("mod=" + str(ex.prefs[u'mod']) + "\n")
    #f = open(prefsPath,'r+')
    #json.dump(ex.prefs, f)
    ls_window.check_buttons()
    ls_window.queue_poll()
    while not ls_window.exitFlag:
        #while not ls.server.timed_out:
        ls_window.server.handle_request()
        root.update_idletasks()
        root.update()
        

        
if __name__ == '__main__':
    main()  
        