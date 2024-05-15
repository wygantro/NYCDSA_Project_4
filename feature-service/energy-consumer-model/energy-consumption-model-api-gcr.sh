#!/bin/bash

# check file execution permissions
if [[ ! -x $0 ]]; then
    echo "making the script executable..."
    chmod +x $0
    exec $0 "$@"
fi

# define energy-consumption-api image
IMAGE_NAME="energy-consumption-api"
PROJECT_ID="$(gcloud config get-value project)"
GCR_HOSTNAME="gcr.io"

# build and push image to Google Cloud
docker build -t "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_NAME}:latest" .
gcloud auth configure-docker
docker push "${GCR_HOSTNAME}/${PROJECT_ID}/${IMAGE_NAME}:latest"

echo "energy-consumption-api images built and pushed successfully"

# Deploy Docker image to Cloud Run
# REGION = 
# PORT = 
# ALLOW_UNAUTHENTICATED = True
# SERVICE_NAME = 

# gcloud run deploy --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
#                   --platform managed \
#                   --region $REGION \
#                   --port $PORT \
#                   --allow-unauthenticated=$ALLOW_UNAUTHENTICATED \
#                   --service=$SERVICE_NAME
