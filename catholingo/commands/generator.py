#!/usr/bin/python3
#coding: utf8

import commands
import speechdb
import time
import random
import sys
from speechdb import Word, Speech

class SpeakCommand(commands.TalkativeCommandOrder):
	COMMAND = "!speak"

	def talk(self, source, target, message):
		speechdb.connect()
		word = Word.select().where(Word.previous_word >> None).order_by(speechdb.random()).first()
		if word:
			pprev_word = None
			prev_word  = word.word
			payload = word.word
			maxlength = 100
			while maxlength > 0:
				maxlength -= 1
				pprev_cond = speechdb.none_or(Word.pprevious_word, pprev_word)
				prev_cond = speechdb.none_or(Word.previous_word, prev_word)
				word = Word.select().where(pprev_cond & prev_cond).order_by(speechdb.random()).first()
				if word:
					payload += " " + word.word
					if word.next_word is None:
						break

					pprev_word = prev_word
					prev_word = word.word
				else:
					break
			speechdb.close()
			return payload
		else:
			speechdb.close()
			return "no result"

if __name__ == '__main__':
	SpeakCommand().run()
