# Dockerfile

FROM python:3.11.1
RUN pip install --upgrade pip
WORKDIR /energy-consumption-model

ENV APP_HOME /energy-consumption-api
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r ./config/requirements.txt

EXPOSE 5000

# database env
ENV DB_USER=user
ENV DB_PASS=postgres
ENV DB_ENERGY_CONSUMPTION_SERVICE_NAME=energy-consumption-db
#ENV DB_HOST=???
ENV DB_HOST=???
ENV DB_PORT=5432

CMD ["python", "energy_consumption_api.py"]