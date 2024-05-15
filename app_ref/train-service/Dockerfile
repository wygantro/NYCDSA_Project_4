FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /train-service

ENV APP_HOME /train-service
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 6000

ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_NAME_train_service=train-service-db
ENV DB_NAME_feature_service=feature-service-db
ENV DB_HOST=35.184.60.255
ENV DB_PORT=5432

RUN chmod +x ./train-service-run.sh
ENTRYPOINT ["/bin/bash", "./train-service-run.sh"]