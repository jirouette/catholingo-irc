FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo.py .
ADD speechdb.py .

CMD ["python", "./catholingo.py"]
