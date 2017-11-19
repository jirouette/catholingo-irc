#!/usr/bin/python3
#coding: utf8

import database
from commands import TalkativeCommandOrder, OrderPool

class SQLCommand(TalkativeCommandOrder):
	COMMAND = "!sql"

	def talk(self, source, target, message):
		database.connect()
		payload = "Result = "
		results = database.execute(" ".join(message)).fetchall()
		if results:
			payload += " ".join([str(r) for r in results])
		database.close()
		return payload

class EvalCommand(TalkativeCommandOrder):
	COMMAND = "!eval"

	def talk(self, source, target, message):
		return eval(" ".join(message))

if __name__ == '__main__':
	pool = OrderPool(orders=[SQLCommand, EvalCommand])
	pool.run()
