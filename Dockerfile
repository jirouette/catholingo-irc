FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo/catholingo.py .
ADD catholingo/speechdb.py .

CMD ["python", "./catholingo.py"]
