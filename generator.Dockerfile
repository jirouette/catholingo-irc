FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo/commands/generator.py .
ADD catholingo/commands.py .
ADD catholingo/speechdb.py .

CMD ["python", "./generator.py"]
