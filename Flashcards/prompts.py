#!/usr/bin/env python3

import sys
import boto3

SPEECH_VOICE = "Joanna"
PROMPTS = [
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">A</say-as>!</prosody></speak>', "fname" : "A"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">B</say-as>!</prosody></speak>', "fname" : "B"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">C</say-as>!</prosody></speak>', "fname" : "C"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">D</say-as>!</prosody></speak>', "fname" : "D"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">E</say-as>!</prosody></speak>', "fname" : "E"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">F</say-as>!</prosody></speak>', "fname" : "F"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">G</say-as>!</prosody></speak>', "fname" : "G"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">H</say-as>!</prosody></speak>', "fname" : "H"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">I</say-as>!</prosody></speak>', "fname" : "I"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">J</say-as>!</prosody></speak>', "fname" : "J"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">K</say-as>!</prosody></speak>', "fname" : "K"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">L</say-as>!</prosody></speak>', "fname" : "L"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">M</say-as>!</prosody></speak>', "fname" : "M"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">N</say-as>!</prosody></speak>', "fname" : "N"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">O</say-as>!</prosody></speak>', "fname" : "O"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">P</say-as>!</prosody></speak>', "fname" : "P"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">Q</say-as>!</prosody></speak>', "fname" : "Q"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">R</say-as>!</prosody></speak>', "fname" : "R"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">S</say-as>!</prosody></speak>', "fname" : "S"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">T</say-as>!</prosody></speak>', "fname" : "T"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">U</say-as>!</prosody></speak>', "fname" : "U"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">V</say-as>!</prosody></speak>', "fname" : "V"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">W</say-as>!</prosody></speak>', "fname" : "W"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">X</say-as>!</prosody></speak>', "fname" : "X"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">Y</say-as>!</prosody></speak>', "fname" : "Y"},
{"speech" : '<speak><prosody rate="slow">Give me a <say-as interpret-as="characters">Z</say-as>!</prosody></speak>', "fname" : "Z"},
{"speech" : '<speak><prosody rate="slow">Give me a space</prosody></speak>', "fname" : "space"},
{"speech" : '<speak><prosody rate="slow">Let\'s spell the word:</prosody></speak>', "fname" : "lets-spell"},
{"speech" : '<speak><prosody rate="slow">Try again!</prosody></speak>', "fname" : "try-again"},
{"speech" : '<speak><prosody rate="slow">Got it!</prosody></speak>', "fname" : "got-it"},
{"speech" : '<speak><prosody rate="slow">Congratulations!</prosody></speak>', "fname" : "congrats"},
{"speech" : '<speak><prosody rate="slow">spells</prosody></speak>', "fname" : "spells"},
]

polly = boto3.client('polly')

for p in PROMPTS:

	print("'{}'".format(p), file=sys.stderr)

	with open("./prompts/" + p["fname"] + ".ogg", 'wb') as f:
		f.write(polly.synthesize_speech(TextType="ssml", Text=p["speech"], OutputFormat='ogg_vorbis', VoiceId=SPEECH_VOICE).get('AudioStream').read())
