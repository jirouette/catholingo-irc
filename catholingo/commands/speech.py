#!/usr/bin/python3
#coding: utf8

import database
import os
from commands import TextOrder, TalkativeCommandOrder, OrderPool
from database import Word, Speech

def _conditions(*args):
	result = None
	for cond in args:
		if not cond:
			continue
		result = cond if not result else (result & cond)
	return result

class WordDatabaseOrder(TextOrder):
	NICKNAME = "CathoLingo"

	def action(self, source, target, message):
		if message[0][0] in ["!", ",", ";", "~", "#", ".", "§"]:
			return

		with database.connection():
			with database.transaction():
				for i, word in enumerate(message):
					pprev_word = message[i-2] if i > 1 else None
					prev_word  = message[i-1] if i > 0 else None
					next_word  = message[i+1] if i < len(message)-1 else None
					nnext_word = message[i+2] if i < len(message)-2 else None

					pprev_cond = database.none_or(Word.pprevious_word, pprev_word)
					prev_cond  = database.none_or(Word.previous_word, prev_word)
					next_cond  = database.none_or(Word.next_word, next_word)
					nnext_cond = database.none_or(Word.nnext_word, nnext_word)

					word = Word.select().where((pprev_cond) & (prev_cond) & (next_cond) & (nnext_cond) & (Word.word == word)).first()
					if not word:
						word = Word.create(pprevious_word=pprev_word,
										   previous_word=prev_word,
										   next_word=next_word,
										   nnext_word=nnext_word,
										   word=message[i])
						word.save()
					Speech.create(word=word, user=target, chan=source).save()
		self.check_speak(source, target, message)

	def check_speak(self, source, target, message):
		if self.NICKNAME.lower() in " ".join(message).lower():
			sentence = WordDatabaseOrder.generator()
			if sentence:
				self.client.message(source, sentence)

	@staticmethod
	def generator(conditions=None, first_condition=None, maxlength=100):
		with database.connection():
			_cond = _conditions(Word.previous_word >> None, conditions, first_condition)
			word = Word.select().join(Speech).where(_cond).order_by(database.random()).first()
			if word:
				pprev_word = None
				prev_word  = word.word
				payload = word.word
				maxlength = 100
				while maxlength > 0:
					maxlength -= 1
					pprev_cond = database.none_or(Word.pprevious_word, pprev_word)
					prev_cond = database.none_or(Word.previous_word, prev_word)
					_cond = _conditions(pprev_cond, prev_cond, conditions)
					word = Word.select().join(Speech).where(_cond).order_by(database.random()).first()
					if word:
						payload += " " + word.word
						if word.next_word is None:
							break

						pprev_word = prev_word
						prev_word = word.word
					else:
						break
				return payload

class SpeakCommand(TalkativeCommandOrder):
	COMMAND = "!speak"

	def talk(self, source, target, message):
		sentence = WordDatabaseOrder.generator()
		return sentence if sentence else "no result"

class SpeakforCommand(TalkativeCommandOrder):
	COMMAND = "!speakfor"

	def talk(self, source, target, message):
		sentence = WordDatabaseOrder.generator(Speech.user == message[0])
		return sentence if sentence else "no result"

class StartWithCommand(TalkativeCommandOrder):
	COMMAND = "!startwith"

	def talk(self, source, target, message):
		sentence = WordDatabaseOrder.generator(first_condition=Word.word == message[0])
		return sentence if sentence else "no result"

if __name__ == '__main__':
	if os.environ.get('DEBUG'):
		import logging
		logger = logging.getLogger('peewee')
		logger.setLevel(logging.DEBUG)
		logger.addHandler(logging.StreamHandler())
	with database.connection():
		database.create_tables()
	pool = OrderPool(orders=[SpeakCommand, SpeakforCommand, StartWithCommand, WordDatabaseOrder])
	pool.run()
