#!/usr/bin/env python3

import sys
import boto3

SPEECH_VOICE = "Joanna"

polly = boto3.client('polly')

while True:

	card = sys.stdin.readline().strip()
	if not card:
		break

	print("'{}'".format(card), file=sys.stderr)

	with open("./cards/" + card.replace(' ', '-') + ".ogg", 'wb') as f:
		f.write(polly.synthesize_speech(TextType="ssml", Text='<speak><prosody rate="slow">{}</prosody></speak>'.format(card), OutputFormat='ogg_vorbis', VoiceId=SPEECH_VOICE).get('AudioStream').read())
