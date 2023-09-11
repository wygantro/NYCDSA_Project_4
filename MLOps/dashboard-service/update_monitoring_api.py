from google.cloud import monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta
import os
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import pickle
import time

def get_gc_server_values():
    # get secrets and define credentials

    service_account_path = "/var/secrets/google/service-account.json"
    credentials = Credentials.from_service_account_info(service_account_path)
    client = monitoring_v3.MetricServiceClient(credentials=credentials)
    
    # Specify your Project ID
    project_id = "nycdsa-project-4"
    project_name = f"projects/{project_id}"
    
    # Create Timestamp objects for the start and end times
    now = datetime.utcnow()
    five_minutes_ago = now - timedelta(minutes=1)
    
    start_timestamp = Timestamp()
    start_timestamp.FromDatetime(five_minutes_ago)
    end_timestamp = Timestamp()
    end_timestamp.FromDatetime(now)
    
    # Create and populate the TimeInterval object
    interval = monitoring_v3.TimeInterval()
    
    interval.start_time = start_timestamp
    interval.end_time = end_timestamp
    
    ### cpu_limit_utilization_current
    request = monitoring_v3.ListTimeSeriesRequest(
        name=project_name,
        filter='metric.type="kubernetes.io/container/cpu/limit_utilization"',
        interval=interval,
        )
    for series in client.list_time_series(request):
        for point in series.points:
            cpu_limit_utilization_current = point.value.double_value

    ### postgresql_num_conn_backends
    request = monitoring_v3.ListTimeSeriesRequest(
        name=project_name,
        filter='metric.type="cloudsql.googleapis.com/database/postgresql/num_backends_by_state"',
        interval=interval,
        )
    
    for series in client.list_time_series(request):
        if series.metric.labels == {'state': 'idle', 'database': 'feature-service-db'}:
            postgresql_idle_conn = series.points[-1].value.int64_value
    
    ### kubernetes_memory_limit_utilization
    request = monitoring_v3.ListTimeSeriesRequest(
        name=project_name,
        filter='metric.type="kubernetes.io/container/memory/used_bytes"',
        interval=interval,
        )
    kubernetes_memory_limit_utilization_lst = []
    for series in client.list_time_series(request):
        kubernetes_memory_limit_utilization_lst.append(series.points[-1].value.int64_value)
    kubernetes_memory_limit_utilization = kubernetes_memory_limit_utilization_lst[-2]
    
    return [cpu_limit_utilization_current, postgresql_idle_conn, kubernetes_memory_limit_utilization]


if os.path.exists('server_update_lst.pkl'):
    with open('server_update_lst.pkl', 'rb') as f:
        server_update_lst = pickle.load(f)

    time_data = server_update_lst[0]
    cpu_data = server_update_lst[1]
    db_conn_data = server_update_lst[2]
    memory_data = server_update_lst[3]
else:
    time_data = []
    cpu_data = []
    db_conn_data = []
    memory_data = []

time.sleep(5)
update_monitoring_lst = get_gc_server_values()
    
time_data.append(datetime.now())
cpu_data.append(update_monitoring_lst[0])
db_conn_data.append(update_monitoring_lst[1])
memory_data.append(update_monitoring_lst[2])
    
if len(cpu_data) > 400:
    del time_data[0]
    del cpu_data[0]
    del db_conn_data[0]
    del memory_data[0]
    
    
server_update_lst = [time_data, cpu_data, db_conn_data, memory_data]
    
with open('server_update_lst.pkl', 'wb') as f:
    pickle.dump(server_update_lst, f)
