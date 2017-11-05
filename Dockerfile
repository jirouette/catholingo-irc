FROM python:3

RUN pip install peewee pydle redis pymysql

ADD catholingo.py .
ADD speechdb.py .

CMD ["python", "./catholingo.py"]
