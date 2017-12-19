FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo/commands/messenger.py .
ADD catholingo/commands.py .

CMD ["python", "./messenger.py"]
