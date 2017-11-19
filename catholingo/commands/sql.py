#!/usr/bin/python3
#coding: utf8

import commands
import speechdb
import time
import random
from speechdb import Word, Speech

class Sql(commands.TalkativeCommandOrder):
	COMMAND = "!sql"

	def talk(self, source, target, message):
		speechdb.connect()
		payload = "Result = "
		results = speechdb.execute(" ".join(message)).fetchall()
		if results:
			payload += " ".join([str(r) for r in results])
		speechdb.close()
		return payload

if __name__ == '__main__':
	Sql().run()
