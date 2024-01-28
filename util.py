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
TICK_PHYSICS_MULTIPLIER = 500

ENEMY_GODLINESS_BASE =  20 #higher is easier


MENU = "menu"
GAME = "game"
GAMEOVER = "gameover"

EASY = 2000
MEDIUM = 1300
HARD = 700
BOSS = 500

def image_load_downscale(name, factor):
    img = pygame.image.load(name)
    imgsize = (img.get_width()//factor,img.get_height()//factor)
    img = pygame.transform.scale(img, imgsize)

    return (img, imgsize)