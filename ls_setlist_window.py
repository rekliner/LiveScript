from Tkinter import *
from tkFileDialog import * 
import os
import json

class ls_setlist_window():
    def __init__(self, parent):
        self.parent = parent
        self.is_open = False
        self.temp_setlist = []
    
    def open(self):
        if self.is_open == False:
            self.window = Toplevel(self.parent)
        self.window.geometry("400x380+" + str(self.parent.setlist_xpos) + "+" + str(self.parent.setlist_ypos))  
        self.window.wm_title("LiveScript Setlist Manager")
        self.window.configure(bg="black")
        print("loading setlist window")
        self.window.protocol('WM_DELETE_WINDOW', self.setlist_close)
        self.listbox_setlist = Listbox(self.window, height=18,width=40,exportselection=False, bg="black", fg="white")
        self.listbox_setlist.grid(row=1, column=0, rowspan=2, columnspan=2)
        for song in self.parent.setlist:
            self.listbox_setlist.insert(END,song[0])
        self.temp_setlist = self.parent.setlist
        
        self.button_add = Button(self.window, text="Add\nSong", command=self.add_song,bg="#003366", fg="white", width=8)
        self.button_add.grid(row=3, column=0)
        self.button_del = Button(self.window, text="Delete\nSong", command=self.del_song,bg="#003366", fg="white", width=8)
        self.button_del.grid(row=3, column=1)
        self.button_del = Button(self.window, text="Move\nUp", command=self.move_up,bg="#003366", fg="white", width=8)
        self.button_del.grid(row=1, column=2)
        self.button_del = Button(self.window, text="Move\nDown", command=self.move_down,bg="#003366", fg="white", width=8)
        self.button_del.grid(row=2, column=2)
        self.button_add = Button(self.window, text="Load\nSet", command=self.load_set,bg="#003366", fg="white", width=8)
        self.button_add.grid(row=4, column=0)
        self.button_del = Button(self.window, text="Save\nSet", command=self.save_set_as,bg="#003366", fg="white", width=8)
        self.button_del.grid(row=4, column=1)
        self.button_del = Button(self.window, text="Save\nSet", command=self.save_set_as,bg="#003366", fg="white", width=8)
        self.button_del.grid(row=3, column=2)
        self.window.focus_set()
        
    def setlist_close(self):
        self.parent.setlist_xpos = self.window.winfo_x()
        self.parent.setlist_ypos = self.window.winfo_y()
        self.parent.save_prefs()
        self.window.destroy()

    
    def add_song(self):
        current_path = os.path.split(os.path.normpath(__file__))[0]
        #current_path = os.path.dirname(sys.argv[0])
        print(current_path)
        file_name = askopenfilename()
        
        simple_name = os.path.splitext(os.path.splitext(os.path.basename(os.path.normpath(file_name)))[0])[0]
        file_name = os.path.relpath(file_name)
        print("adding" + str(simple_name) + ":" + str(file_name))
        self.listbox_setlist.insert(END,simple_name)
        self.temp_setlist.append([simple_name,file_name])

    def load_set(self):
        file_name = askopenfilename() 
        simple_name = os.path.splitext(os.path.splitext(os.path.basename(os.path.normpath(file_name)))[0])[0]
        print("loading" + str(simple_name) + ":" + str(file_name))
        self.parent.setlist_file = os.path.relpath(file_name)
        self.parent.load_set()
        self.listbox_setlist.delete(0,END)
        for song in self.parent.setlist:
            self.listbox_setlist.insert(END,song[0])

    def save_set_as(self):
        file_name = asksaveasfilename(initialfile=self.parent.setlist_file) 
        #simple_name = re.sub(r'[\d_]', '',os.path.splitext(os.path.splitext(os.path.basename(os.path.normpath(file_name)))[0])[0])
        self.parent.setlist_file = file_name
        self.save_set(file_name)
        self.parent.save_prefs()
        #self.listbox_setlist.delete(0,END)
            
    def save_song_as(self): 
        #wip
        file_name = asksaveasfilename(initialfile=self.parent.setlist_file) 
        #simple_name = re.sub(r'[\d_]', '',os.path.splitext(os.path.splitext(os.path.basename(os.path.normpath(file_name)))[0])[0])
        self.parent.setlist_file = file_name
        self.save_set(file_name)
        self.parent.save_prefs()
        #self.listbox_setlist.delete(0,END)
            
    def save_set(self,file_name):
        print("saving" + str(file_name))
        if os.path.isfile(file_name):
            f = open(file_name,'w+')
            print("saving to set file")
        else:
            print("creating new set file!")
            f = open(file_name,'a')
        #dict_songs = {}
        #for song in self.parent.setlist:
        #    dict_prefs[pref] = getattr(self,pref)
        f.write(json.dumps(self.parent.setlist))
        f.close()
        self.parent.setlist = self.temp_setlist
        self.parent.load_set()

    def backup_song(self,song_index):
        #WIP
        print("saving song backup" + str(file_name))
        if os.path.isdir(current_path = os.path.split(os.path.normpath(__file__))[0]):
            f = open(file_name,'w+')
            print("saving to set file")
        else:
            print("creating new set file!")
            f = open(file_name,'a')
        #dict_songs = {}
        #for song in self.parent.setlist:
        #    dict_prefs[pref] = getattr(self,pref)
        f.write(json.dumps(self.parent.setlist))
        f.close()
        self.parent.setlist = self.temp_setlist
        self.parent.load_set()

    def move_up(self):
        try:
            song_index = self.listbox_setlist.curselection()[0]
            print(song_index)
            if song_index == 0:
                print("song already at top!")
                return
            else:
                temp_song = self.temp_setlist.pop(song_index)
                self.listbox_setlist.delete(song_index)
                self.temp_setlist.insert(song_index - 1,temp_song)
                self.listbox_setlist.insert(song_index - 1,temp_song[0])
                self.listbox_setlist.select_set(song_index - 1)
        except IndexError:
            print("no song selected for moving!")

    def move_down(self):
        try:
            song_index = self.listbox_setlist.curselection()[0]
            print(song_index)
            if song_index > self.listbox_setlist.size() - 2:
                print("song already at top!")
                return
            else:
                temp_song = self.temp_setlist.pop(song_index)
                self.listbox_setlist.delete(song_index)
                self.temp_setlist.insert(song_index + 1,temp_song)
                self.listbox_setlist.insert(song_index + 1,temp_song[0])
                self.listbox_setlist.select_set(song_index + 1)
        except IndexError:
            print("no song selected for moving!")

    def del_song(self):
        try:
            print(self.listbox_setlist.curselection()[0])
            self.temp_setlist.pop(self.listbox_setlist.curselection()[0])
            self.listbox_setlist.delete(self.listbox_setlist.curselection()[0])
        except IndexError:
            print("no song selected for deletion!")
        
        
        