## Local image build and run on Docker

1. Build docker file
```
# docker pull dpage/pgadmin4:latest
```

2. Run image as a container
```
# docker run -d -p 9000:9000 pgadmin-service:latest 
```

3. View message at http://127.0.0.1:9000/


## Kubernetes Engine deployment

1. Enable Google Cloud Container Registry via console

2. Initialize Google Cloud
```bash
gcloud init
```

3. Create a GKE Cluster for the project (use current if available)
```bash
#gcloud container clusters create ml-ops-cluster
```

4. Configure 'kubectl' to gcloud cluster
```bash
gcloud container clusters get-credentials ml-ops-cluster
```

5. Set up Cloud SQL and get 'connectionName' (PROJECT_ID:REGION:INSTANCE_ID)

6. Create a Kubernetes Secret
```bash
kubectl create secret generic pgadmin-secret \
--from-literal=PGADMIN_DEFAULT_EMAIL=admin@admin.com \
--from-literal=PGADMIN_DEFAULT_PASSWORD=password

```

7. Create/udate Kubernetes deployment script deployment.yaml

8. Deploy
```bash
kubectl apply -f pgadmin-deployment.yaml
```