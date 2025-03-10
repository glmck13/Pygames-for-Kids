#!/usr/bin/env python3

import sys
import string
import pygame
from pygame.locals import *
import boto3

TILE_PIX = 64
TILES_X = 11
TILES_Y = 7
WORDBOX_X = 7
WORDBOX_Y = 2
SCREEN_WIDTH = 1+TILES_X*(TILE_PIX+1)
WORDBOX_WIDTH = 1+WORDBOX_X*(TILE_PIX+1)
SCREEN_HEIGHT = 1+TILES_Y*(TILE_PIX+1)
WORDBOX_HEIGHT = 1+WORDBOX_Y*(TILE_PIX+1)

pygame.init()
pygame.display.set_caption('Spell & Tell')
Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

font = pygame.font.SysFont(None, 72)

clock = pygame.time.Clock()
heartbeat = pygame.event.Event(USEREVENT, mode="heartbeat")
pygame.time.set_timer(heartbeat, 500)

Sounds = {}
Letters = []
for c in string.ascii_uppercase + string.ascii_lowercase + '0123456789 ':
	t = {}
	t["letter"] = c

	surf = []
	surf.append(pygame.Surface((TILE_PIX, TILE_PIX)))
	surf[0].fill('tan')
	img = font.render(c, True, 'brown')
	surf[0].blit(img, img.get_rect(center=surf[0].get_rect().center))

	surf.append(pygame.Surface((TILE_PIX, TILE_PIX)))
	surf[1].fill('green')
	img = font.render(c, True, 'brown')
	surf[1].blit(img, img.get_rect(center=surf[1].get_rect().center))
	t["surf"] = surf
	Letters.append(t)

	if c == ' ':
		u = "space"
	else:
		u = c.upper()
	Sounds[c] = pygame.mixer.Sound("./sounds/" + u + ".ogg")

WordSurf = pygame.Surface((WORDBOX_WIDTH, WORDBOX_HEIGHT))
WordRect = WordSurf.get_rect(topleft=(2*(TILE_PIX+1), 2*(TILE_PIX+1)))
WordTxt = "Hello"
WordBlink= 1

def move_cursor(delta):
	global Cursor
	while True:
		Cursor = (Cursor + delta + len(Tiles)) % len(Tiles)
		if Tiles[Cursor]:
			break

SPEECH_FILE = "./sounds/say.ogg"
SPEECH_VOICE = "Joanna"
polly = boto3.client('polly')
def tts():
	if not WordTxt:
		return

	try:
		with open(SPEECH_FILE, 'wb') as f:
			f.write(polly.synthesize_speech(Text=" spells " + WordTxt, OutputFormat='ogg_vorbis', VoiceId=SPEECH_VOICE).get('AudioStream').read())

		for c in WordTxt:
			pygame.time.wait(500)
			Sounds[c].play()
		else:
			pygame.time.wait(500)

		pygame.mixer.Sound(SPEECH_FILE).play()

	except:
		pass

Tiles = []
x = 1
y = 1
n = 0
while True:
	rect = pygame.Rect(x, y, TILE_PIX, TILE_PIX)
	if rect.colliderect(WordRect):
		Tiles.append(None)
	else:
		z = Letters[n]
		z["rect"] = rect
		Tiles.append(z)
		n += 1
	if n >= len(Letters):
		n = 0
	x += TILE_PIX + 1
	if x >= SCREEN_WIDTH:
		x = 1
		y += TILE_PIX + 1
	if y >= SCREEN_HEIGHT:
		break

Cursor = 0
LingerState = False
LingerCount = 0
MAX_LINGER = 2

# Terminate app if no activity in 60 minutes
MAX_IDLE = 60*60*2
IdleTicks = 0

while True:
	for event in pygame.event.get():
		#print(event, file=sys.stderr)
		if event.type == USEREVENT:
			IdleTicks += 1
			if IdleTicks >= MAX_IDLE:
				pygame.quit()
				raise SystemExit
		else:
			IdleTicks = 0
		if event.type == QUIT:
			pygame.quit()
			raise SystemExit
		elif event.type == JOYHATMOTION:
			quad = event.value
			if quad[0] > 0:
				move_cursor(1)
			elif quad[0] < 0:
				move_cursor(-1)
			elif quad[1] > 0:
				move_cursor(-TILES_X)
			elif quad[1] < 0:
				move_cursor(TILES_X)
		elif event.type == JOYDEVICEADDED:
			joystick = pygame.joystick.Joystick(event.device_index)
			joystick.init()
		elif event.type == JOYBUTTONUP:
			if event.button in (4, 5):
				tts()
			elif event.button in (0, 1, 2, 3):
				t = Tiles[Cursor]
				WordTxt += t["letter"]
				Sounds[t["letter"]].play()
			elif event.button == 6:
				WordTxt = WordTxt[:len(WordTxt)-1]
			elif event.button == 7:
				WordTxt = ""

		elif event.type == MOUSEBUTTONUP:
			if WordRect.collidepoint(event.pos):
				if LingerCount < MAX_LINGER:
					tts()
			else:
				for n, t in enumerate(Tiles):
					if not t:
						continue
					rect = t["rect"]
					if rect.collidepoint(event.pos):
						Cursor = n
						if LingerCount < MAX_LINGER:
							WordTxt += t["letter"]
							Sounds[t["letter"]].play()
			LingerState = False
			LingerCount = 0

		elif event.type == MOUSEBUTTONDOWN:
			if WordRect.collidepoint(event.pos):
				LingerState = True

		elif event.type == USEREVENT:
			WordBlink ^= 1
			if LingerState:
				LingerCount += 1
				if LingerCount > MAX_LINGER:
					WordTxt = ""
				elif LingerCount == MAX_LINGER:
					WordTxt = WordTxt[:len(WordTxt)-1]

	Screen.fill('Black')
	for n, t in enumerate(Tiles):
		if not t:
			continue
		rect = t["rect"]
		if n == Cursor:
			index = 1
		else:
			index = 0
		surf = t["surf"][index]
		Screen.blit(surf, rect)
	WordSurf.fill('Black')
	txt = WordTxt
	if WordBlink:
		txt += '|'
	WordSurf.blit(font.render(txt, True, 'White'), (TILE_PIX/2, TILE_PIX/2))
	Screen.blit(WordSurf, WordRect)

	pygame.display.flip()
	clock.tick(60)
