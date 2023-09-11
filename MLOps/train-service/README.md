# train-service container build and deployment
## Local image build and run on Docker

1. Build docker file
```
# docker build -t train-service:latest .
```

2. Run image as a container
```
# docker run -d -p 6000:6000 train-service:latest 
```

3. View message at http://127.0.0.1:6000/

## Build image and push to Google Cloud Container Registry

1. Enable Google Cloud Container Registry via console

2. Initialize Google Cloud
```bash
gcloud init
```

3. Build docker image
```bash
docker build -t gcr.io/nycdsa-project-4/train-service:latest .

# docker run -d -p 6000:6000 gcr.io/nycdsa-project-4/train-service:latest
```

4. Authenticate Docker with Google cloud project
```bash
gcloud auth configure-docker
```

5. Push image to Google Container Registry
```bash
docker push gcr.io/nycdsa-project-4/train-service:latest
```

6. Confirm image is located Google Container Registry


## Kubernetes Engine deployment

1. Enable Google Cloud Container Registry via console

2. Initialize Google Cloud
```bash
gcloud init
```

3. Create a GKE Cluster for the project (use current if available)
```bash
gcloud container clusters create ml-ops-cluster

gcloud container clusters create ml-ops-cluster \
  --num-nodes=3 \
  --disk-size=50GB \
```

4. Configure 'kubectl' to gcloud cluster
```bash
gcloud container clusters get-credentials ml-ops-cluster
```

5. Set up Cloud SQL and get 'connectionName' (PROJECT_ID:REGION:INSTANCE_ID)

6. Create a Kubernetes Secret
```bash
kubectl create secret generic cloudsql-db-credentials \
    --from-literal=username=user \
    --from-literal=password=postgres

    # --from-literal=username=
    # --from-literal=password=[YOUR_PASSWORD]
```

7. Create/udate Kubernetes deployment script deployment.yaml

8. Deploy
```bash
kubectl apply -f deployment.yaml
```

9. Expose (if application serves traffic)
```bash
kubectl expose deployment predict-service-name --type=LoadBalancer --port 6000 [PORT_YOUR_APP_RUNS_ON]

#get external ip
kubectl get svc
```