#!/usr/bin/env python3

import sys
import string
import pygame
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Flashcards')

CARD_START = 0
CARD_PROMPT = 1
CARD_END = 2
CARD_WAIT = 3
Cards = []
for card in sys.stdin.read().split('\n'):
	if not card:
		continue
	card = card.split(',')
	Cards.append({"name" : card[0], "image" : card[1], "sound" : card[2]})
CardIndex = len(Cards)-1
CardSubindex = -1
CardState = CARD_WAIT

PromptLetsSpell = pygame.mixer.Sound("./prompts/" + "lets-spell" + ".ogg")
PromptGotit = pygame.mixer.Sound("./prompts/" + "got-it" + ".ogg")
PromptTryAgain = pygame.mixer.Sound("./prompts/" + "try-again" + ".ogg")
PromptCongrats = pygame.mixer.Sound("./prompts/" + "congrats" + ".ogg")
PromptSpells = pygame.mixer.Sound("./prompts/" + "spells" + ".ogg")
PromptCard = None

TILE_PIX = 64
SCREEN_XTILES = 11
SCREEN_YTILES = 7
ALPHA_XTILES = 4
ALPHA_YTILES = 7
CARD_XTILES = SCREEN_XTILES - ALPHA_XTILES
CARD_YTILES = SCREEN_YTILES
WORDBOX_XTILES = SCREEN_XTILES - ALPHA_XTILES
WORDBOX_YTILES = 1

SCREEN_WIDTH = 1+SCREEN_XTILES*(TILE_PIX+1)
SCREEN_HEIGHT = 1+SCREEN_YTILES*(TILE_PIX+1)
Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

WORDBOX_WIDTH = 1+WORDBOX_XTILES*(TILE_PIX+1)
WORDBOX_HEIGHT = 1+WORDBOX_YTILES*(TILE_PIX+1)
WordSurf = pygame.Surface((WORDBOX_WIDTH, WORDBOX_HEIGHT))
WordRect = WordSurf.get_rect(topleft=(ALPHA_XTILES*(TILE_PIX+1), (SCREEN_YTILES-WORDBOX_YTILES)*(TILE_PIX+1)))

CARD_WIDTH = 1+CARD_XTILES*(TILE_PIX+1)
CARD_HEIGHT = 1+CARD_YTILES*(TILE_PIX+1)
CardSurf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
CardSurf.fill('black')
CardRect = CardSurf.get_rect(topleft=(1+ALPHA_XTILES*(TILE_PIX+1), 0))
BlankCard = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
BlankCard.fill('black')

font = pygame.font.SysFont(None, 72)
font_freetype = pygame.freetype.SysFont(None, 50)
font_freetype.origin = True
Ground = font_freetype.get_rect('|').y

clock = pygame.time.Clock()
heartbeat = pygame.event.Event(USEREVENT, mode="heartbeat")
pygame.time.set_timer(heartbeat, 500)

PromptLetter = {}
Sounds = {}
Letters = []
for c in string.ascii_uppercase + '  ':
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
		u = c
	Sounds[c] = pygame.mixer.Sound("./keypad/" + u + ".ogg")
	PromptLetter[c] = pygame.mixer.Sound("./prompts/" + u + ".ogg")

WordTxt = "Flashcards"
WordBlink = 1

def move_cursor (delta):
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
	WordSurf.blit(text_surf, (10-text_rect.x, 15))

def spell_word ():
	for pos in range(0, len(WordTxt)):
		blit_word(txt, pos)
		Screen.blit(WordSurf, WordRect)
		pygame.display.update(WordRect)
		play_prompt(Sounds[WordTxt[pos].upper()])

def play_prompt (sound):
	sound.play()
	pygame.time.wait(int(sound.get_length()*1000))

Tiles = []
for y in range(0, ALPHA_YTILES):
	for x in range(0, ALPHA_XTILES):
		z = Letters[len(Tiles)]
		z["rect"] = pygame.Rect(1+x*(TILE_PIX+1), 1+y*(TILE_PIX+1), TILE_PIX, TILE_PIX)
		Tiles.append(z)

Cursor = len(Tiles)-1
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
				move_cursor(-ALPHA_XTILES)
			elif quad[1] < 0:
				move_cursor(ALPHA_XTILES)

		elif event.type == JOYDEVICEADDED:
			joystick = pygame.joystick.Joystick(event.device_index)
			joystick.init()

		elif event.type == JOYBUTTONUP:
			if event.button in (4, 5):
				CardState = CARD_PROMPT
			elif event.button in (2, 3):
				t = Tiles[Cursor]
				c = t["letter"].lower()
				if CardSubindex < 0 or CardSubindex >= len(Cards[CardIndex]["name"]):
					pass
				elif c == Cards[CardIndex]["name"][CardSubindex]:
					CardSubindex += 1
					CardState = CARD_PROMPT
					WordTxt += c.lower()
					play_prompt(PromptGotit)
				else:
					play_prompt(PromptTryAgain)
			elif event.button in (0, 1):
				Done = True
				break
			elif event.button == 6:
				WordTxt = WordTxt[:len(WordTxt)-1]
				if CardSubindex > 0:
					CardSubindex -= 1
				CardState = CARD_PROMPT
			elif event.button == 7:
				WordTxt = ""
				CardState = CARD_START
				CardSurf.fill('black')

		elif event.type == MOUSEBUTTONUP:
			if WordRect.collidepoint(event.pos):
				if LingerCount < MAX_LINGER:
					CardState = CARD_PROMPT
			else:
				for n, t in enumerate(Tiles):
					if not t:
						continue
					rect = t["rect"]
					if rect.collidepoint(event.pos):
						Cursor = n
						if LingerCount < MAX_LINGER:
							c = t["letter"].lower()
							if CardSubindex < 0 or CardSubindex >= len(Cards[CardIndex]["name"]):
								pass
							elif c == Cards[CardIndex]["name"][CardSubindex]:
								CardSubindex += 1
								CardState = CARD_PROMPT
								WordTxt += c.lower()
								play_prompt(PromptGotit)
							else:
								play_prompt(PromptTryAgain)
			LingerState = False
			LingerCount = 0

		elif event.type == MOUSEBUTTONDOWN:
			if WordRect.collidepoint(event.pos):
				LingerState = True
			else:
				for n, t in enumerate(Tiles):
					if not t:
						continue
					rect = t["rect"]
					if rect.collidepoint(event.pos):
						Cursor = n

		elif event.type == USEREVENT:
			WordBlink ^= 1
			if LingerState:
				LingerCount += 1
				if LingerCount > MAX_LINGER:
					WordTxt = ""
					CardState = CARD_START
					CardSurf.fill('black')
				elif LingerCount == MAX_LINGER:
					WordTxt = WordTxt[:len(WordTxt)-1]
					if CardSubindex > 0:
						CardSubindex -= 1
					CardState = CARD_PROMPT

	Screen.blit(BlankCard, CardRect)
	Screen.blit(CardSurf, CardRect)
	WordSurf.fill('black')
	txt = WordTxt
	if WordBlink:
		txt += '|'
	blit_word(txt)
	Screen.blit(WordSurf, WordRect)
	pygame.display.flip()
	clock.tick(60)

	Screen.fill('black')
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

	if CardState == CARD_START:
		CardIndex = (CardIndex + 1) % len(Cards)
		CardSurf = pygame.image.load("./cards/" + Cards[CardIndex]["image"]).convert()
		CardPrompt = pygame.mixer.Sound("./cards/" + Cards[CardIndex]["sound"])
		play_prompt(PromptLetsSpell)
		play_prompt(CardPrompt)
		CardSubindex = 0
		CardState = CARD_PROMPT

	elif CardState == CARD_PROMPT:
		if CardSubindex < 0 or CardSubindex >= len(Cards[CardIndex]["name"]):
			pass
		else:
			play_prompt(PromptLetter[Cards[CardIndex]["name"][CardSubindex].upper()])
		CardState = CARD_WAIT

	elif CardState == CARD_END:
		play_prompt(PromptCongrats)
		spell_word()
		play_prompt(PromptSpells)
		play_prompt(CardPrompt)
		CardSubindex = -1
		CardState = CARD_WAIT

	elif CardState == CARD_WAIT:
		if CardSubindex >= len(Cards[CardIndex]["name"]):
			CardState = CARD_END

pygame.quit()
