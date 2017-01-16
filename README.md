#LiveScript

This parses a scripting language to control Ableton Live SDK through a MIDI remote script.

It sounds complicated but it is a very versatile live tool.  It could be used as a rig manager to move through instrument presets for different songs a live show.  Or in my case it can be used 
every few bars of a song to control which clips are recorded and for how long.  This could be called "scripted looping" and allows one to avoid memorizing a complicated series of buttons in exchange for a plan.

The basic concept is "scenes" that contain a batch of commands, such as volume control, clip recording and launching, playback control, etc..

The information is stored in text files using JSON.  A group of scenes is a song and a setlist manager is included to create a playlist of songs.

I've also included a control panel for my own purposes that you may find useful.  It switches to different track names and adjusts my commonly used settings.

It is meant to be combined with and OSC receiving MIDI remote script such as LiveOSC...which unfortunately hasn't kept up with with recent versions of Ableton Live.  Because of this
I have rewritten it as DeafOSC which ditches two way communication with Live and simply takes orders from LiveScript.