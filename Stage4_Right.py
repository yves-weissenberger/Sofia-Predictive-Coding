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

print "I'm online :-)"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(33,GPIO.IN) #These four are the input pins receiving TTLs from the first RPi. 
GPIO.setup(31,GPIO.IN)
GPIO.setup(29,GPIO.IN)
GPIO.setup(15,GPIO.IN) 
GPIO.setup(23,GPIO.IN)
GPIO.setup(21,GPIO.IN)
GPIO.setup(19,GPIO.IN)
GPIO.setup(26,GPIO.IN)
GPIO.setup(40,GPIO.IN)

GPIO.add_event_detect(33,GPIO.RISING)
GPIO.add_event_detect(31,GPIO.RISING)
GPIO.add_event_detect(29,GPIO.RISING)
GPIO.add_event_detect(15,GPIO.RISING)
GPIO.add_event_detect(23,GPIO.RISING)
GPIO.add_event_detect(21,GPIO.RISING)
GPIO.add_event_detect(19,GPIO.RISING)
GPIO.add_event_detect(40,GPIO.RISING)
GPIO.add_event_detect(26,GPIO.RISING)
punishment_delay = 5

BLACK= (0,0,0)
GRAY=(127,127,127)
grey_rect=pygame.Rect(160,0,480,480)


gameDisplay=pygame.display.set_mode((800, 480))#,pygame.FULLSCREEN)
changex=4
freq=6 #Originally 18. There is a MATLAB script named sine_experiment in the Matlabcourse folder where you can adjust the parameters in trying to identify the best frequency to pick. Use it.
stim_dur=5
greyscreen_dur=2
refresh_rate = 0.05 #originally 0.05
cue_period = 2
contrast_var=0.6 #ADJUST BASED ON EACH MOUSE'S 75% CORRECT PERFORMANCE THRESHOLD


#MAKING GRATINGS

h_gab=[] #Horizontal sine wave array, to be filled
v_gab=[] #Vertical sine wave array


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

h_gab=np.array(h_gab)
v_gab=h_gab.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings


print "Done with generating gratings"


surface_maker=0
h_surf_list = []
v_surf_list = []

while surface_maker<=39: #Now the first half of the elements will be horizontal gabors (with 100% contrast)
                            
    h_surface = pygame.surfarray.make_surface(h_gab[surface_maker])
    h_surf_list.append([h_surface])
    v_surface = pygame.surfarray.make_surface(v_gab[surface_maker])
    v_surf_list.append([v_surface])
    print "Making a surface"
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

making_noise_frames=0
noise_frame_list=[]

while making_noise_frames <=39:

    Noise=pygame.surfarray.make_surface(destroyed_gratings[making_noise_frames])
    noise_frame_list.append([Noise])
    making_noise_frames+=1


print "Finished making noise video"


start=time.time()


while time.time()<=start+3600 #An hour

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
                

    if GPIO.event_detected(15): 
        
        startmoment = time.time()
        finishmoment = startmoment+stim_dur
        frame_num=0   #Gonna go through the frames containing the vertical sine
                          #gratings (after the 102nd element in the all_gabors array)
        x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating)

        while time.time()<=finishmoment:
                
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

            if GPIO.event_detected(26):

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

            
    if GPIO.event_detected(23):
            
        startmoment = time.time()
        finishmoment = startmoment+stim_dur
        frame_num=0 #Gonna go through the frames containing the vertical sine
                      #gratings (after the 102nd element in the all_gabors array)
        x=0 #This variable is going to increase by one at every iteration of the time loop below. I will multiply it by the refresh period of 50 msec every iteration to get an update on the screen (needed for moving sine grating) 

        while time.time()<= finishmoment:
                
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
                frame_num=0

            if GPIO.event_detected(26):

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


    if GPIO.event_detected(40):

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


            if GPIO.event_detected(26):

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
 

        
  

                    
    
   

                          




