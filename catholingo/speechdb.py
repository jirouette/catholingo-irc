#!/usr/bin/python3
#coding: utf8

from peewee import (MySQLDatabase, Model, CharField, ForeignKeyField, TextField,
                    DateTimeField, BooleanField, IntegerField, fn)
from playhouse.db_url import connect as connect_url
import datetime
import os
import sys

db = connect_url(os.environ.get('DATABASE'))


def none_or(field, val):
    return field == val if not (val is None) else field >> None

def execute(sql):
    return db.execute_sql(sql)

def random():
    return fn.Rand() if type(db) is MySQLDatabase else fn.Random()

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
    with transaction():
        db.create_tables([Word, Speech], safe=True)

class BaseModel(Model):
    class Meta:
        database = db

class Word(BaseModel):
    pprevious_word = CharField(null=True, max_length=100)
    previous_word = CharField(null=True, max_length=100)
    word        = CharField(max_length=100)
    next_word  = CharField(null=True, max_length=100)
    nnext_word  = CharField(null=True, max_length=100)

class Speech(BaseModel):
    word = ForeignKeyField(Word)
    user = CharField(max_length=30)
    chan = CharField(max_length=30)
    datetime = DateTimeField(default=datetime.datetime.now)
