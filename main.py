import pygame
from pygame.locals import *
import sys
import numpy as np
from util import * 
import random
from camera import FrameCapturer
from face_detection import FaceDetectionThread
from punch_detection import HandPunchDetector

false = False
true = True
asdp = [false, false, false, false]
difficulty = EASY # high number: less difficult
# 2000: easy
# 1300: medium
# 700: hard

frame_capturer = FrameCapturer(camera_index=0)

hand_punch_detector = HandPunchDetector(frame_capturer=frame_capturer)
face_detection_thread = FaceDetectionThread(frame_capturer=frame_capturer)
try:
    # Start the face detection thread
    hand_punch_detector.start()
    face_detection_thread.start()
    face_detection_thread.reset_initial_position()
except KeyboardInterrupt:
    # Stop the face detection thread on keyboard interrupt
    face_detection_thread.stop()
    hand_punch_detector.stop()
    frame_capturer.stop()


#positions = left, right, middle
#actions = punching, resting
class physicsObj():
    def __init__(self):
        self.imagePath = ""
        self.pos = (0,0)
        self.velocity = (0,0)
        self.acceleration = (0,0)
    def setInit(self, newImg, newPos,newVelocity, newAccl):
        self.imagePath=newImg
        self.pos=newPos
        self.velocity=newVelocity
        self.acceleration=newAccl
    def update(self):
        self.pos[0]+=self.velocity[0] * ticks/TICK_PHYSICS_MULTIPLIER
        self.pos[1]+=self.velocity[1]* ticks/TICK_PHYSICS_MULTIPLIER
        self.velocity[0]+=self.acceleration[0]* ticks/TICK_PHYSICS_MULTIPLIER
        self.velocity[1]+=self.acceleration[1]* ticks/TICK_PHYSICS_MULTIPLIER
    def display(self):
        if self.imagePath == "": return
        screen.blit(self.imagePath, (self.pos[0],self.pos[1]))
        
class Character():
    def __init__(self):
        self.isAllied = 1
        self.xpos = 0 #range (-.5) - (.5)
        self.healthPoints = ALLIED_HP
        self.action = REST
        self.cooldown = 0
        self.positionTime = 0 #how long your character has been in the same positionpygame.time.get_ticks()
    def setInitState (self,alliedState, Health):
        self.isAllied=alliedState
        self.healthPoints=Health
    def update(self, newxpos, newAction): # reads the action and position from CV and uses them to update the player
        currentTime = pygame.time.get_ticks()
        self.xpos = newxpos # updates position (no cooldown)
        if newAction == REST:
            self.action = REST
        else: #new action = punch
            if self.cooldown <= 0:
                self.action = PUNCH
                if(self.isAllied):
                    self.cooldown = ALLIED_COOLDOWN
                else:
                    self.cooldown = ENEMY_COOLDOWN
            else:
                self.action = REST

        self.previousTime = currentTime
        

#game objects
enemyChar = Character()
youChar = Character()
enemyChar.setInitState(false,ENEMY_HP)
youChar.setInitState(true,ALLIED_HP)

testplayerpos = 0

def isPunch():
    return hand_punch_detector.is_punching

def playerPosition():
    face_offset = face_detection_thread.get_face_x_offset()
    if face_offset == 0:
        return youChar.xpos
    return np.clip(face_offset, -0.5, +0.5)

 
def enemyAction(): # done
    if enemyChar.cooldown <= 0 and abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE and youChar.positionTime >= (ENEMY_GODLINESS_BASE+random.random()+3):
        return PUNCH
    return REST





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
    #return enemyChar.xpos

pygame.init()
pygame.display.set_caption("XORcise")
display_size = (1280, 720)
screen = pygame.display.set_mode(display_size)
font32 = pygame.font.Font("freesansbold.ttf", 32)
font24 = pygame.font.Font("freesansbold.ttf", 24)
gamebg = pygame.image.load("bgbgbg.png")

if difficulty == EASY:
    midimg, midimgsize = image_load_downscale("0_1_Idle.png", 7)
    mpg, mpgs = image_load_downscale("0_1_Punch.png", 7)
    leftimg, leftimgsize = image_load_downscale("0_0_Idle.png", 7)
    lpg, lpgs = image_load_downscale("0_0_Punch.png", 7)
    rightimg, rightimgsize = image_load_downscale("0_2_Idle.png", 7)
    rpg, rpgs = image_load_downscale("0_2_Punch.png", 7)
elif difficulty == MEDIUM:
    midimg, midimgsize = image_load_downscale("1_1_Idle.png", 7)
    mpg, mpgs = image_load_downscale("1_1_Punch.png", 7)
    leftimg, leftimgsize = image_load_downscale("1_0_Idle.png", 7)
    lpg, lpgs = image_load_downscale("1_0_Punch.png", 7)
    rightimg, rightimgsize = image_load_downscale("1_2_Idle.png", 7)
    rpg, rpgs = image_load_downscale("1_2_Punch.png", 7)
elif difficulty == HARD:
    midimg, midimgsize = image_load_downscale("2_1_Idle.png", 7)
    mpg, mpgs = image_load_downscale("2_1_Punch.png", 7)
    leftimg, leftimgsize = image_load_downscale("2_0_Idle.png", 7)
    lpg, lpgs = image_load_downscale("2_0_Punch.png", 7)
    rightimg, rightimgsize = image_load_downscale("2_2_Idle.png", 7)
    rpg, rpgs = image_load_downscale("2_2_Punch.png", 7)


player_idle_1_img, player_idle_1_img_size = image_load_downscale("playeridle1.png", 12)
player_idle_2_img, player_idle_2_img_size = image_load_downscale("playeridle2.png", 12)
player_punch_img, player_punch_img_size = image_load_downscale("playerpunch.png", 12)

hitimg, hitimgsize = image_load_downscale("hit.png", 1)
missimg, missimgsize = image_load_downscale("miss.png", 1)

music = pygame.mixer.music.load("sounds/musicbetter.wav")
pygame.mixer.music.play(-1)

bell_sound = pygame.mixer.Sound("sounds/bell.wav")

punch_sounds = [
    pygame.mixer.Sound("sounds/punch1.wav"),
    pygame.mixer.Sound("sounds/punch2.wav"),
    pygame.mixer.Sound("sounds/punch3.wav"),
    pygame.mixer.Sound("sounds/punch4.wav"),
    pygame.mixer.Sound("sounds/punch5.wav"),
]

hit_sounds = [
    pygame.mixer.Sound("sounds/hit1.wav"),
    pygame.mixer.Sound("sounds/hit2.wav"),
    pygame.mixer.Sound("sounds/hit3.wav"),
]

DT_SHIFT = 10
FPS = 60
ANIMATION_DT = 1000
gameClock = pygame.time.Clock()
ticks = 0
dt = 1
punchAnimating = false
enemypunching = false
enemypunchanit = 0
punchAnimatingt = 0

hitIcons = []
missIcons = []

uistate = MENU

def update(frameTime):
    
    # if isPunch():
    #     print("PUNCH!")
    global ticks, punchAnimating, punchAnimatingt, enemypunching, enemypunchanit, uistate

    dt = frameTime >> DT_SHIFT
    ticks += 1
    #playerpos = playerBodyPosition()

    if uistate == MENU:
        text = font32.render("XORcise VIRTUAL BOXING", True, (255,0,0))
        text2 = font24.render("Punch to get started!", True, (255,0,0))
        textRect = text.get_rect()
        text2Rect = text2.get_rect()
        textRect.center = (display_size[0] // 2, display_size[1] // 2+90)
        text2Rect.center = (display_size[0] // 2, display_size[1] // 2 + 150)
        screen.blit(text, textRect)
        screen.blit(text2, text2Rect)
        #update current state
        #if currently calibrating, wait

        if (isPunch()): #TOO: add transition
            bell_sound.play()
            uistate=GAME 
        #update ui
    elif uistate == GAME:
        for i in hitIcons:
            if (i.pos[1]>display_size[1] or i.pos[1]<0):
                hitIcons.remove(i)
                
            else:
                i.update()
                i.display()

        for i in missIcons:
            if (i.pos[1]>display_size[1]):
                missIcons.remove(i)
            else:
                i.update()
                i.display()
        youChar.cooldown-=frameTime
        enemyChar.cooldown-=frameTime
        if  abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE: #position time is checking how long they're within range now
            enemyChar.positionTime+=frameTime
            youChar.positionTime+=frameTime
        else:
            enemyChar.positionTime==0
            youChar.positionTime==0
        youChar.update(playerPosition(), PUNCH if isPunch() else REST)
        enemyChar.update(periodicEnemyPos(ticks / difficulty), enemyAction())
        
        # print(enemyChar.xpos)
        #hit detection
        if youChar.cooldown==ALLIED_COOLDOWN:
            if youChar.action == PUNCH:
                punchAnimating = True
                punchAnimatingt = 50
                random.choice(punch_sounds).play()

                if abs(enemyChar.xpos-youChar.xpos)<=ALLIED_HIT_RANGE:
                    random.choice(hit_sounds).play()

                    enemyChar.healthPoints-=1
                    toAppend = physicsObj()
                    #print("hitobj")
                    toAppend.setInit(hitimg,[(enemyChar.xpos+.5)*display_size[0],10+random.random()*15],[1+random.random()*2,-1 -random.random()], [0,1])
                    hitIcons.append(toAppend)
                    if enemyChar.healthPoints<=0:
                        uiState=GAMEOVER
            else:
                toAppend = physicsObj()
                # print("missobj")
                toAppend.setInit(missimg,[(youChar.xpos+.5)*display_size[0],10+random.random()*15],[(random.random()-.5)*2.5,-1.25], [0,-1])
                missIcons.append(toAppend)
        if enemyChar.cooldown==ENEMY_COOLDOWN:
            if enemyChar.action == PUNCH:
                enemypunching = True
                enemypunchanit = 50
                if abs(enemyChar.xpos-youChar.xpos)<=ENEMY_TARGET_RANGE:
                    youChar.healthPoints-=1
                    # print("hitobj")
                    toAppend = physicsObj()
                    toAppend.setInit(hitimg,[(youChar.xpos+.5)*display_size[0],display_size[1]*.75+random.random()*5],[2*(random.random()-.5),-2+random.random()*1], [0,1+random.random()*.5])
                    hitIcons.append(toAppend)
                if youChar.healthPoints<=0:
                        uiState=GAMEOVER
            else:
                # print("missobj")
                toAppend = physicsObj()
                toAppend.setInit(missimg,[(enemyChar.xpos+.5)*display_size[0],display_size[1]*.75+random.random()*5],[1.5*(random.random()-.5),-1+random.random()*1], [0,1+random.random()*.5])
                missIcons.append(toAppend)
        
        if youChar.action == PUNCH:
            punchAnimating = True
            punchAnimatingt = 50
        if punchAnimating and punchAnimatingt > 0:
            punchAnimatingt -= 1
        if punchAnimatingt <= 0:
            punchAnimating = False
        if enemyChar.action == PUNCH:
            enemypunching = True
            enemypunchanit = 50
        if enemypunching and enemypunchanit > 0:
            enemypunchanit -= 1
        if enemypunchanit <= 0:
            enemypunching = False

        #key detection

        #update UI - bottom: HP
        pygame.draw.rect(screen,(255,0,0),(display_size[0]*.1,0, display_size[0]*.8*(enemyChar.healthPoints)/ENEMY_HP,display_size[1]*.05))
        
        pygame.draw.rect(screen,(0,0,255),(0,display_size[1]*.2, display_size[0]*.05,display_size[1]*(max(0,youChar.cooldown)/ALLIED_COOLDOWN)))

        pygame.draw.rect(screen,(0,255,0),(display_size[0]*.1,display_size[1]*.90, display_size[0]*.8*(youChar.healthPoints)/ALLIED_HP,display_size[1]*.1)) #your healthbar
        # print(youChar.cooldown, enemyChar.cooldown, youChar.xpos, enemyChar.xpos, asdp)
        # print(youChar.healthPoints, enemyChar.healthPoints, youChar.cooldown, enemyChar.cooldown)
        # pygame.draw.circle(screen, (255,0,0), (enemyChar.xpos * display_size[0] + (display_size[0] / 2), 200), 25) #may not work
        if enemyChar.xpos < -0.1:
            if enemypunching:
                screen.blit(lpg, (enemyChar.xpos * display_size[0] + (display_size[0] / 2) - lpgs[0]/2, 250 - lpgs[1]/2 + (20+random.random()*10)*np.sin(ticks/7)))
            else:
                screen.blit(leftimg, (enemyChar.xpos * display_size[0] + (display_size[0] / 2) - leftimgsize[0]/2, 250 - leftimgsize[1]/2 + (20+random.random()*10)*np.sin(ticks/7)))
        elif enemyChar.xpos > 0.1:
            if enemypunching:
                screen.blit(rpg, (enemyChar.xpos * display_size[0] + (display_size[0] / 2) - rpgs[0]/2, 250 - rpgs[1]/2 + (20+random.random()*10)*np.sin(ticks/7)))
            else:
                screen.blit(rightimg, (enemyChar.xpos * display_size[0] + (display_size[0] / 2) - rightimgsize[0]/2, 250 - rightimgsize[1]/2 + (20+random.random()*10)*np.sin(ticks/7)))
        else:
            if enemypunching:
                screen.blit(mpg, (enemyChar.xpos * display_size[0] + (display_size[0] / 2) - mpgs[0]/2, 250 - mpgs[1]/2 + (20+random.random()*10)*np.sin(ticks/7)))
            else:
                screen.blit(midimg, (enemyChar.xpos * display_size[0] + (display_size[0] / 2) - midimgsize[0]/2, 250 - midimgsize[1]/2 + (20+random.random()*10)*np.sin(ticks/7)))
        
        # pygame.draw.circle(screen, (0,255,0), (youChar.xpos * display_size[0] + (display_size[0] / 2), 600), 25)
        if punchAnimating:
            screen.blit(player_punch_img, (youChar.xpos * display_size[0] + (display_size[0] / 2) - player_punch_img_size[0]/2, 600 - player_punch_img_size[1]/2))
        elif youChar.xpos <= 0:
            screen.blit(player_idle_1_img, (youChar.xpos * display_size[0] + (display_size[0] / 2) - player_idle_1_img_size[0]//2, 600 - player_idle_1_img_size[1]/2))
        else:
            screen.blit(player_idle_2_img, (youChar.xpos * display_size[0] + (display_size[0] / 2) - player_idle_2_img_size[0]//2, 600 - player_idle_2_img_size[1]/2))

    elif uistate == GAMEOVER:
        #display gameover screen
        pygame.draw.rect(screen,(255,255,255),(0,0,display_size[0],display_size[1]))
        
        #if isPunch():
        #    uiState=MENU
    else:
        pass #noop
while True:
    screen.fill((0,0,0))
    screen.blit(gamebg, (0,0))
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
    update(dt)
    pygame.display.flip()