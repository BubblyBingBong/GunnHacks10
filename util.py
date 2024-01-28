import pygame

LEFT = 0
RIGHT = 2
MIDDLE = 1

REST = "rest"
PUNCH = "punch"

ENEMY_COOLDOWN = 150
ALLIED_COOLDOWN = 75
ENEMY_HP = 5
ALLIED_HP = 7
ENEMY_TARGET_RANGE = .2
ALLIED_HIT_RANGE = .3
TICK_PHYSICS_MULTIPLIER = 350

ENEMY_GODLINESS_BASE =  25 #higher is easier


MENU = "menu"
MENU2 = "menu2"
GAME = "game"
GAMEOVER = "gameover"

BEGINNER = 3000
EASY = 2000
MEDIUM = 1700
HARD = 1400
BOSS = 700

def image_load_downscale(name, factor):
    img = pygame.image.load(name)
    imgsize = (img.get_width()//factor,img.get_height()//factor)
    img = pygame.transform.scale(img, imgsize)

    return (img, imgsize)