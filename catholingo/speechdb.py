#!/usr/bin/python3
#coding: utf8

from peewee import (MySQLDatabase, Model, CharField, ForeignKeyField, TextField,
                    DateTimeField, BooleanField, IntegerField, fn)
from playhouse.db_url import connect
import datetime
import os

db = connect(os.environ.get('DATABASE') or 'sqlite:///catholingo.db')

def none_or(field, val):
    return field == val if not (val is None) else field >> None

def random():
    return fn.Random()

def connect():
    if db.is_closed():
        db.connect()

def close():
    if not db.is_closed():
        db.close()

def transaction():
    return db.transaction()

def create_tables():
    connect()
    if not Word.table_exists():
        Word.create_table(True)
    if not Speech.table_exists():
        Speech.create_table(True)

class BaseModel(Model):
    class Meta:
        database = db

class Word(Model):
    pprevious_word = CharField(null=True, max_length=100)
    previous_word = CharField(null=True, max_length=100)
    word        = CharField(max_length=100)
    next_word  = CharField(null=True, max_length=100)
    nnext_word  = CharField(null=True, max_length=100)

class Speech(Model):
    word = ForeignKeyField(Word)
    user = CharField(max_length=30)
    chan = CharField(max_length=30)
    datetime = DateTimeField(default=datetime.datetime.now)
