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
font_freetype = pygame.freetype.SysFont(None, 50)
font_freetype.origin = True
Ground = font_freetype.get_rect('|').y

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

M_ADV_X = 4
def blit_word (txt, pos = -1):
	WordSurf.fill('black')
	metrics = font_freetype.get_metrics(txt)
	text_rect = font_freetype.get_rect(txt)
	text_surf = pygame.Surface(WordRect.size)
	x = 0
	for (n, (c, met)) in enumerate(zip(txt, metrics)):
		if n == pos:
			color = 'green'
		else:
			color = 'white'
		font_freetype.render_to(text_surf, (x, Ground), c, color)
		x += met[M_ADV_X]
	WordSurf.blit(text_surf, (TILE_PIX/2, TILE_PIX/2))

def spell_word ():
	for pos in range(0, len(WordTxt)):
		blit_word(txt, pos)
		Screen.blit(WordSurf, WordRect)
		pygame.display.update(WordRect)
		play_prompt(Sounds[WordTxt[pos].upper()])

def play_prompt (sound):
	sound.play()
	pygame.time.wait(int(sound.get_length()*1000))

SPEECH_FILE = "./sounds/say.ogg"
SPEECH_VOICE = "Joanna"
polly = boto3.client('polly')
def tts():
	if not WordTxt:
		return

	try:
		with open(SPEECH_FILE, 'wb') as f:
			f.write(polly.synthesize_speech(Text=" spells " + WordTxt, OutputFormat='ogg_vorbis', VoiceId=SPEECH_VOICE).get('AudioStream').read())

		spell_word()
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
				Done = True
				break
		else:
			IdleTicks = 0

		if event.type == QUIT:
			Done = True
			break

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
			elif event.button in (2, 3):
				t = Tiles[Cursor]
				WordTxt += t["letter"]
				Sounds[t["letter"]].play()
			elif event.button in (0, 1):
				Done = True
				break
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
	blit_word(txt)
	Screen.blit(WordSurf, WordRect)

	pygame.display.flip()
	clock.tick(60)

pygame.quit()
