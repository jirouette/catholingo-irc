FROM python:3

ADD requirements.txt .

RUN pip install -r ./requirements.txt

ADD catholingo/commands/admin.py .
ADD catholingo/commands.py .
ADD catholingo/database.py .

CMD ["python", "./admin.py"]
