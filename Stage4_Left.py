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
from random import shuffle
import os
import time 

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
contrast_var= 0.6 #ADJUST BASED ON INDIVIDUAL MOUSE'S 75% THRESHOLD AT STAGE 3

# Reward Delivery Helper Functions 

def deliverRew(channel):

    rewstart=time.time()
    while time.time()<= rewstart+solOpenDur:
        GPIO.output(channel,1)
   
    GPIO.output(channel,0)

rewProcL= billiard.Process(target=deliverRew,args=(rewL,))
rewProcR=billiard.Process(target=deliverRew, args=(rewR,))


def sendpulse(channel):
    pulsestart=time.time()
    
    while time.time()<=pulsestart+0.05:
        GPIO.output(channel,1)
    GPIO.output(channel,0)
    

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

def data_sender (lickLst,rewLst,orientation, location, sendT): #Modify here since I have more than two entries in each string

        lickStr = 'LickList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + str(np.round(entry[1],decimals=3))+ ' ' + str(np.round(entry[2],decimals=3))+ ' ' + entry[3] + ' ' + entry[4] for entry in lickLst])
        rewStr = 'rewList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + str(np.round(entry[1],decimals=3))+ ' ' + str(np.round(entry[2],decimals=3))+ ' ' + entry[3] for entry in rewLst])
        locStr = 'Location:' + '-'.join([str(np.round(location,decimals=3))])
        orStr= 'Orientation:' + '-'.join([str(np.round(orientation,decimals=3))])
        sendStr = ', '.join([rewStr,lickStr,locStr,orStr])
                    
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


gameDisplay=pygame.display.set_mode((800, 480)) #,pygame.FULLSCREEN
changex=4
freq=6 #Originally 18. There is a MATLAB script named sine_experiment in the Matlabcourse folder where you can adjust the parameters in trying to identify the best frequency to pick. Use it.
stim_dur=5
greyscreen_dur=2
refresh_rate = 0.05 #originally 0.05
cue_period = 2
#Defining trial structure

Location = []
Orientation = []
location = []
orientation = []
Location_Array = []
Orientation_Array = [] 

block_repeats=1

while block_repeats <=18:

    t_perblock=1
    
    while t_perblock<=10:
        
        if t_perblock<=9:
            
            Location = random.randrange(1,3) #Location
            Orientation = random.randrange(3,5) #Orientation
            Location_Array.append(Location)
            Orientation_Array.append(Orientation)
            t_perblock+=1
            
        elif t_perblock == 10: #Once every ten times that a trial condition is picked, I want an invalid condition to be picked.
                               #Even though now, the invalid condition is always the last to be picked in a block of 10 trials,
                               #I will shuffle the contents of each block before concatenating the 18 of them into a single block of 180 trials.

            Location = random.randrange(1,3) # Location, works the same on invalid trials.
            Orientation = random.randrange(6,8) #This will represent the two types of invalidly cued trials.
                                                #7 = aud_cueH incorrect, 8 = aud_cueV incorrect.
            Location_Array.append(Location)
            Orientation_Array.append(Orientation)
            t_perblock+=1

    block_repeats+=1

shuffle (Location_Array)
shuffle(Orientation_Array)
Location_Array = np.array(Location_Array)
Orientation_Array = np.array(Orientation_Array)

#MAKING GRATINGS

h_gab=[] #Horizontal sine wave array, to be filled
v_gab=[] #Vertical sine wave array

print "Currently making gratings"

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

    horizontal_sine= (np.sin(sinexgrid*freq)) * contrast_var
    hgabor = horizontal_sine * gaussian   
    hgabor = ((hgabor+1)/2*255).astype('uint8')  
    hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
    h_gab.append(hgabor)
   

    x+=changex
    j+=1


h_gab.append(hgabor)    
h_gab=np.array(h_gab)
v_gab=h_gab.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

surface_maker=0
h_surf_list = []
v_surf_list = []

while surface_maker<=39: 
    
    h_surface = pygame.surfarray.make_surface(h_gab[surface_maker])
    h_surf_list.append([h_surface])
    v_surface = pygame.surfarray.make_surface(v_gab[surface_maker])
    v_surf_list.append([v_surface])
    surface_maker+=1


# MAKING THE NOISE VIDEO

print "Making noise video now"

noise_movie_frames=0
destroyed_gratings=[]
gaussianinputs= np.linspace(-np.pi, np.pi,480)
[gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)
gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2



while noise_movie_frames <=39:

    randomisation = 0
    pixels = np.linspace(np.pi,3*np.pi,480) 
    [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
    destroyedgabor= (np.sin(sinexgrid*15)) * contrast_var #*contrast_var originally and freq instead of 15

    while randomisation <=479:

        destroyedgabor [randomisation] [0:480] = np.random.permutation(destroyedgabor[randomisation] [0:480])
        destroyedgabor [0:480] [randomisation] = np.random.permutation(destroyedgabor [0:480][randomisation])
        randomisation+=1

    destroyedgabor = destroyedgabor * gaussian
    destroyedgabor = ((destroyedgabor+1)/2*255).astype('uint8')  
    destroyedgabor = destroyedgabor[..., None].repeat(3, -1).astype("uint8")
    destroyed_gratings.append(destroyedgabor)
    noise_movie_frames+=1


destroyed_gratings = np.array(destroyed_gratings)
print destroyed_gratings.shape

making_noise_frames=0
noise_frame_list=[]

while making_noise_frames <=39:

    Noise=pygame.surfarray.make_surface(destroyed_gratings[making_noise_frames])
    noise_frame_list.append([Noise])
    making_noise_frames+=1


print "Finished making noise video"

#MAKING AUDITORY CUES NOW

pygame.mixer.pre_init(96000,-16,1,4096) #if jitter, change 256 to different value
pygame.init()

sR = 96000 #Sampling rate
cue_dur = 0.4 # Duration of auditory cue
max16bit = 32766

aud_cues = np.zeros((1,2)) 
aud_cues [0] [0] = 20 * 10**2
aud_cues [0] [1] = 5 * 10**2 

making_sounds=0
aud_cueH = []
aud_cueV = []

print "Making sounds now"

while making_sounds <=1:

    def gensin(frequency=aud_cues [0][making_sounds], duration= cue_dur, sampRate = sR, edgeWin = 0.01):

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
    
    if making_sounds==0:
        
        aud_cueH = snd_Audio
     
    elif making_sounds==1:
        
        aud_cueV = snd_Audio #np.concatenate((snd_Arr,snd_Audio),axis=0)
    
    making_sounds+=1

print "Sounds done"


#Initialising data lists for licks and tones


lickLst = [] #[trial number] [lick time relative to start of task]
                         #[lick time relative to stimulus onset] [lick location: R/L] [Correct/Incorrect]
rewLst = [] #[trial number] [relative to stimulus onset] [reward side]


sendT = time.time() #Not sure if these three should be just at the start of the trial counter or outside of it...
lickT = time.time()
prevL = time.time()
start = time.time()
counter = 0

while counter <=179:

    orientation = Orientation_Array [counter]
    location = Location_Array [counter]

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
                    
    if Location_Array [counter] == 1:

        if Orientation_Array [counter] == 3: #Right side, vertical 

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
                    aud_cueV.play()

                    #Pulses should be sent here because this screen is meant to contain greyscreen
                    #while the other RPi should be getting a pulse to trigger grating presentation

            sendpulse(15)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            making_noise_frames=0
            x=0
            

            while time.time() <= finishmoment:


                gameDisplay.blit(noise_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

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

        elif Orientation_Array [counter] == 7: #Right side, vertical, INVALID prediction by cue

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
                    aud_cueH.play()

                    #Pulses should be sent here because this screen is meant to contain greyscreen
                    #while the other RPi should be getting a pulse to trigger grating presentation

            sendpulse(15)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur

            making_noise_frames=0
            x=0
            
            while time.time() <= finishmoment:


                gameDisplay.blit(noise_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

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
                            
                
                if (GPIO.event_detected(lickR)): #I need the mice to withhold responding.
                                                 #ALL responses are punished with a break
                                
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Response on no-go trial')])
                        prevL = time.time()
                        punish_pulse(26) 
                                        
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
                            

                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                         lickT = time.time()
                         licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                         lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Response on no-go trial')])
                         punish_pulse(26) 

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

        elif Orientation_Array [counter] == 4:

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
                    aud_cueH.play()

            sendpulse(23)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            making_noise_frames=0
            x=0
            

            while time.time() <= finishmoment:


                gameDisplay.blit(noise_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

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
                                          

        elif Orientation_Array [counter] == 6: #Horizontal grating, INVALID prediction by auditory cue

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
                    aud_cueV.play()

            sendpulse(23)
            startmoment = time.time()
            finishmoment = startmoment+stim_dur

            making_noise_frames=0
            x=0
            
            while time.time() <= finishmoment:


                gameDisplay.blit(noise_frame_list[making_noise_frames][0],((160,0))) #Originally second value was [0]

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

                if (GPIO.event_detected(lickR)): #I need the mice to withhold responding.
                                                 #ALL responses are punished with a break
                                
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Response on no-go trial')])
                        prevL = time.time()
                        punish_pulse(26) 
                                        
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
                            

                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                     if (time.time()-prevL)>minILI:
                          lickT = time.time()
                          licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                          lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Response on no-go trial')])
                          punish_pulse(26) 
                         
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
   


    elif Location_Array [counter] == 2:

        if Orientation_Array [counter] == 3: #Let's make this the left, vertical


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
                    aud_cueV.play()

            grey_screenpulse(40) 
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            frame_num=0 #Gonna go through the frames containing the vertical sine
                              #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine gratinfor event in pygame.event.get(): 

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

                gameDisplay.blit(v_surf_list[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

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


        elif Orientation_Array [counter] == 7: # Vertical grating, invalid prediction by auditory cue

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
                    aud_cueH.play()

            grey_screenpulse(40) 
            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            
            frame_num=0 #Gonna go through the frames containing the vertical sine
                              #gratings (after the 102nd element in the all_gabors array)
            x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine gratinfor event in pygame.event.get(): 

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

                gameDisplay.blit(v_surf_list[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                         
                     pygame.display.update()
                     frame_num+=1
                     x+=1

                if frame_num ==40:
                    frame_num=0


                if (GPIO.event_detected(lickR)): #I need the mice to withhold responding.
                                                 #ALL responses are punished with a break
                                
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Response on no-go trial')])
                        prevL = time.time()
                        punish_pulse(26) 
                                        
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
                            

                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Response on no-go trial')])
                        punish_pulse(26) 


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

                                             
        elif Orientation_Array [counter] == 4: #Horizontal grating, valid auditory cue

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
                    aud_cueH.play()

            grey_screenpulse(40)
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

                gameDisplay.blit(h_surf_list[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

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
                        prevL = time.time()


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

                                                                         
        elif Orientation_Array [counter] == 6: #Horizontal grating, invalid auditory cue


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
                    aud_cueV.play()

            grey_screenpulse(40)
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

                gameDisplay.blit(h_surf_list[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

                if time.time()>= startmoment+(x*refresh_rate):
                     
                    pygame.display.update()
                    frame_num+=1
                    x+=1

                if frame_num ==40:
                    frame_num = 0


                if (GPIO.event_detected(lickR)): #I need the mice to withhold responding.
                                                 #ALL responses are punished with a break
                                
                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumR = licknumR + 1 
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('RL'), ''+str ('Response on no-go trial')])
                        prevL = time.time()
                        punish_pulse(26) 
                                        
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
                            

                if (GPIO.event_detected(lickL)): #Incorrect side. Punishment by timeout before next trial?

                    if (time.time()-prevL)>minILI:
                        lickT = time.time()
                        licknumL = licknumL + 1 #Figure out where to initialise this variable. It's just a lick counter
                        lickLst.append([counter,lickT-start,lickT-startmoment,'' +str('LL'), ''+str ('Response on no-go trial')])
                        punish_pulse(26) 

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


#lickLst=np.array(lickLst)
#lickLst=np.concatenate((lickLst[0],lickLst[1],lickLst[2],lickLst[3],lickLst[4]),axis=1)
#rewLst=np.array(rewLst)
#rewLst=np.concatenate((rewLst[0],rewLst[1],rewLst[2]),axis=1)
#print lickLst
#print rewLst
#print Task_Matrix
                                     
        
for event in pygame.event.get(): 
    if event.type == KEYUP:
        if event.key == K_ESCAPE:
            task = False 
            pygame.quit()
    elif event.type == KEYUP:
        if event.key == K_ESCAPE:
            task = False
            pygame.quit() 



Clock.tick(FPS)
pygame.quit()
quit()

