FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod 755 ./bin/BlibBuild

CMD [ "python", "./start_service.py" ]
