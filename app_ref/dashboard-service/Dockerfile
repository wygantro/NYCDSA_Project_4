FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /dashboard-service

ENV APP_HOME /dashboard-service
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

EXPOSE 8080

ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_NAME_train_service=train-service-db
ENV DB_NAME_feature_service=feature-service-db
ENV DB_PORT=5432

RUN chmod +x ./dashboard-run.sh
ENTRYPOINT ["/bin/bash", "./dashboard-run.sh"]