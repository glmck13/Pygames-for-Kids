#!/usr/bin/env python3

import sys
import pygame
from pygame.locals import *

TILE_PIX = 64
TILES_X = 11
TILES_Y = 7
SCREEN_XTILES = 11
SCREEN_YTILES = 7
SCREEN_WIDTH = 1+TILES_X*(TILE_PIX+1)
SCREEN_HEIGHT = 1+TILES_Y*(TILE_PIX+1)

pygame.init()
font = pygame.font.SysFont(None, 72)
clock = pygame.time.Clock()
heartbeat = pygame.event.Event(USEREVENT, mode="heartbeat")
pygame.time.set_timer(heartbeat, 500)

Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
sw = Screen.get_rect().w
sh = Screen.get_rect().h

AppInfo = [
	{"name": "Spell & Tell", "image": "spell.png", "exec": "~/opt/Pygames-for-Kids/Spell-and-Tell/spell.sh"},
	{"name": "Flashcards",   "image": "cards.png", "exec": "~/opt/Pygames-for-Kids/Flashcards/cards.sh"}
]
w = 0
for n, app in enumerate(AppInfo):
	surf = pygame.image.load(app["image"]).convert_alpha()
	w += surf.get_rect().w
	AppInfo[n]["surf"] = surf

j = int((sw-w)/(len(AppInfo)+1))
x = j
y = sh/2
for n, app in enumerate(AppInfo):
	desc = font.render(app["name"], True, 'brown')
	rect = app["surf"].get_rect(midleft=(x, y))
	AppInfo[n]["desc"] = desc
	AppInfo[n]["rect"] = rect
	x += rect.w + j

def move_cursor (delta):
	global Cursor
	Cursor = (Cursor + delta + len(AppInfo)) % len(AppInfo)

Cursor = 0
BORDER = 5

# Terminate app if no activity in 30 minutes
MAX_IDLE = 30*60*2
IdleTicks = 0

Done = False
while not Done:

	for event in pygame.event.get():
		#print(event, file=sys.stderr)
		if event.type == USEREVENT:
			IdleTicks += 1
			if IdleTicks >= MAX_IDLE:
				Cursor = -1
				Done = True
				break
		else:
			IdleTicks = 0

		if event.type == QUIT:
			Cursor = -1
			Done = True
			break

		elif event.type == JOYHATMOTION:
			quad = event.value
			if quad[0] > 0:
				move_cursor(1)
			elif quad[0] < 0:
				move_cursor(-1)
			elif quad[1] > 0:
				pass
			elif quad[1] < 0:
				pass

		elif event.type == JOYDEVICEADDED:
			joystick = pygame.joystick.Joystick(event.device_index)
			joystick.init()

		elif event.type == JOYBUTTONUP:
			if event.button in (4, 5):
				pass
			elif event.button in (2, 3):
				Done = True
				break
			elif event.button in (0, 1):
				Cursor = -1
				Done = True
				break
			elif event.button == 6:
				pass
			elif event.button == 7:
				pass

		elif event.type == MOUSEBUTTONUP:
			for n, app in enumerate(AppInfo):
				if app["rect"].collidepoint(event.pos):
					Cursor = n
					Done = True
					break

	Screen.fill('white')
	for n, app in enumerate(AppInfo):
		x, y = app["rect"].topleft
		Screen.blit(app["surf"], (x,y))
		Screen.blit(app["desc"], (x,y-TILE_PIX))
		if n == Cursor:
			pygame.draw.rect(Screen, 'green', (x-BORDER, y-TILE_PIX-BORDER, app["rect"].w+BORDER, app["rect"].h+TILE_PIX+BORDER), width=BORDER)
	pygame.display.flip()

	if Done:
		pygame.time.wait(1000)

	clock.tick(60)

if Cursor < 0:
	print('echo "Goodbye!"; exit')
else:
	print(AppInfo[Cursor]["exec"])

pygame.quit()
