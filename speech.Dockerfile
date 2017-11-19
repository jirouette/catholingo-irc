FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo/commands/speech.py .
ADD catholingo/commands.py .
ADD catholingo/speechdb.py .

CMD ["python", "./speech.py"]
