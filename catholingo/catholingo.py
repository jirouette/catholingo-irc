#!/usr/bin/python3
#coding: utf8

import os
import pydle
import speechdb
from speechdb import Speech, Word

class Command(object):
	def __init__(self, client):
		self.client = client
		self.command = self.__class__.COMMAND
		if self.command[0] == "!":
			self.command = self.command[1:]

	def is_command(self, command):
		return self.command == command

	def execute(self, source, target, message):
		self.client.message(source, "hello ! ")

class TalkativeCommand(Command):
	def execute(self, source, target, message):
		response = self.talk(source, target, message)
		self.client.message(source, response)

	def talk(self, source, target, message):
		return "hello world ! "

class RandomCommand(TalkativeCommand):
	COMMAND = "speak"

	def talk(self, source, target, message):
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
			return payload
		else:
			return "no result"

class SpeakforCommand(TalkativeCommand):
	COMMAND = "speakfor"

	def talk(self, source, target, message):
		if len(message.split()) < 2:
			return ":("
		user = message.split()[1]
		word = Word.select().join(Speech).where((Word.previous_word >> None) & (Speech.user == user)).order_by(speechdb.random()).first()
		if word:
			pprev_word = None
			prev_word = word.word
			payload = word.word
			maxlength = 100
			while maxlength > 0:
				maxlength -= 1
				pprev_cond = speechdb.none_or(Word.pprevious_word, pprev_word)
				prev_cond = speechdb.none_or(Word.previous_word, prev_word)
				word = Word.select().join(Speech).where(pprev_cond & prev_cond & (Speech.user == user)).order_by(speechdb.random()).first()
				if word:
					payload += " " + word.word
					if word.next_word is None:
						break
					pprev_word = prev_word
					prev_word = word.word
				else:
					break
			return payload
		return "nope "+user+" :("

class CathoLingo(pydle.Client):
	def on_connect(self):
		speechdb.connect()
		speechdb.create_tables()
		for chan in os.environ.get('CHANNELS', '#amdo').split():
			self.join(chan)

	def set_commands(self, *args):
		self.commands = []
		for command in args:
			if isinstance(command, Command):
				self.commands.append(command)
			elif isinstance(command, type):
				try:
					command = command(client)
					if isinstance(command, Command):
						self.commands.append(command)
				except:
					pass

	def on_message(self, source, target, message):
		self.save_speech(source, target, message)
		self.command(source, target, message)

	def talk(self, source, target, message):
		self.message(source, "cccht, je suis en mission secrète, je reste silencieux")

	def command(self, source, target, message):
		if "CathoLingo" in message:
			self.talk(source, target, message)
		elif message[0] == "!":
			cmd = message.split()[0][1:]
			for command in self.commands:
				if command.is_command(cmd):
					return command.execute(source, target, message)

	def save_speech(self, channel, user, message):
		if message[0] in ["!", ",", ";", "~", "#", ".", "§"]:
			return

		with speechdb.transaction():
			message = message.split()
			for i, word in enumerate(message):
				pprev_word = message[i-2] if i > 1 else None
				prev_word  = message[i-1] if i > 0 else None
				next_word  = message[i+1] if i < len(message)-1 else None
				nnext_word = message[i+2] if i < len(message)-2 else None

				pprev_cond = speechdb.none_or(Word.pprevious_word, pprev_word)
				prev_cond  = speechdb.none_or(Word.previous_word, prev_word)
				next_cond  = speechdb.none_or(Word.next_word, next_word)
				nnext_cond = speechdb.none_or(Word.nnext_word, nnext_word)

				word = Word.select().where((pprev_cond) & (prev_cond) & (next_cond) & (nnext_cond) & (Word.word == word)).first()
				if not word:
					word = Word.create(pprevious_word=pprev_word,
									   previous_word=prev_word,
									   next_word=next_word,
									   nnext_word=nnext_word,
									   word=message[i])
					word.save()
				Speech.create(word=word, user=user, chan=channel).save()

if __name__ == '__main__':
	client = CathoLingo(os.environ.get('USERNAME', 'CathoLingo'), realname=os.environ.get('REALNAME', 'la pizzeria'))
	client.set_commands(RandomCommand, SpeakforCommand)
	client.connect(os.environ.get('IRC_HOST', 'chat.freenode.net'), int(os.environ.get('IRC_PORT', 6697)), tls=True, tls_verify=False)
	client.handle_forever()
