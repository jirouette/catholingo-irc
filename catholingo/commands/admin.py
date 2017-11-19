#!/usr/bin/python3
#coding: utf8

import speechdb
from commands import TalkativeCommandOrder, OrderPool

class SQLCommand(TalkativeCommandOrder):
	COMMAND = "!sql"

	def talk(self, source, target, message):
		speechdb.connect()
		payload = "Result = "
		results = speechdb.execute(" ".join(message)).fetchall()
		if results:
			payload += " ".join([str(r) for r in results])
		speechdb.close()
		return payload

class EvalCommand(TalkativeCommandOrder):
	COMMAND = "!eval"

	def talk(self, source, target, message):
		return eval(" ".join(message))

if __name__ == '__main__':
	pool = OrderPool(orders=[SQLCommand, EvalCommand])
	pool.run()
