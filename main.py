import pygame
from pygame.locals import *
import sys
import numpy as np
from util import * 
import random
from face_detection import FaceDetectionThread

false = False
true = True
asdp = [false, false, false, false]

face_detection_thread = FaceDetectionThread(0, True)
try:
    # Start the face detection thread
    face_detection_thread.start()
    face_detection_thread.reset_initial_position()
except KeyboardInterrupt:
    # Stop the face detection thread on keyboard interrupt
    face_detection_thread.stop()

#positions = left, right, middle
#actions = punching, resting

class Character():
    def __init__(self):
        self.xpos = 0 #range (-.5) - (.5)
        self.healthPoints = DEFAULT_HP
        self.action = REST
        self.cooldown = 0
        self.positionTime = 0 #how long your character has been in the same positionpygame.time.get_ticks()

    def update(self, newxpos, newAction): # reads the action and position from CV and uses them to update the player
        currentTime = pygame.time.get_ticks()
        self.xpos = newxpos # updates position (no cooldown)
       
        if newAction == REST:
            self.action = REST
        else: #new action = punch
            if self.cooldown <= 0:
                self.action = PUNCH
                self.cooldown = DEFAULT_PUNCH_CD
            else:
                self.action = REST

        self.previousTime = currentTime
        

#game objects
enemyChar = Character()
youChar = Character()

testplayerpos = 0

def isPunch():
    if asdp[3] == 1:
        return PUNCH
    else:
        return REST
    # To be integrated with CV (deez nuts)
    return false

def playerPosition():
    face_offset = face_detection_thread.get_face_x_offset()
    if face_offset == 0:
        return youChar.xpos
    return np.clip(face_offset, -0.5, +0.5)

 
def enemyAction(): # done
    if enemyChar.cooldown <= 0 and abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE and youChar.positionTime >= (8+random.random()*15):
        enemyChar.cooldown=DEFAULT_PUNCH_CD
        return PUNCH
    return REST

def enemyPos(): 
    funnevariable = enemyChar.xpos
    if enemyChar.positionTime>=12+random.random()*13: #humble them with a reaction 
        if abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE: #if in same range currently
            if youChar.cooldown< DEFAULT_PUNCH_CD * .4 and enemyChar.cooldown>=DEFAULT_PUNCH_CD*.5: #if it senses punch incoming and has been in space longer than reaction time
                funnevariable+=(random.random()-.5)*.1 #move by a random amount in either direction
        else:
            if (enemyChar.cooldown < DEFAULT_PUNCH_CD *.4): #if punch cooldown is low and distance is far awayish then go closer
                if (youChar.xpos<enemyChar.xpos):
                    funnevariable-=.1
                else:
                    funnevariable+=.1
    if (funnevariable>.5):
        funnevariable =.5
    elif funnevariable<-.5:
        funnevariable=-.5
    return funnevariable #maintain curr position

def periodicEnemyPos(t):
    value = 0

    # Set up parameters for the function
    sin_frequencies = [-21, 41]
    sin_amplitudes = [.17, .07]
    cos_frequencies = [31, -51]
    cos_amplitudes = [.12, .14]

    for i in range(len(sin_frequencies)):
        value += sin_amplitudes[i] * np.sin(sin_frequencies[i] * t)

    for i in range(len(cos_frequencies)):
        value += cos_amplitudes[i] * np.cos(cos_frequencies[i] * t)

    return value

pygame.init()
pygame.display.set_caption("Test")
display_size = (500, 500)
screen = pygame.display.set_mode(display_size)
font = pygame.font.Font("freesansbold.ttf", 32)
# bg = pygame.image.load("GunnHacks10/bgbg.png")

DT_SHIFT = 10
FPS = 60
ANIMATION_DT = 1000
gameClock = pygame.time.Clock()
ticks = 0
dt = 1

uistate = GAME

def update(frameTime, uistate):
    global ticks

    dt = frameTime >> DT_SHIFT
    ticks += 1
    #playerpos = playerBodyPosition()

    if uistate == MENU:
        #update current state
        if (punching): #TOO: add transition
            uistate=GAME
        #update ui
    elif uistate == GAME:
        youChar.cooldown-=frameTime
        enemyChar.cooldown-=frameTime
        if  abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE: #position time is checking how long they're within range now
            enemyChar.positionTime+=frameTime
            youChar.positionTime+=frameTime
        youChar.update(playerPosition(), isPunch())
        enemyChar.update(periodicEnemyPos(ticks / 700), enemyAction())
        
        # print(enemyChar.xpos)
        
        #hit detection
        if  abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE: #do the thingggggggg
            if youChar.action == PUNCH:
                enemyChar.healthPoints-=1
                if enemyChar.healthPoints<=0:
                    uiState=GAMEOVER
            if enemyChar.action ==PUNCH:
                youChar.healthPoints-=1
                if youChar.healthPoints<=0:
                    uiState=GAMEOVER
        #key detection

        #update UI - bottom: HP
        # print(youChar.cooldown, enemyChar.cooldown, youChar.xpos, enemyChar.xpos, asdp)
        pygame.draw.circle(screen, (255,0,0), (enemyChar.xpos * display_size[0] + (display_size[0] / 2), 200), 25) #may not work
        pygame.draw.circle(screen, (0,255,0), (youChar.xpos * display_size[0] + (display_size[0] / 2), 400), 25)
    elif uistate == GAMEOVER:
        #display gameover screen

        if isPunch:
            uiState=MENU
    
    else:
        pass #noop
while True:
    screen.fill((0,0,0))
    # screen.blit(bg, (0,0))
    asdp[0] = False; asdp[1] = False; asdp[2] = False; asdp[3] = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_a:
                testplayerpos=0
            if event.key == K_s:
                testplayerpos=1
            if event.key == K_d:
                testplayerpos=2
            if event.key == K_p:
                asdp[3] = True
    frameTime = gameClock.tick(FPS)
    update(dt, uistate)
    pygame.display.flip()