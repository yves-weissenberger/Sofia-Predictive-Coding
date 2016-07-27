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

gameDisplay=pygame.display.set_mode((800, 480))#,pygame.FULLSCREEN
changex=4
freq=6 #Originally 18. There is a MATLAB script named sine_experiment in the Matlabcourse folder where you can adjust the parameters in trying to identify the best frequency to pick. Use it.
stim_dur=5
greyscreen_dur=2
refresh_rate = 0.05 #originally 0.05
cue_period = 2


contrast_var_ar = np.array([0, 1, 0.6, 0.8, 0.2, 0.4]) #The 0 is pointless, it's just a placeholder in the array


h_gab100=[]
h_gab80=[]
h_gab60=[]
h_gab40=[]
h_gab20=[] #Horizontal sine wave arrays of different contrast values, to be filled
v_gab100=[]
v_gab80=[]
v_gab60=[]
v_gab40=[]
v_gab20=[] #Horizontal sine wave arrays of different contrast values, to be filled

for c in range (1,6):

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

                    horizontal_sine= (np.sin(sinexgrid*freq)) * contrast_var_ar [c]
                    hgabor = horizontal_sine * gaussian   
                    hgabor = ((hgabor+1)/2*255).astype('uint8')  
                    hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                    h_gab100.append(hgabor)
                   

                    x+=changex
                    j+=1

                h_gab100=np.array(h_gab100)
                v_gab100=h_gab100.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==2:

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

                    horizontal_sine= (np.sin(sinexgrid*freq)) * contrast_var_ar [c]
                    hgabor = horizontal_sine * gaussian   
                    hgabor = ((hgabor+1)/2*255).astype('uint8')  
                    hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                    h_gab60.append(hgabor)
                   

                    x+=changex
                    j+=1

                h_gab60=np.array(h_gab60)
                v_gab60=h_gab60.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==3:

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

                    horizontal_sine= (np.sin(sinexgrid*freq)) * contrast_var_ar [c]
                    hgabor = horizontal_sine * gaussian   
                    hgabor = ((hgabor+1)/2*255).astype('uint8')  
                    hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                    h_gab80.append(hgabor)
                   

                    x+=changex
                    j+=1

                h_gab80=np.array(h_gab80)
                v_gab80=h_gab80.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==4:

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

                    horizontal_sine= (np.sin(sinexgrid*freq)) * contrast_var_ar [c]
                    hgabor = horizontal_sine * gaussian   
                    hgabor = ((hgabor+1)/2*255).astype('uint8')  
                    hgabor = hgabor[..., None].repeat(3, -1).astype("uint8")
                    h_gab20.append(hgabor)
                   

                    x+=changex
                    j+=1

                h_gab20=np.array(h_gab20)
                v_gab20=h_gab20.transpose(0,2,1,3) #Transpose the horizontal grating matrix to create vertical gratings

        elif c==5:

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

                    horizontal_sine= (np.sin(sinexgrid*freq)) * contrast_var_ar [c]
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
    
    print "Making a surface"
    surface_maker+=1

# MAKING NOISE VIDEO
print "Making noise video now"

destroyed_gratings100=[]
destroyed_gratings80=[]
destroyed_gratings60=[]
destroyed_gratings40=[]
destroyed_gratings20=[]

gaussianinputs= np.linspace(-np.pi, np.pi,480)
[gaussxgrid,gaussygrid] = np.meshgrid(gaussianinputs, gaussianinputs)
gaussian = np.exp(-(gaussxgrid/2)**2-(gaussygrid/2)**2) #originally grids divided by 2

       
for c in range (1,6):

    if c ==1: #Different contrast values in the task_structure vector

        noise_movie_frames=0
        print "Making noise video at 100% contrast now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*contrast_var_ar[c]  #*contrast_var originally and freq instead of 15

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


    elif c==2:

        noise_movie_frames=0
        print "Making noise video at 60% contrast now"
       
        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*contrast_var_ar[c]  #*contrast_var originally and freq instead of 15

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


    elif c==3:

        noise_movie_frames=0
        print "Making noise video at 80% contrast now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*contrast_var_ar[c]  #*contrast_var originally and freq instead of 15

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
            
    elif c==4:

        noise_movie_frames=0
        print "Making noise video at 20% contrast now"
        
        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*contrast_var_ar[c]  #*contrast_var originally and freq instead of 15

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

    elif c==5:

        noise_movie_frames=0
        print "Making noise video at 40% contrast now"

        while noise_movie_frames <=39:

            randomisation = 0
            pixels = np.linspace(np.pi,3*np.pi,480) 
            [sinexgrid, sineygrid] = np.meshgrid(pixels, pixels)
            destroyedgabor= (np.sin(sinexgrid*15))*contrast_var_ar[c]  #*contrast_var originally and freq instead of 15

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

    

pygame.init()
start=time.time()


while time.time() <= start+3600:

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

    if (GPIO.event_detected(15)) and (GPIO.event_detected(32)) and (GPIO.event_detected(31)):

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

                gameDisplay.blit(v_surf_list100[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

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


    if (GPIO.event_detected(15)) and (GPIO.event_detected(31)) and (GPIO.event_detected(29)):
            
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


    if (GPIO.event_detected(15)) and (GPIO.event_detected(29)) and (GPIO.event_detected(23)):

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

            
    if (GPIO.event_detected(15)) and (GPIO.event_detected(23)) and (GPIO.event_detected(21)):
            
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


            
    if (GPIO.event_detected(15)) and (GPIO.event_detected(21)) and (GPIO.event_detected(19)):

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



    if (GPIO.event_detected(33)) and (GPIO.event_detected(32)) and (GPIO.event_detected(31)):

            startmoment = time.time()
            finishmoment = startmoment+stim_dur
            frame_num=0   #Gonna go through the frames containing the vertical sine
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


    if (GPIO.event_detected(33)) and (GPIO.event_detected(31)) and (GPIO.event_detected(29)):
            
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


    if (GPIO.event_detected(33)) and (GPIO.event_detected(29)) and (GPIO.event_detected(23)):

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

    if (GPIO.event_detected(33)) and (GPIO.event_detected(23)) and (GPIO.event_detected(21)):
            
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

                gameDisplay.blit(h_surf_list20[frame_num][0],((160,0))) # Originally 4 and 10 for 300 x 300 pixel size matrix

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


            
    if (GPIO.event_detected(33)) and (GPIO.event_detected(21)) and (GPIO.event_detected(19)):

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
                    

    if (GPIO.event_detected(23)) and (GPIO.event_detected(15)) and (GPIO.event_detected(33)):

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

                                    
    if (GPIO.event_detected(23)) and (GPIO.event_detected(15)) and (GPIO.event_detected(32)):


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


    if (GPIO.event_detected(23)) and (GPIO.event_detected(29)) and (GPIO.event_detected(21)):


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


    if (GPIO.event_detected(23)) and (GPIO.event_detected(19)) and (GPIO.event_detected(31)):

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


    if (GPIO.event_detected(23)) if (GPIO.event_detected(29)) and (GPIO.event_detected(31)):

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



                    
    
   

                          




