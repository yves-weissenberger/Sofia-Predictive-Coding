from __future__ import division
import numpy.random as rnd
import RPi.GPIO as GPIO
import csv
import requests as req
import sys
import pygame
from pygame.locals import *
import numpy as np
import random
import os
import time 
import multiprocessing as billiard
print "Im online :)"

# Data sending function

pi_IP = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
pi_ID = str(int(pi_IP[-3:])-100) 

def send_data(load):

    headers = {'User-Agent': 'Mozilla/5.0'}
    link = 'http://192.168.0.99:8000/getData/' + pi_ID + '/get_PiData/'

    session = req.Session()
    r1 = session.get(link,headers=headers)

    link1 = 'http://192.168.0.99:8000/getData/' + pi_ID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       + '/write_PiData/'


    payload = {'piData':load,'csrfmiddlewaretoken':r1.cookies['csrftoken']}
    #cookies = dict(session.cookies)
    session.post(link1,headers=headers,data=payload)
    return None


# Setup RPi.GPIO 

GPIO.setmode(GPIO.BOARD)


lickL = 36 #Input channel wired up to the left licking spout
lickR = 38 #Input channel wired up to the right spout
GPIO.setup(lickL,GPIO.IN) #Input pin receiving voltage change resulting from lick
GPIO.setup(lickR,GPIO.IN)
GPIO.add_event_detect(lickL,GPIO.RISING) 
GPIO.add_event_detect(lickR,GPIO.RISING)


#The pins I'm using to send a pulse to the second RPi to trigger the presentation of the other stimulus.
GPIO.setup(33,GPIO.OUT)
GPIO.setup(31,GPIO.OUT)
GPIO.setup(29,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(40,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(32,GPIO.OUT)


solOpenDur = 0.03 #Really? Really short reward delivery window...
rewL = 35
rewR = 37
GPIO.setup(rewL,GPIO.OUT) #Output pin specified; used to deliver rewards
GPIO.setup(rewR,GPIO.OUT)
sound_dur=0.4
minILI=0.05 #Minimum interlick interval in seconds; needed to calculate licking frequency
punishment_delay = 5

# Reward Delivery Helper Functions 

def deliverRew(channel):

    rewstart=time.time()
    while time.time()<= rewstart+solOpenDur:
        GPIO.output(channel,1)
   
    GPIO.output(channel,0)

rewProcL= billiard.Process(target=deliverRew,args=(rewL,))
rewProcR=billiard.Process(target=deliverRew, args=(rewR,))


def sendpulse(f_channel,s_channel,t_channel):
    pulsestart=time.time()
    
    while time.time()<=pulsestart+0.05:
        GPIO.output(f_channel,1)
        GPIO.output(s_channel,1)
        GPIO.output(t_channel,1) 
        
    GPIO.output(f_channel,0)
    GPIO.output(s_channel,0)
    GPIO.output(t_channel,0)

def grey_screenpulse(channel):
    pulsestart=time.time()
    while time.time()<=pulsestart+0.05:
        GPIO.output(channel,1)
    GPIO.output(channel,0)

def punish_pulse(channel):
    pulsestart=time.time()
    while time.time()<=pulsestart+0.05:
        GPIO.output(channel,1)
    GPIO.output(channel,0)

def data_sender (lickLst,rewLst,orientation, location, contrast, sendT): #Modify here since I have more than two entries in each string

        lickStr = 'LickList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + str(np.round(entry[1],decimals=3))+ ' ' + str(np.round(entry[2],decimals=3))+ ' ' + entry[3] + ' ' + entry[4] for entry in lickLst])
        rewStr = 'rewList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + str(np.round(entry[1],decimals=3))+ ' ' + str(np.round(entry[2],decimals=3))+ ' ' + entry[3] for entry in rewLst])
        locStr = 'Location:' + '-'.join([str(np.round(location,decimals=3))])
        orStr= 'Orientation:' + '-'.join([str(np.round(orientation,decimals=3))])
        conStr = 'Contrast:' + '-'.join([str(np.round(contrast,decimals=3))])
        sendStr = ', '.join([rewStr,lickStr,locStr,orStr,conStr])
                    
        sendProc = billiard.Process(target=send_data,args=(sendStr,))
        sendProc.start()
        print 'seeeeeending'
        #send_data(sendStr)
        sendT = time.time()
        lickLst = []; rewLst = []; #No need to empty / update the location/orientation values
                                   #these will be updated at the start of each trial
        return lickLst,rewLst,sendT



#Defining my visual stimuli and task parameters

timeout = 0.1 # Every 100 msec, trial frequency

FPS =30
Clock= pygame.time.Clock()

BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
grey_rect=pygame.Rect(160,0,480,480)

gameDisplay=pygame.display.set_mode((800, 480))#,pygame.FULLSCREEN
changex=4
freq=6 #Originally 18. There is a MATLAB script named sine_experiment in the Matlabcourse folder where you can adjust the parameters in trying to identify the best frequency to pick. Use it.
#ppx=173 #grating period in pixels
stim_dur=5
greyscreen_dur=2
refresh_rate = 0.05 #originally 0.05
cue_period = 2


# CONTRAST BLOCKS

contrast_var_ar = np.array([1, 0.6, 1, 0.8, 1, 0.2, 1, 0.4, 1]) 
[output1,output2] = np.meshgrid(contrast_var_ar, contrast_var_ar) #Output1 organises all the trials of the same contrast values into columns
task_structure=np.ones((20))
task_structure=np.array([task_structure])
task_structure= task_structure.T
i=1

while i <=8: #This is just to create a long vector of 180 trials, with each 20 trial block presenting a particular stimulus contrast 
    
    output= np.array([output1[:,i]]) 
    output = output.T   
    task_structure=np.concatenate((task_structure, output,output,output[0:2]), axis=0)
    i+=1

print "Done with contrast array"

#MAKING GRATINGS


h_gab100=[]
h_gab80=[]
h_gab60=[]
h_gab40=[]
h_gab20=[] #Horizontal sine wave arrays of different contrast values, to be filled
v_gab100=[]
v_gab80=[]
v_gab60=[]
v_gab40=[]
v_gab20=[] #Vertical sine wave arrays of different contrast values, to be filled

for c in range (1,180):

        if c==1:

            print "Currently making gratings at 100% contrast"
            j=0
            x=0

            while j <=38: #Horizontal grating, originally made 100 meshgrids (j going from 0 to <=100, but smaller number is preferable because of memory allocation issues on the RPpi).              

                pixels = np.linspace(np.pi+x,3*np.pi+x,480) 
                [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
                gaussianinputs= np.linspace(-np.pi, np.pi,480)
                [gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)

                # Gaussian : mean = 0, std = 1, amplitude = 1 
                gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

                # Sine wave grating : orientation = 0, phase = 0, amplitude = 1, frequency = 10/(2*pi) 

                horizontal_sine= (np.sin(sinexgrid*freq)) * task_structure [c]
                hgabor = horizontal_sine * gaussian   
                hgabor = ((hgabor+1)/2*255).astype('uint8')  
                hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                h_gab100.append(hgabor)
               

                x+=changex
                j+=1

            h_gab100=np.array(h_gab100)
            v_gab100=h_gab100.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==20:

            print "Currently making gratings at 60% contrast"
            j=0
            x=0

            while j <=38: #Horizontal grating, originally made 100 meshgrids (j going from 0 to <=100, but smaller number is preferable because of memory allocation issues on the RPpi).              

                pixels = np.linspace(np.pi+x,3*np.pi+x,480) 
                [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
                gaussianinputs= np.linspace(-np.pi, np.pi,480)
                [gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)

                # Gaussian : mean = 0, std = 1, amplitude = 1 
                gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

                # Sine wave grating : orientation = 0, phase = 0, amplitude = 1, frequency = 10/(2*pi) 

                horizontal_sine= (np.sin(sinexgrid*freq)) * task_structure [c]
                hgabor = horizontal_sine * gaussian   
                hgabor = ((hgabor+1)/2*255).astype('uint8')  
                hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                h_gab60.append(hgabor)
               

                x+=changex
                j+=1

            h_gab60=np.array(h_gab60)
            v_gab60=h_gab60.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==60:

            print "Currently making gratings at 80% contrast"
            j=0
            x=0

            while j <=38: #Horizontal grating, originally made 100 meshgrids (j going from 0 to <=100, but smaller number is preferable because of memory allocation issues on the RPpi).              

                pixels = np.linspace(np.pi+x,3*np.pi+x,480) 
                [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
                gaussianinputs= np.linspace(-np.pi, np.pi,480)
                [gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)

                # Gaussian : mean = 0, std = 1, amplitude = 1 
                gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

                # Sine wave grating : orientation = 0, phase = 0, amplitude = 1, frequency = 10/(2*pi) 

                horizontal_sine= (np.sin(sinexgrid*freq)) * task_structure [c]
                hgabor = horizontal_sine * gaussian   
                hgabor = ((hgabor+1)/2*255).astype('uint8')  
                hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                h_gab80.append(hgabor)
               

                x+=changex
                j+=1

            h_gab80=np.array(h_gab80)
            v_gab80=h_gab80.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==100:

            print "Currently making gratings at 20% contrast"

            j=0
            x=0

            while j <=38: #Horizontal grating, originally made 100 meshgrids (j going from 0 to <=100, but smaller number is preferable because of memory allocation issues on the RPpi).              

                pixels = np.linspace(np.pi+x,3*np.pi+x,480) 
                [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
                gaussianinputs= np.linspace(-np.pi, np.pi,480)
                [gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)

                # Gaussian : mean = 0, std = 1, amplitude = 1 
                gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

                # Sine wave grating : orientation = 0, phase = 0, amplitude = 1, frequency = 10/(2*pi) 

                horizontal_sine= (np.sin(sinexgrid*freq)) * task_structure [c]
                hgabor = horizontal_sine * gaussian   
                hgabor = ((hgabor+1)/2*255).astype('uint8')  
                hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                h_gab20.append(hgabor)
               

                x+=changex
                j+=1

            h_gab20=np.array(h_gab20)
            v_gab20=h_gab20.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==140:

            print "Currently making gratings at 40% contrast"
            j=0
            x=0

            while j <=38: #Horizontal grating, originally made 100 meshgrids (j going from 0 to <=100, but smaller number is preferable because of memory allocation issues on the RPpi).              

                pixels = np.linspace(np.pi+x,3*np.pi+x,480) 
                [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
                gaussianinputs= np.linspace(-np.pi, np.pi,480)
                [gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)

                # Gaussian : mean = 0, std = 1, amplitude = 1 
                gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

                # Sine wave grating : orientation = 0, phase = 0, amplitude = 1, frequency = 10/(2*pi) 

                horizontal_sine= (np.sin(sinexgrid*freq)) * task_structure [c]
                hgabor = horizontal_sine * gaussian   
                hgabor = ((hgabor+1)/2*255).astype('uint8')  
                hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                h_gab40.append(hgabor)
               

                x+=changex
                j+=1

            h_gab40=np.array(h_gab40)
            v_gab40=h_gab40.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

print "Done with generating gratings"

surface_maker=0
h_surf_list100=[]
h_surf_list80=[]
h_surf_list60=[]
h_surf_list40=[]
h_surf_list20=[]
v_surf_list100=[]
v_surf_list80=[]
v_surf_list60=[]
v_surf_list40=[]
v_surf_list20=[]

while surface_maker<=39: #Now the first half of the elements will be horizontal gabors (with the contrast values
                           #1, 0.6, 0.8, 0.2 and 0.4 in order), last half vertical, with the same contrast values in the same order.

    
    h_surface100 = pygame.surfarray.make_surface(h_gab100[surface_maker])
    h_surf_list100.append([h_surface100])
    h_surface80 = pygame.surfarray.make_surface(h_gab80[surface_maker])
    h_surf_list80.append([h_surface80])
    h_surface60 = pygame.surfarray.make_surface(h_gab60[surface_maker])
    h_surf_list60.append([h_surface60])
    h_surface40 = pygame.surfarray.make_surface(h_gab40[surface_maker])
    h_surf_list40.append([h_surface40])
    h_surface20 = pygame.surfarray.make_surface(h_gab20[surface_maker])
    h_surf_list20.append([h_surface20])
    v_surface100 = pygame.surfarray.make_surface(v_gab100[surface_maker])
    v_surf_list100.append([v_surface100])
    v_surface80 = pygame.surfarray.make_surface(v_gab80[surface_maker])
    v_surf_list80.append([v_surface80])
    v_surface60 = pygame.surfarray.make_surface(v_gab60[surface_maker])
    v_surf_list60.append([v_surface60])
    v_surface40 = pygame.surfarray.make_surface(v_gab40[surface_maker])
    v_surf_list40.append([v_surface40])
    v_surface20 = pygame.surfarray.make_surface(v_gab20[surface_maker])
    v_surf_list20.append([v_surface20])
    
    surface_maker+=1

# MAKING NOISE VIDEO

print "Making noise videos now"

destroyed_gratings100=[]
destroyed_gratings80=[]
destroyed_gratings60=[]
destroyed_gratings40=[]
destroyed_gratings20=[]

gaussianinputs= np.linspace(-np.pi, np.pi,480)
[gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)
gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

       
for c in range (1,180):

    if c ==1: #Different contrast values in the task_structure vector

        noise_movie_frames=0
        print "Making 100% contrast noise now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*task_structure[c]  #*contrast_var originally and freq instead of 15

            while randomisation <=479:

                destroyedgabor [randomisation] [0:480] = np.random.permutation(destroyedgabor[randomisation] [0:480])
                destroyedgabor [0:480] [randomisation] = np.random.permutation(destroyedgabor [0:480][randomisation])
                randomisation+=1
                
            destroyedgabor = destroyedgabor * gaussian   
            destroyedgabor = ((destroyedgabor+1)/2*255).astype('uint8')  
            destroyedgabor = destroyedgabor[..., None].repeat(3, -1).astype("uint8")
            destroyed_gratings100.append(destroyedgabor)
            noise_movie_frames+=1


        destroyed_gratings100 = np.array(destroyed_gratings100)


    elif c==20:

        noise_movie_frames=0
        print "Making 60% contrast noise now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*task_structure[c]  #*contrast_var originally and freq instead of 15

            while randomisation <=479:

                destroyedgabor [randomisation] [0:480] = np.random.permutation(destroyedgabor[randomisation] [0:480])
                destroyedgabor [0:480] [randomisation] = np.random.permutation(destroyedgabor [0:480][randomisation])
                randomisation+=1
                
            destroyedgabor = destroyedgabor * gaussian   
            destroyedgabor = ((destroyedgabor+1)/2*255).astype('uint8')  
            destroyedgabor = destroyedgabor[..., None].repeat(3, -1).astype("uint8")
            destroyed_gratings60.append(destroyedgabor)
            noise_movie_frames+=1


        destroyed_gratings60 = np.array(destroyed_gratings60)


    elif c==60:

        noise_movie_frames=0
        print "Making 80% contrast noise now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*task_structure[c]  #*contrast_var originally and freq instead of 15

            while randomisation <=479:

                destroyedgabor [randomisation] [0:480] = np.random.permutation(destroyedgabor[randomisation] [0:480])
                destroyedgabor [0:480] [randomisation] = np.random.permutation(destroyedgabor [0:480][randomisation])
                randomisation+=1
                
            destroyedgabor = destroyedgabor * gaussian   
            destroyedgabor = ((destroyedgabor+1)/2*255).astype('uint8')  
            destroyedgabor = destroyedgabor[..., None].repeat(3, -1).astype("uint8")
            destroyed_gratings80.append(destroyedgabor)
            noise_movie_frames+=1


        destroyed_gratings80 = np.array(destroyed_gratings80)
            
    elif c==100:

        noise_movie_frames=0
        print "Making 20% contrast noise now"
        
        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*task_structure[c]  #*contrast_var originally and freq instead of 15

            while randomisation <=479:

                destroyedgabor [randomisation] [0:480] = np.random.permutation(destroyedgabor[randomisation] [0:480])
                destroyedgabor [0:480] [randomisation] = np.random.permutation(destroyedgabor [0:480][randomisation])
                randomisation+=1
                
            destroyedgabor = destroyedgabor * gaussian   
            destroyedgabor = ((destroyedgabor+1)/2*255).astype('uint8')  
            destroyedgabor = destroyedgabor[..., None].repeat(3, -1).astype("uint8")
            destroyed_gratings20.append(destroyedgabor)
            noise_movie_frames+=1


        destroyed_gratings20 = np.array(destroyed_gratings20)

    elif c==140:
        
        noise_movie_frames=0
        print "Making 40% contrast noise now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*task_structure[c]  #*contrast_var originally and freq instead of 15

            while randomisation <=479:

                destroyedgabor [randomisation] [0:480] = np.random.permutation(destroyedgabor[randomisation] [0:480])
                destroyedgabor [0:480] [randomisation] = np.random.permutation(destroyedgabor [0:480][randomisation])
                randomisation+=1
                
            destroyedgabor = destroyedgabor * gaussian   
            destroyedgabor = ((destroyedgabor+1)/2*255).astype('uint8')  
            destroyedgabor = destroyedgabor[..., None].repeat(3, -1).astype("uint8")
            destroyed_gratings40.append(destroyedgabor)
            noise_movie_frames+=1


        destroyed_gratings40 = np.array(destroyed_gratings40)
        

making_noise_frames=0

noise100_frame_list=[]
noise80_frame_list=[]
noise60_frame_list=[]
noise40_frame_list=[]
noise20_frame_list=[]


while making_noise_frames <=39:

    Noise100=pygame.surfarray.make_surface(destroyed_gratings100[making_noise_frames])
    Noise80=pygame.surfarray.make_surface(destroyed_gratings80[making_noise_frames])
    Noise60=pygame.surfarray.make_surface(destroyed_gratings60[making_noise_frames])
    Noise40=pygame.surfarray.make_surface(destroyed_gratings40[making_noise_frames])
    Noise20=pygame.surfarray.make_surface(destroyed_gratings20[making_noise_frames])

    
    noise100_frame_list.append([Noise100])
    noise80_frame_list.append([Noise80])
    noise60_frame_list.append([Noise60])
    noise40_frame_list.append([Noise40])
    noise20_frame_list.append([Noise20])
    making_noise_frames+=1

print "Noise video finished"

#Making the auditory cues

pygame.mixer.pre_init(96000,-16,1,4096) #if jitter, change 256 to different value
pygame.init()

sR = 96000 #Sampling rate
cue_dur = 0.4 # Duration of auditory cue
max16bit = 32766

aud_cue = 7 * 10**3 

print "MAKING AUDITORY TRIAL CUE NOW"

def gensin(frequency=aud_cue, duration= cue_dur, sampRate = sR, edgeWin = 0.01):

    cycles = np.linspace
    cycles = np.linspace(0,duration*2*np.pi,num=duration*sampRate)
    wave = np.sin(cycles*frequency, dtype='float32')
    
    #smooth sine wave at the edges
    numSmoothSamps = int(edgeWin*sR)
    wave[0:numSmoothSamps] = wave[0:numSmoothSamps] * np.cos(np.pi*np.linspace(0.5,1,num=numSmoothSamps))**2
    wave[-numSmoothSamps:] = wave[-numSmoothSamps:] * np.cos(np.pi*np.linspace(1,0.5,num=numSmoothSamps))**2
    wave = np.round(wave*max16bit)
    
    return wave.astype('int16')

sndArray=gensin()
snd_Audio = pygame.sndarray.make_sound(sndArray)
aud_cue=snd_Audio

print "Sound done"


#Initialising data lists for licks and tones

contrast=[]
location=[]
orientation=[]
Location_Array=[]
Orientation_Array = []



lickLst = [] #[trial number] [lick time relative to start of task]
                         #[lick time relative to stimulus onset] [lick location: R/L] [Correct/Incorrect]
rewLst = [] #[trial number] [relative to stimulus onset] [reward side]

lickT = time.time()
prevL = time.time()
sendT = time.time()
start = time.time()
counter = 0

while counter <=179:
    
    contrast= task_structure [counter]
    location = random.randrange(1,3) #Location
    orientation = random.randrange(3,5) #Orientation
    Location_Array.append(location)
    Orientation_Array.append(orientation)

    if (time.time()-sendT> 5): #Basically, if 5 seconds have elapsed since the last data_send, then call on that function
                               #and update the contents of the strings
        lickLst,rewLst,orientation,location,contrast,sendT = data_sender(lickLst,rewLst,orientation,location,contrast,sendT)    
 
    
    gameDisplay.fill(BLACK)
    pygame.draw.rect(gameDisplay,GRAY,grey_rect)
    pygame.display.update()

    for event in pygame.event.get(): 
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                task = False 
                pygame.quit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                task = False
                pygame.quit() 
                    
    if Location_Array [counter] == 1 and Orientation_Array [counter] == 3: #Right side, vertical 

    
        licknumL=0
        licknumR=0

        cue_start=time.time()

        while time.time()<=cue_start+cue_period:
            
            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
            pygame.display.update()
        
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()

            if time.time()>=cue_start+0.6 and time.time()<=cue_start+1:
                aud_cue.play()

                #Pulses should be sent here because this screen is meant to contain greyscreen
                #while the other RPi should be getting a pulse to trigger grating presentation

        if task_structure [counter] == 1:

            sendpulse(15,32,31)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise100_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

        
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()
                
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])

                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26) 
                        print "Incorrect response"

            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                             

        elif task_structure [counter] == 0.6:

            sendpulse(15,31,29)
            
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise60_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()
                
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewprocr.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"

            

            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                         
                     
        elif task_structure [counter] == 0.8:

            sendpulse (15,29,23)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise80_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()
                            
                
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time()  
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"


            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                         
                     
        elif task_structure [counter] == 0.2:

            sendpulse(15,23,21)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise20_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"
                  

            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()     
                     
        else:

            sendpulse(15,21,19)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
  
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise40_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()


                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() 
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"
                    

            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect)#when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit() 
                                    

        startmoment = time.time()
        finishmoment = startmoment+greyscreen_dur
      
        while time.time() <= finishmoment:     

            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
            pygame.display.update()
        
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()

        
        counter+=1
   

    elif Location_Array [counter] == 1 and Orientation_Array [counter] == 4:
        

        licknumL=0
        licknumR=0

        cue_start=time.time()

        while time.time()<=cue_start+cue_period:
            
            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
            pygame.display.update()
        
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()

            if time.time()>=cue_start+0.6 and time.time()<=cue_start+1:
                aud_cue.play()
        
        if task_structure [counter]== 1:
            
            sendpulse(33,32,31)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise100_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0
                
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

  
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"

            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                         

        elif task_structure [counter] == 0.6:

            sendpulse(33,31,29)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise60_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()
                            
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"


            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                         
                     
        elif task_structure [counter] == 0.8:

            sendpulse(33,29,23)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise80_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"


            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                         
                     
        elif task_structure [counter] == 0.2:

            sendpulse(33,23,21)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur

            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise20_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                                   
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()
                
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"


            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                         
                     
        else:

            sendpulse(33,21,19)

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0

            while time.time() <= finishmoment:

                gameDisplay.blit(noise40_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

                if time.time()>=start+(x*refresh_rate): 

                    pygame.display.update()
                    making_noise_frames+=1
                    x+=1
                if making_noise_frames ==40:
                    making_noise_frames=0

                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

    
                if (GPIO.event_detected(lickR)): #Right lick - correct side; rewarded
                            
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocr = billiard.Process(target=deliverRew,args=(rewR,))
                        rewProcR.start()
                        #deliverRew(rewR)
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('RR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Incorrect')])
                        prevL = time.time()
                        punish_pulse(26)
                        print "Incorrect response"

                        
            #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                        startmoment = time.time()
                        finishmoment = startmoment+punishment_delay


                        while time.time() <= finishmoment:
            
                             gameDisplay.fill(BLACK)
                             pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                             pygame.display.update()
            
                             for event in pygame.event.get(): 
                                 if event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False 
                                         pygame.quit()
                                 elif event.type == KEYUP:
                                     if event.key == K_ESCAPE:
                                         task = False
                                         pygame.quit()
                                             
                                         
        startmoment = time.time()
        finishmoment = startmoment+greyscreen_dur
       
        while time.time() <= finishmoment:     

            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect) 
            pygame.display.update()
          
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()
                        
        counter+=1


    elif Location_Array [counter] == 2 and Orientation_Array [counter] == 3: #Let's make this the left, vertical


        licknumL=0
        licknumR=0
 
        cue_start=time.time()

        while time.time()<=cue_start+cue_period:
            
            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
            pygame.display.update()
        
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()

            if time.time()>=cue_start+0.6 and time.time()<=cue_start+1:
                aud_cue.play()

        if task_structure [counter] == 1:

            sendpulse(23,15,33)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                        #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(v_surf_list100[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num=0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 


        elif task_structure [counter] == 0.6:

            sendpulse(23,15,32) 
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(v_surf_list60[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1
                     
                if frame_num ==40:
                    frame_num=0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

                     
        elif task_structure [counter] == 0.8:

            sendpulse(23,29,21)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating) 
            
            while time.time() <= finishmoment:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(v_surf_list80[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num == 40:
                    frame_num=0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

                     
        elif task_structure [counter] == 0.2:

            sendpulse(23,19,31)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(v_surf_list20[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1
                     
                if frame_num ==40:
                    frame_num=0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

                     
        else: 

            sendpulse(23,29,31)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(v_surf_list40[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num = 0

    
                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                    
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

        startmoment = time.time()
        finishmoment = startmoment+greyscreen_dur

                        
        while time.time() <= finishmoment:     

            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect) 
            pygame.display.update()
        
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()
          
        counter+=1

    else: #Let's make this left, horizontal


        licknumL=0
        licknumR=0

        cue_start=time.time()

        while time.time()<=cue_start+cue_period:
            
            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
            pygame.display.update()
        
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()

            if time.time()>=cue_start+0.6 and time.time()<=cue_start+1:
                aud_cue.play()

        
        if task_structure [counter] == 1:

            sendpulse(23,15,33)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(h_surf_list100[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num = 0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 


        elif task_structure [counter] == 0.6:

            sendpulse(23,15,32)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(h_surf_list60[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num = 0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

                     
        elif task_structure [counter] == 0.8:

            sendpulse(23,29,21)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(h_surf_list80[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num = 0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"

                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect)#when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

                     
        elif task_structure [counter] == 0.2:

            sendpulse(23,19,31)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num= 0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <=finishmoment: 
                
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(h_surf_list20[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num=0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 

                     
        else:

            sendpulse(23,29,31)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0 #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

            while time.time() <= finishmoment:
                                         
                for event in pygame.event.get(): 
                    if event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False 
                            pygame.quit()
                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            task = False
                            pygame.quit()

                gameDisplay.blit(h_surf_list40[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num = 0

                if (GPIO.event_detected(lickL)): #Left lick - correct side; rewarded
                        
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Correct')])
                        prevL = time.time()
                        print "Correct response detected"

                        #rewprocl = billiard.Process(target=deliverRew,args=(rewL,))
                        rewProcL.start()
                        #deliverRew(rewL) 
                        rewT = time.time() #Time elapsed since grating onset and reward OR ASK YVES IF MORE USEFUL TO COLLECT TIMINGS RELATIVE TO THE ORIGINAL START OF THE EXPERIMENT RATHER THAN TRIAL
                        rewLst.append([counter, rewT-start, rewT-startmoment,'' +str('LR')])
                        print "Reward delivered"
                        
                    else:
                        prevL = time.time() #ASK YVES WHY YOU'D WANT TO RESET THE TIMER IN CASE OF A PREMATURE LICK...


                if (GPIO.event_detected(lickR)): #Incorrect side. Punishment by timeout before next trial?

                   if (time.time()-prevL)>minILI:
                       lickT = time.time()
                       licknumR = licknumR + 1 #Figure out where to initialise this variable. It's just a lick counter
                       lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Incorrect')])
                       prevL= time.time()
                       punish_pulse(26)
                       print "Incorrect response"
                       
                       
                       #punishment for incorrect spout - grey screen and delay of 5 secs before next trial onset

                       startmoment = time.time()
                       finishmoment = startmoment+punishment_delay


                       while time.time() <= finishmoment:
            
                            gameDisplay.fill(BLACK)
                            pygame.draw.rect(gameDisplay,GRAY,grey_rect) #when movie finishes, replace with blank grey screen for 2 seconds
                            pygame.display.update()
            
                            for event in pygame.event.get(): 
                                if event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False 
                                        pygame.quit()
                                elif event.type == KEYUP:
                                    if event.key == K_ESCAPE:
                                        task = False
                                        pygame.quit() 


                
        startmoment = time.time()
        finishmoment = startmoment+greyscreen_dur

                
        while time.time() <= finishmoment:     

            gameDisplay.fill(BLACK)
            pygame.draw.rect(gameDisplay,GRAY,grey_rect)
            pygame.display.update()
          
            for event in pygame.event.get(): 
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False 
                        pygame.quit()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        task = False
                        pygame.quit()
                        
        counter+=1
        
for event in pygame.event.get(): 
    if event.type == KEYUP:
        if event.key == K_ESCAPE:
            task = False 
            pygame.quit()
    elif event.type == KEYUP:
        if event.key == K_ESCAPE:
            task = False
            pygame.quit() 


#lickLst=np.array(lickLst)
#lickLst=np.concatenate((lickLst[0],lickLst[1],lickLst[2],lickLst[3],lickLst[4]),axis=1)
#rewLst=np.array(rewLst)
#rewLst=np.concatenate((rewLst[0],rewLst[1],rewLst[2]),axis=1)
#print "LickLst"
#print lickLst
#print "rewLst" 
#print rewLst
Orientation_Array = np.array(Orientation_Array)
print "Orientations"
print Orientation_Array
Location_Array = np.array(Location_Array) 
print "Locations"
print Location_Array


Clock.tick(FPS)
pygame.quit()
quit()

