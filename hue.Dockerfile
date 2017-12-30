FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt
RUN pip install qhue

ADD catholingo/commands/hue.py .
ADD catholingo/commands.py .

CMD ["python", "./hue.py"]
