FROM python:3.7

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo/catholingo.py .
ADD catholingo/database.py .

CMD ["python", "./catholingo.py"]
