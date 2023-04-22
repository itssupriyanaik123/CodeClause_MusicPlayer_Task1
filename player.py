from tkinter import *
from tkinter import messagebox,filedialog
from ttkthemes import ThemedTk
from tkinter import ttk
from pygame import mixer
from mutagen.mp3 import MP3
from PIL import Image, ImageTk
import os
import time
import threading


class CustomScale(ttk.Scale):
    def __init__(self, master=None, **kw):
        kw.setdefault("orient", "horizontal")
        self.variable = kw.pop('variable', DoubleVar(master))
        ttk.Scale.__init__(self, master, variable=self.variable, **kw)


root = ThemedTk(theme='scidgrey')
root.geometry('338x600')
root.title('HR Music Player')
root.wm_iconbitmap('icons/icon.ico')
root.resizable(False,False)

mixer.init()

style = ttk.Style()
style.configure("BW.Horizontal.TScale", background='#5f6d62', troughcolor='white')

''' set bakground '''
background = Image.open("icons/background.png")
background=background.resize((338,600))
bg = ImageTk.PhotoImage(background)
bgLabel = Label(root,image = bg)
bgLabel.place(x=0,y=0)
bgLabel.pack()

'''declaring variables'''
pause = True
isNewSong = True
song = os.getcwd()
currTimeLength=0
totalTimeLength = 0
volume = 20
mute = False
currSong=0
playList=[]

''' declaring scale bar to show current volume and song played'''

def shift():
    x1,y1,x2,y2 = canvas.bbox("marquee")
    if(x2<0 or y1<0): #reset the coordinates
        x1 = canvas.winfo_width()
        y1 = canvas.winfo_height()//2
        canvas.coords("marquee",x1,y1)
    else:
        canvas.move("marquee", -2, 0)
    canvas.after(1000//20,shift)

canvas = Canvas(root,bg='#5f6d62',highlightthickness=0)
canvas['width']= 180
canvas['height']=25
canvas.place(x=75,y=260)
song_name = canvas.create_text(0,-2000,text='Select A Song From File',font=('Times New Roman',15,'bold'),fill='black',tags=("marquee",),anchor='w')
shift()

curr_time = Label(root,text= '-- : --',bg='#5f6d62')
curr_time.place(x=60,y=311)

tot_time = Label(root,text= '-- : --',bg='#5f6d62')
tot_time.place(x=235,y=311)

song_bar = CustomScale(root,from_=0, to = 500,orient = HORIZONTAL, length =210,style='BW.Horizontal.TScale')
song_bar.place(x=60,y=300)


def set_volume(val):
    global mute,volume
    volume = float(val) / 100
    if not(mute):
        mixer.music.set_volume(volume)
    elif(volume==0):
        mute()
    else:
        unmute()
sound_bar = CustomScale(root,from_=0, to = 100,orient = HORIZONTAL, length =170,style='BW.Horizontal.TScale',command=set_volume)
sound_bar.place(x=80,y=372)
sound_bar.set(20)

''' declaring buttons and assigning functions to them'''

def pauseMusic():
    global pause
    if(not(pause)):
        mixer.music.pause()
        pauseBtn.place_forget()
        playBtn.place(x=153,y=330)
        pause = True

pause_icon = Image.open("icons/pause button.png")
pause_icon = pause_icon.resize((32,32))
pause_icon  = ImageTk.PhotoImage(pause_icon)
pauseBtn = Button(root,image=pause_icon,borderwidth=0,bg='#5f6d62',command=pauseMusic)
pauseBtn.place(x=153,y=330)
pauseBtn.place_forget()


def stopMusic():
    global pause
    mixer.music.stop()
    pauseBtn.place_forget()
    playBtn.place(x=153,y=330)
    pause =True

def currtime(t):
    global pause,currTimeLength,song
    cSong = song
    currTimeLength=0
    try:
        while(currTimeLength<=t and cSong==song):
            if(not(pause)):
                mins = currTimeLength // 60
                secs = currTimeLength % 60
                curr_time['text'] ='{:02d} : {:02d}'.format(mins,secs)
                song_bar.set(currTimeLength)
                time.sleep(1)
                currTimeLength+=1
            if(currTimeLength==t):
                next()
    except:
        stopMusic()
                
def totaltime():
    global totalTimeLength
    
    file_data = os.path.splitext(song)
    if(file_data[1]=='.mp3'):
        audio= MP3(song)
        totalTimeLength=audio.info.length
    else:
        file = mixer.Sound(song)
        totalTimeLength=file.get_length()
        
    totalTimeLength = round(totalTimeLength)
    mins = totalTimeLength//60
    secs = totalTimeLength%60
    tot_time['text'] = '{:02d} : {:02d}'.format(mins,secs)
    song_bar['to'] = totalTimeLength
    
    thrd=threading.Thread(target= currtime ,args= (totalTimeLength,))
    thrd.start()

def playMusic():
    global pause,isNewSong,song
    try:
        if(isNewSong):
            messagebox.showerror('File Not Found','select song to play')
        elif(pause):
            mixer.music.unpause()
            playBtn.place_forget()
            pauseBtn.place(x=153,y=330)
            pause=False
    except:
        messagebox.showerror('File Not Found','select song to play')

play_icon = Image.open("icons/play button.png")
play_icon = play_icon.resize((32,32))
play_icon  = ImageTk.PhotoImage(play_icon)
playBtn = Button(root,image=play_icon,borderwidth=0,bg='#5f6d62',command=playMusic)
playBtn.place(x=153,y=330)


def next():
    global song, playList,currSong,pause,isNewSong
    try:
        mixer.music.stop()
        if currSong == len(playList)-1:
            currSong = 0
        else:
            currSong+=1
        song = playList[currSong]
        mixer.music.load(song)
        time.sleep(1)
        mixer.music.play()
        canvas.itemconfig(song_name,text=os.path.basename(song))
        playBtn.place_forget()
        pauseBtn.place(x=153,y=330)
        pause = False
        isNewSong = False
        totaltime()
    except:
        messagebox.showerror('File Not Found', 'Could not find file to play. Please check again')



next_icon = Image.open("icons/next button.png")
next_icon = next_icon.resize((18,18))
next_icon = ImageTk.PhotoImage(next_icon)
nextBtn = Button(root,image=next_icon,borderwidth=0,bg='#5f6d62',command=next)
nextBtn.place (x=198,y=338)


def previous():
    global song, playList,currSong,pause,isNewSong
    try:
        mixer.music.stop()
        if currSong == 0:
            currSong = len(playList) - 1
        else:
            currSong-=1
        song = playList[currSong]
        mixer.music.load(song)
        time.sleep(1)
        mixer.music.play()
        canvas.itemconfig(song_name,text=os.path.basename(song))
        playBtn.place_forget()
        pauseBtn.place(x=153,y=330)
        pause = False
        isNewSong = False
        totaltime()
    except:
        messagebox.showerror('File Not Found', 'Could not find file to play. Please check again')
            
previous_icon = Image.open("icons/previous button.png")
previous_icon = previous_icon.resize((18,18))
previous_icon = ImageTk.PhotoImage(previous_icon)
previousBtn = Button(root,image = previous_icon,borderwidth=0,bg='#5f6d62',command=previous)
previousBtn.place(x=122,y=338)


less_volume_icon = Image.open("icons/lessvolume.png")
less_volume_icon = less_volume_icon.resize((10,10))
less_volume_icon  = ImageTk.PhotoImage(less_volume_icon)
lessVLabel = Label(root,image=less_volume_icon,borderwidth=0)
lessVLabel.place(x=60,y=376)



full_volume_icon = Image.open("icons/fullvolume.png")
full_volume_icon = full_volume_icon.resize((12,12))
full_volume_icon  = ImageTk.PhotoImage(full_volume_icon)
fullVLabel = Label(root,image=full_volume_icon,borderwidth=0)
fullVLabel.place(x=260,y=375)


def forward():
    global currTimeLength,totalTimeLength,song 
    csong = song
    while currTimeLength <= totalTimeLength-5 and csong==song:
        if not(pause):
            currTimeLength += 5
            mins, secs = divmod(currTimeLength, 60)
            currentformat = '{:02d} : {:02d}'.format(mins,secs)
            curr_time['text'] = currentformat
            song_bar.set(currTimeLength)
            mixer.music.set_pos(currTimeLength)
            break

forward_icon = Image.open("icons/forward.png")
forward_icon = forward_icon.resize((18,22))
forward_icon = ImageTk.PhotoImage(forward_icon)
forwardBtn = Button(root,image = forward_icon,borderwidth=0,bg='#5f6d62',command=forward)
forwardBtn.place(x=228,y=336)

def backward():
    global currTimeLength,totalTimeLength,song 
    csong = song
    while currTimeLength >= 5 and csong==song:
        if not(pause):
            currTimeLength -= 5
            mins, secs = divmod(currTimeLength, 60)
            currentformat = '{:02d} : {:02d}'.format(mins,secs)
            curr_time['text'] = currentformat
            song_bar.set(currTimeLength)
            mixer.music.set_pos(currTimeLength)
            break

backward_icon = Image.open("icons/backward.png")
backward_icon = backward_icon.resize((18,21))
backward_icon = ImageTk.PhotoImage(backward_icon)
backwardBtn = Button(root,image = backward_icon,borderwidth=0,bg='#5f6d62',command=backward)
backwardBtn.place(x=91,y=337)


'''menu and its functions'''
def browsefile(event=None):
    global playList,pause, song,isNewSong,currSong
    playList=[]
    filename = filedialog.askopenfilename(initialdir = os.getcwd(), title = 'Select File', filetypes = (('Audio Files', '*.mp3'), ('Audio Files', '*.wav'), ('Audio Files', '*.ogg')))
    playList.insert(0,filename)
    currSong=0
    song = filename
    mixer.music.load(filename)
    mixer.music.play()
    canvas.itemconfig(song_name,text=os.path.basename(song))
    playBtn.place_forget()
    pauseBtn.place(x=153,y=330)
    pause = False
    isNewSong = False
    totaltime()

def browsefiles():
    global playList,isNewSong,song,pause,currSong
    playList=[]
    currSong=0
    multiple_filename_path = filedialog.askopenfilenames(initialdir = os.getcwd(), title = 'Select Files', filetypes = (('Audio Files', '*.mp3'), ('Audio Files', '*.wav'), ('Audio Files', '*.ogg')))
    for i in range(len(multiple_filename_path)):
        playList.insert(i, multiple_filename_path[i])
    song=playList[0]
    try:
        mixer.music.load(song)
        mixer.music.play()
        canvas.itemconfig(song_name,text=os.path.basename(song))
        playBtn.place_forget()
        pauseBtn.place(x=153,y=330)
        pause = False
        isNewSong = False
        totaltime()
    except:
        messagebox.showerror('File Not Found','select song to play')
    
def openFolder():
    global playList,isNewSong,song,pause,currSong
    dirname_path = filedialog.askdirectory(initial = os.getcwd(), title = 'Select Folder')
    dirname = list(os.listdir(dirname_path))
    playList=[]
    currSong=0
    for i in range(len(dirname)):
        if dirname[i].endswith(".mp3") or dirname[i].endswith(".wav") or dirname[i].endswith(".ogg"):
            r = os.path.join(dirname_path, dirname[i])
            playList.insert(i, r)
    song=playList[0]
    mixer.music.load(song)
    mixer.music.play()
    canvas.itemconfig(song_name,text=os.path.basename(song))
    playBtn.place_forget()
    pauseBtn.place(x=153,y=330)
    pause = False
    isNewSong = False
    totaltime()
    

file_icon = PhotoImage(file="icons/file.png")
folder_icon = PhotoImage(file="icons/folder.png")
menu = Menu()

file_menu = Menu(menu,tearoff=False)
menu.add_cascade(label='File',menu=file_menu)

file_menu.add_command(label='Open File',image = file_icon,compound=LEFT,command= browsefile)
file_menu.add_command(label='Open Multiples Files',image=file_icon,compound=LEFT,command=browsefiles)
file_menu.add_command(label='Open Folder',image=folder_icon,compound=LEFT,command=openFolder)

root.config(menu= menu)

root.mainloop()

mixer.music.stop()
