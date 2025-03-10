#!/usr/bin/env python3

import sys
import string
import boto3

SPEECH_VOICE = "Joanna"

polly = boto3.client('polly')

for c in string.ascii_uppercase + '0123456789 ':

	print("'{}'".format(c), file=sys.stderr)

	if c == ' ':
		c = "space"

	with open("./sounds/" + c + ".ogg", 'wb') as f:
		f.write(polly.synthesize_speech(TextType="ssml", Text='<speak><prosody rate="slow">{}</prosody></speak>'.format(c), OutputFormat='ogg_vorbis', VoiceId=SPEECH_VOICE).get('AudioStream').read())
