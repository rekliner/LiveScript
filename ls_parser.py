from OSC import OSCMessage, OSCBundle
class ls():
    def __init__(self, parent):
        self.parent = parent     
        
    def int_or_string(self,strName):
        try: 
            int(strName)
            return int(strName)
        except ValueError:
            return strName
            
    def int_float_string(self,strName):
        try: 
            int(strName)
            return int(strName)
        except ValueError:
            try:
                float(strName)
                return float(strName)
            except ValueError:
                return strName
    
    def simple_cmd(self,osc_addr,arrCmd):
        oscm = OSCMessage(osc_addr)
        for i in range(len(arrCmd)):
            if arrCmd[i] not in self.parent.filler_words:
                oscm.append(self.int_or_string(arrCmd[i]))
        return oscm
    

    def arm(self,arrCmd):
        arrCmd.append(-2)
        return self.simple_cmd("/live/track/arm",arrCmd)
        
    def assign(self,arrCmd):
        return self.simple_cmd("/live/cc/assign",arrCmd)
        
    def box(self,arrCmd):
        return self.simple_cmd("/live/track/select",arrCmd)       
        
    def cc(self,arrCmd):
        return self.simple_cmd("/live/midi/cc",arrCmd)
        
    def collapsed(self,arrCmd):
        return self.simple_cmd("/live/track/collapsed",arrCmd)        
        
    def copy(self,arrCmd):
        return self.simple_cmd("/live/clip/copy",arrCmd)
		
    def cspos(self,arrCmd):
        return self.simple_cmd("/live/controller/position",arrCmd)

    def delete(self,arrCmd):
        return self.simple_cmd("/live/clip/delete",arrCmd)
        
    def devon(self,arrCmd):
        if arrCmd[0].lower() == "send":
            oscm = OSCMessage("/live/return/device/param" )
            arrCmd.pop(0)
        else:
            oscm = OSCMessage("/live/track/device/param" )
        oscm.append(self.int_or_string(arrCmd[0]))  #track
        oscm.append(self.int_or_string(arrCmd[1]))  #device
        oscm.append(0,'i')                          #param 0
        oscm.append(1,'i')                          #on
        return oscm
        
    def devoff(self,arrCmd):
        if arrCmd[0].lower() == "send":
            oscm = OSCMessage("/live/return/device/param" )
            arrCmd.pop(0)
        else:
            oscm = OSCMessage("/live/track/device/param" )
        oscm.append(self.int_or_string(arrCmd[0]))  #track
        oscm.append(self.int_or_string(arrCmd[1]))  #device
        oscm.append(0,'i')                          #param 0
        oscm.append(0,'i')                          #off
        return oscm

    def disarm(self,arrCmd):
        arrCmd.append(0)
        return self.simple_cmd("/live/track/arm",arrCmd)
        
    def fade(self,arrCmd):
        oscm = OSCMessage("/live/track/fade")
        oscm.append(self.int_or_string(arrCmd[0])) #track
        oscm.append(float(arrCmd[1])) #final volume
        if len(arrCmd) > 2:
            oscm.append(arrCmd[2]) #bars, beats, or secs
            if arrCmd[2].lower == 'bars' or arrCmd[2].lower == 'beats':
                oscm.append(int(arrCmd[3])) #final volume
            else:
                oscm.append(float(arrCmd[3])) #final volume
                
            if len(arrCmd) > 4:
                oscm.append(int(arrCmd[4])) #increments
        else:
            oscm.append('bars') #bars, beats, or secs
            oscm.append(1) #bars, beats, or secs
        return oscm
        
    def input(self,arrCmd):
        return self.simple_cmd("/live/track/input",arrCmd)
                
    def inputblock(self,arrCmd):
        return self.simple_cmd("/live/track/input/block",arrCmd)
        
    def insub(self,arrCmd):
        return self.simple_cmd("/live/track/insub",arrCmd)

    def kit(self,arrCmd):   #this one's more for my own set
        oscm = OSCMessage("/live/track/device/param" )
        oscm.append(self.int_or_string(arrCmd[0]))  #track
        oscm.append('Kits','s')                     #device named kits
        oscm.append(9,'i')                          #param chain selector
        oscm.append(int(arrCmd[1]),'i')             #value
        return oscm
            
    def knob(self,arrCmd):
        if arrCmd[0].lower() == "send":
            oscm = OSCMessage("/live/return/device/param" )
            arrCmd.pop(0)
        else:
            oscm = OSCMessage("/live/track/device/param" )
        oscm.append(self.int_or_string(arrCmd[0]))  #track
        oscm.append(self.int_or_string(arrCmd[1]))  #device
        oscm.append(self.int_or_string(arrCmd[2]))  #param
        oscm.append(float(arrCmd[3]),'f')           #value
        return oscm
        
    def lock(self,arrCmd):
        self.parent.locker(True,int(arrCmd[0]))
        return None
                        
    def loopstart(self,arrCmd):
        oscm = OSCMessage("/live/clip/loop/start")
        oscm.append(self.int_or_string(arrCmd[0])) #track
        oscm.append(int(arrCmd[1])) #slot
        print(str(["loopstart bars", arrCmd[2],self.parent.signature_numerator]))
        if arrCmd[2].lower() == 'bars':
            oscm.append((float(arrCmd[3]) - 1) * self.signature_numerator) #position in beats
        else:
            oscm.append(float(arrCmd[3]) - 1) #position in beats
        return oscm
        
    def loopend(self,arrCmd):
        oscm = OSCMessage("/live/clip/loop/end")
        oscm.append(self.int_or_string(arrCmd[0])) #track
        oscm.append(int(arrCmd[1])) #slot
        if arrCmd[2].lower() == 'bars':
            oscm.append((float(arrCmd[3]) - 1) * self.parent.signature_numerator) #position in beats
        else:
            oscm.append(float(arrCmd[3]) - 1) #position in beats
        return oscm
        
    def looping(self,arrCmd):
        oscm = OSCMessage("/live/clip/looping")
        oscm.append(self.int_or_string(arrCmd[0])) #track
        oscm.append(int(arrCmd[1])) #slot
        try: 
            arrCmd[2] = int(arrCmd[2])
            oscm.append(arrCmd[2]) #bars, beats, or secs
        except:
            if arrCmd[2].lower() == 'off':
                oscm.append(0)
            else:
                oscm.append(1)
        return oscm
        
    def metro(self,arrCmd):
        oscm = OSCMessage("/live/metronome")
        val = 1 if arrCmd[0].lower() == 'on' else 0
        oscm.append(val,'i')
        return oscm

    def mute(self,arrCmd):
        oscm = OSCMessage("/live/track/mute" )
        oscm.append(self.int_or_string(arrCmd[0]))
        oscm.append(1,'i')
        return oscm
        
    def note(self,arrCmd):
        return self.simple_cmd("/live/midi/note",arrCmd)
        
    def osc(self,arrCmd):
        oscm = OSCMessage(arrCmd[0])
        for i in range(1,len(arrCmd)):
            oscm.append(self.int_float_string(arrCmd[i]))
        return oscm

    def output(self,arrCmd):
        return self.simple_cmd("/live/track/output",arrCmd)

    def outsub(self,arrCmd):
        return self.simple_cmd("/live/track/outsub",arrCmd)

    def overdub(self,arrCmd):
        oscm = OSCMessage("/live/overdub")
        if arrCmd[0].lower() == 'on':
            oscm.append(1,'i')
        else:
            oscm.append(0,'i')
        return oscm
                
    def param(self,arrCmd): #i like options
        return self.knob(arrCmd)
        
    def pgm(self,arrCmd):
        arrCmd[0] = int(arrCmd[0]) - 1 if int(arrCmd[0]) > 0 else 0 #keep it 1 based instead of 0 based counting for consistancy
        oscm = self.simple_cmd("/live/midi/pgm",arrCmd)
        if self.parent.ck_ctl:
            ch = 1
            if len(oscm) > 1:
                ch = oscm[1]
            self.parent.control_panel.program_change(arrCmd[0] + 1,ch)
        return oscm

    def play(self,arrCmd):
        return self.simple_cmd("/live/clip/play",arrCmd)

    def playback(self,arrCmd):
        oscm = OSCMessage("/live/stop") if arrCmd[0].lower() == 'stop' else OSCMessage("/live/play")
        return oscm

    def prm(self,arrCmd): #i like options
        return self.knob(arrCmd)
                
    def program(self,arrCmd): #i like options
        return self.pgm(arrCmd)

    def prog(self,arrCmd): #i like options
        return self.pgm(arrCmd)

    def rec(self,arrCmd):
        return self.simple_cmd("/live/clip/rec",arrCmd)

    def reset(self,arrCmd):
        return self.simple_cmd("/live/clip/delete/all",arrCmd)
        
    def scene(self,arrCmd):
        return self.simple_cmd("/live/scene/select",arrCmd)
        
    def select(self,arrCmd):
        return self.simple_cmd("/live/track/select",arrCmd)

    def send(self,arrCmd):
        oscm = OSCMessage("/live/track/send" )
        oscm.append(self.int_or_string(arrCmd[0]))
        try:
            arrCmd[1] = int(arrCmd[1])
            arrCmd[1] += 1 #keep it 1 based instead of 0 based counting for consistancy
        except:
            arrCmd[1] = ord(arrCmd[1][0].lower()) - 97 #if using letters instead of numbers, convert to lower case and subtract so 'a' = 0, 'b' = 1, etc..
        oscm.append(int(arrCmd[1]),'i')
        oscm.append(int(arrCmd[2]) / 100.0,'f')
        return oscm
        
    def stop(self,arrCmd):
        if len(arrCmd) == 1:
            stop_cmd = "/live/track/stop"
        else:
            stop_cmd = "/live/clip/stop"
        return self.simple_cmd(stop_cmd,arrCmd)

    def tempo(self,arrCmd):
        oscm = OSCMessage("/live/tempo")
        oscm.append(float(arrCmd[0]),'f')
        self.parent.tempo = float(arrCmd[0])
        return oscm
        
    def timesig(self,arrCmd):
        oscm = OSCMessage("/live/signature" )
        oscm.append(int(arrCmd[0]),'i')
        self.parent.signature_numerator = int(arrCmd[0])
        oscm.append(int(arrCmd[1]),'i')
        self.parent.signature_denominator = int(arrCmd[1])
        return oscm
        
    def trackblock(self,arrCmd):
        return self.simple_cmd("/live/track/create/block",arrCmd)
        
    def undo(self,arrCmd):
        return self.simple_cmd("/live/undo",arrCmd)
        
    def undos(self,arrCmd): #sets the number of undo's manually for the 'undo all' button (and 'undo/redo')
        self.parent.undoables = int(arrCmd[0])
        return None

    def unmute(self,arrCmd):
        oscm = OSCMessage("/live/track/mute" )
        oscm.append(self.int_or_string(arrCmd[0]))
        oscm.append(0,'i')
        return oscm        

    def vol(self,arrCmd):
        oscm = OSCMessage("/live/track/volume" )
        oscm.append(self.int_or_string(arrCmd[0]))
        oscm.append(int(arrCmd[1]) / 100.0,'f')
        return oscm
        
    def wait(self,arrCmd):
        #add a number of ms to delay before executing commands below this one
        return None
                
    def xfade(self,arrCmd):
        oscm = OSCMessage("/live/track/crossfader" )
        oscm.append(self.int_or_string(arrCmd[0]))
        oscm.append(int(arrCmd[1]) / 100.0,'f')
        return oscm
