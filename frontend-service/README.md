## Frontend Service Google Cloud Kubernetes Deployment

1. Initialize Google Cloud
```bash
gcloud init
```


2. Assign static IP address for load balancer and get ssl-certificates
```bash
gcloud compute addresses create static-ip --region us-central1


# gcloud beta compute ssl-certificates create ssl-cert-name --domains=????


#https://www.googlecloudcommunity.com/gc/Google-Kubernetes-Engine-GKE/How-to-setup-HTTPS-for-my-GKE-application/m-p/684063
```


3. Build and push images to Google Cloud Container Registry
```bash
./frontend-service-gcke.sh
```


4. View logs
```bash
kubectl get pods --all-namespaces
kubectl logs POD_NAME

# reset pod
kubectl delete pod my-pod
```