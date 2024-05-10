## Energy Consumption Model API Test build image and deploy container locally

1. Build docker image
```
docker build -t energy-consumption-api:latest .
```


2. Run local container
```
docker run -d -p 5000:5000 energy-consumption-api:latest 
```

## Energy Consumption Model API build and deploy Google Cloud Run

1. Initialize Google Cloud
```bash
gcloud init
```


2. Build, push and deploy images to Google Cloud Container Registry and Kubernetes Engine
```bash
./energy-consumption-api-gcr.sh

#docker inspect <container-id> | grep IPAddress
```


3. Launch in Google Cloud Run and set up Cloud Scheduler Cron Job
```bash
# Note: in cloud run enable network setting "Connect to a VPC for outbound traffic"

### cron job syntax ###
# daily: 0 0 * * *
# hour: 0 * * * *
# minute: * * * * *

### API extensions to call ###
# /api/v1/energy-consumption


# https://energy-consumption-api-wpyj5eetua-uc.a.run.app/api/v1/energy-consumption
```