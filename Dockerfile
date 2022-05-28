FROM python:3

ARG IMAGE_APP_DIR=/usr/src/app

ENV APP_WORKDIR=/data/app/workdir
ENV BLIB_DIR=/data/app/blibdir
ENV BLIB_BUILD_EXEC_PATH=${IMAGE_APP_DIR}/bin/BlibBuild
ENV BLIB_FILTER_EXEC_PATH=${IMAGE_APP_DIR}/bin/BlibFilter

WORKDIR ${IMAGE_APP_DIR}

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod 755 ./bin/BlibBuild && chmod 755 ./bin/BlibFilter

CMD [ "python", "-u", "./start_service.py" ]
