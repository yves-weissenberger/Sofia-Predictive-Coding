from __future__ import division
import numpy.random as rnd
import RPi.GPIO as GPIO
import multiprocessing as billiard
import csv
import requests as req
import sys
import pygame
from pygame.locals import *
import numpy as np
import random
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


rewL = 35
rewR = 37
GPIO.setup(rewL,GPIO.OUT) #Output pin specified; used to deliver rewards
GPIO.setup(rewR,GPIO.OUT)


solOpenDur = 0.03 #Really? Really short reward delivery window...
sound_dur=0.4
minILI=0.05 #Minimum interlick interval in seconds; needed to calculate licking frequency

# Reward Delivery Helper Functions 

def deliverRew(channel):

    rewstart=time.time()
    while time.time()<= rewstart+solOpenDur:
        GPIO.output(channel,1)
   
    GPIO.output(channel,0)

rewProcL= billiard.Process(target=deliverRew,args=(rewL,))
rewProcR=billiard.Process(target=deliverRew, args=(rewR,))

def data_sender (lickLst,rewLst, sendT): #Modify here since I have more than two entries in each string

        lickStr = 'LickList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + entry[1] for entry in lickLst])
        rewStr = 'rewList:' + '-'.join([str(np.round(entry[0],decimals=3))+ ' ' + entry[1] for entry in rewLst])
        sendStr = ', '.join([rewStr,lickStr])
                    
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

gameDisplay=pygame.display.set_mode((800, 480),pygame.FULLSCREEN)

pygame.init()

#Initialising lists for licks

lickLst = [] #Gonna fill the first column with timings, second column with lick side
rewLst = []


lickT = time.time()
prevL = time.time()
start = time.time()
sendT = time.time()

licknumL=0
licknumR=0

while time.time() <= start+2700: #This makes for 45 minutes of training

    if (time.time()-sendT> 5): #Basically, if 5 seconds have elapsed since the last data_send, then call on that function
                               #and update the contents of the strings
        lickLst,rewLst = data_sender(lickLst,rewLst,sendT)    


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
   
                
    if (GPIO.event_detected(lickR)): 
                
        if (time.time()-prevL)>minILI:
            lickT = time.time()
            licknumR = licknumR + 1 
            lickLst.append ([lickT-start, '' + str('RL')]) 
            prevL = time.time()
            rewProcR.start()
            rewT = time.time() - start 
            rewLst.append([rewT, '' + str('RR')])

        else:
            prevL = time.time()
            
                        

    if (GPIO.event_detected(lickL)): 
        if (time.time()-prevL)>minILI:
            lickT = time.time()
            licknumR = licknumL + 1 
            lickLst.append ([lickT-start, '' + str('LL')]) 
            prevL = time.time()
            rewProcL.start()
            rewT = time.time() - start
            rewLst.append([rewT, '' + str('LR')])

        else:
            prevL = time.time()
            

                
#lickLst=np.array(lickLst)
#lickLst=np.concatenate((lickLst[0],lickLst[1]),axis=1) #Now, say I want the timing of the fifth trial. Type print lickLst [4][0]
#rewLst=np.array(rewLst) 
#print LickLst
#print rewLst 

Clock.tick(FPS)             
pygame.quit()
quit()

