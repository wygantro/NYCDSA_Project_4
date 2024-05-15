# dashboard-service container build and deploy

## Local image build and run on Docker

1. Build docker file
```
# docker build -t dashboard-service:latest .
```

2. Run image as a container
```
# docker run -d -p 8080:8080 dashboard-service:latest 
```

3. View message at http://127.0.0.1:8080/

## Build image and push to Google Cloud Container Registry

1. Enable Google Cloud Container Registry via console

2. Initialize Google Cloud
```bash
gcloud init
```

3. Build docker image
```bash
docker build -t gcr.io/nycdsa-project-4/dashboard-service:latest .

# docker run -d -p 8080:8080 gcr.io/nycdsa-project-4/dashboard-service:latest
```

4. Authenticate Docker with Google cloud project
```bash
gcloud auth configure-docker
```

5. Push image to Google Container Registry
```bash
docker push gcr.io/nycdsa-project-4/dashboard-service:latest
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
```

4. Configure 'kubectl' to gcloud cluster
```bash
gcloud container clusters get-credentials ml-ops-cluster
```

5. Set up Cloud SQL and get 'connectionName' (PROJECT_ID:REGION:INSTANCE_ID)

6. Create a Kubernetes Secret
```bash
kubectl create secret generic my-google-service-account --from-file=service-account.json=./nycdsa-project-4-5549488078d1.json

# kubectl create secret generic google-service-account --from-file=service-account.json=/path/to/service-account.json
# kubectl create secret generic google-service-account --from-file=service-account.json=nycdsa-project-4-5549488078d1.json

kubectl get secrets

kubectl delete secret [SECRET_NAME] -n [NAMESPACE]
```

7. Create/udate Kubernetes deployment script deployment.yaml

8. Deploy
```bash
kubectl apply -f deployment.yaml
```

9. Expose (if application serves traffic)
```bash
kubectl expose deployment dashboard-service --type=LoadBalancer --port 8080 [PORT_YOUR_APP_RUNS_ON]

#get external ip
kubectl get svc
```