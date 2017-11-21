CathoLingo
===========

**CathoLingo** is an IRC bot using [Pydle](https://github.com/Shizmob/pydle) and [peewee](https://github.com/coleifer/peewee).

This bot can interpret commands through microservices which will listen discussions and possibly do actions.

## List of native services

### Speech

The **Speech** service saves words in database in order to generate random sentences.
For each word, the following data will be associated :
- Channel
- Nickname
- Datetime
- Previous word (if any)
- Previous word of previous word (if any)
- Next word (if any)
- Next word of next word (if any)

Surrounding words are saved in order to generate random but consistent sentences.

The services provides the following commands :
- **!speak** : Generate random sentence (up to 100words)
- **!speakfor <nickname>** : Generate random sentence (up to 100words) by using words from one user only
- **!startwith <word>** : Generate random sentence (up to 100words) by using a specific starting word

Highlighting the bot triggers the **!speak** command.

### Admin

The **Admin** service allows users to use admin centered actions. Some of its commands are highly unsecure and the service currently does not recognize admin users. You shouldn't use them. If you still want to use them, add an environment var `UNSECURE_MODE` in the admin service with value `1`.


The services provides the following commands :
- **!sql** : Execute arbitrary SQL queries in the configured database (require `UNSECURE_MODE`)
- **!eval** : Execute arbitrary Python statements (require `UNSECURE_MODE`)
- **!shell** : Execute arbitrary shell commands (require `UNSECURE_MODE`)
- **!mute <channels/nicknames>** : Force the bot to remain silent in the selected channels (or nicknames)
- **!unmute <channels/nicknames>** : Cancel the previous command


## Custom services

You can write custom services by extending one of the following classes from `commands` module :

- `TextOrder` : receives global text activity, through its `action` method and its parameters `source` (channel), `target` (nickname), `message` (splitted message)
- `CommandOrder` : triggers if a command is used (defined in `COMMAND` class var), through its `command` method nad its parameters `source` (channel), `target` (nickname), `message` (splitted message, ommiting the command)
- `TalkativeTextOrder` : receives global text activity, through its `talk` method (same as `action`). Anything returned from this method will be send to the source channel.
- `TalkativeCommandOrder` : triggers if a command is used (defined in `COMMAND` class var), through its `talk` method (same as `command`). Anything returned from this method will be send to the source channel.

Each of these classes also have a `client` attribute which represents the central IRC client (*Pydle* client), and a `run` method which runs forever.
If you want to define several commands inside a unique module, you can also the class `OrderPool` :

```python
if __name__ == '__main__':
	pool = OrderPool(orders=[SpeakCommand, SpeakforCommand, StartWithCommand, WordDatabaseOrder])
	# each of these commands are TalkativeCommandOrder or TextOrder
	pool.run()
```

### Service sample

```python
#!/usr/bin/python3
#coding: utf8

from commands import TalkativeCommandOrder
from functools import reduce
import operator

class Calculator(TalkativeCommandOrder):
	COMMAND = ["!compute", "!calculator", "!calculate"]

	OPERATORS = {
		'+': sum,
		'-': lambda numbers: numbers[-2] - numbers[-1],
		'*': lambda numbers: reduce(operator.mul, numbers, 1),
		'/': lambda numbers: numbers[-2] / numbers[-1]
	}

	def talk(self, source, target, message):
		number_pool = []
		for n in message:
			try:
				n = int(n)
				number_pool.append(n)
			except ValueError:
				if n in self.OPERATORS.keys():
					try:
						number_pool = [self.OPERATORS[n](number_pool)]
					except IndexError:
						return "operand error"
					else:
						continue
				return "operator error"
		try:
			return str(number_pool[0])
		except IndexError:
			return "0"

if __name__ == '__main__':
	Calculator().run()
```

Usage :

```
<jr> !calculate 6 7 * 3 +
<CathoLingo> 45
<jr> !calculate 87 40 -
<CathoLingo> 47
<jr> !calculate 10 2 /
<CathoLingo> 5.0
```

## Requirements

Docker et docker-compose are needed.
You can also build the project manually (with a supervisord or something). In that case, you will need :

- Python3 or more
- Libs *pydle* and *peewee* (pip is recommended : `pip install -r requirements.txt`)
- Don't forget to install database drivers (eg. *pymysql* for *MySQL*), it is required by *peewee*

### Environment vars

#### CathoLingo instance vars
- `CHANNELS` : list of channels (including #) separated by spaces (default *#catholingo*)
- `USERNAME` : Username for the IRC server (default *CathoLingo*)
- `REALNAME` : Realname for the IRC server (default *la pizzeria*)
- `IRC_HOST` : IRC server to connect (default *chat.freenode.net*)
- `IRC_PORT` : IRC port to use (default *6697*)

#### Commands instance vars

- `DATABASE` : the url formatted database location (see [peewee documentation](http://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url)) (default, *sqlite:///catholingo.db*)
- `DEBUG` : If defined, will output peewee debug in stderr (default, undefined)

(if using `database` module)

#### Both

- `REDIS_HOST` : Redis server to connect in which **CathoLingo** and its workers will communicate, (default, *localhost*)
- `REDIS_PORT` : Redis port (default, *6379*)
- `CATHOLINGO_REDIS_ORDER_CHANNEL` : Redis channel in which **CathoLingo** will send IRC activity to its workers, (default, *catholingo_order*)
- `CATHOLINGO_REDIS_EXECUTE_CHANNEL` : Redis channel in which workers will execute actions on **CathoLingo** instance (default, *catholingo_execute*)

## Usage

### With `docker-compose` :

`docker-composer up -d`

### Without Docker :

`python3 catholingo.py`

you will also need to start any microservice individually :

`cd commands && python3 ./speech.py` (etc.)

## License

This project is distributed under the WTFPL v2.0
