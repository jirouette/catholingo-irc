CathoLingo
===========

**CathoLingo** is an IRC bot using [Pydle](https://github.com/Shizmob/pydle) and [peewee](https://github.com/coleifer/peewee).

## Requirements

Docker et docker-compose are needed.
You can also build the project manually (with a supervisord or something). In that case, you will need :

- Python3 or more
- Libs *pydle* and *peewee* (pip is recommended : `pip install -r requirements.txt`)
- Don't forget to install database drivers (eg. *pymysql* for *MySQL*), it is needed by *peewee*

Environment vars :

- `DATABASE` : the url formatted database location (see [peewee documentation](http://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url)) (default, *sqlite:///catholingo.db*)
- `CHANNELS` : list of channels (including #) separated by spaces (default *#catholingo*)
- `USERNAME` : Username for the IRC server (default *CathoLingo*)
- `REALNAME` : Realname for the IRC server (default *la pizzeria*)
- `IRC_HOST` : IRC server to connect (default *chat.freenode.net*)
- `IRC_PORT` : IRC port to use (default *6697*)

## Usage

With `docker-compose` :

`docker-composer up -d`

Without Docker :

`python3 catholingo.py`

## License

This project is distributed under the WTFPL v2.0
