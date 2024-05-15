FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /feature-service

ENV APP_HOME /feature-service
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 5000

ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_NAME=feature-service-db
ENV DB_HOST=35.184.60.255
ENV DB_PORT=5432

RUN chmod +x ./feature-service-run.sh
ENTRYPOINT ["/bin/bash", "./feature-service-run.sh"]