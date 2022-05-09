FROM python:3

ENV APP_WORKDIR=/data/app/workdir
ENV BLIB_DIR=/data/app/blibdir
ENV BLIB_BUILD_EXEC_PATH=/usr/src/app/bin/BlibBuild
ENV BLIB_FILTER_EXEC_PATH=/usr/src/app/bin/BlibFilter

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod 755 ./bin/BlibBuild && chmod 755 ./bin/BlibFilter

CMD [ "python", "./start_service.py" ]
