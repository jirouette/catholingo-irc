#!/usr/bin/python3
#coding: utf8

import commands
import speechdb
import time
import random
import sys
from commands import TalkativeCommandOrder, CommandOrderPool
from speechdb import Word, Speech

def _conditions(*args):
	result = None
	for cond in args:
		if not cond:
			continue
		result = cond if not result else (result & cond)
	return result

def generator(conditions=None, first_condition=None, maxlength=100):
	speechdb.connect()
	_cond = _conditions(Word.previous_word >> None, conditions, first_condition)
	word = Word.select().join(Speech).where(_cond).order_by(speechdb.random()).first()
	if word:
		pprev_word = None
		prev_word  = word.word
		payload = word.word
		maxlength = 100
		while maxlength > 0:
			maxlength -= 1
			pprev_cond = speechdb.none_or(Word.pprevious_word, pprev_word)
			prev_cond = speechdb.none_or(Word.previous_word, prev_word)
			_cond = _conditions(pprev_cond, prev_cond, conditions)
			word = Word.select().join(Speech).where(_cond).order_by(speechdb.random()).first()
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
	speechdb.close()

class SpeakCommand(TalkativeCommandOrder):
	COMMAND = "!speak"

	def talk(self, source, target, message):
		sentence = generator()
		return sentence if sentence else "no result"

class SpeakforCommand(TalkativeCommandOrder):
	COMMAND = "!speakfor"

	def talk(self, source, target, message):
		sentence = generator(Speech.user == message[0])
		return sentence if sentence else "no result"

class StartWithCommand(TalkativeCommandOrder):
	COMMAND = "!startwith"

	def talk(self, source, target, message):
		sentence = generator(first_condition=Word.word == message[0])
		return sentence if sentence else "no result"

if __name__ == '__main__':
	pool = CommandOrderPool(commands=[SpeakCommand, SpeakforCommand, StartWithCommand])
	pool.run()
