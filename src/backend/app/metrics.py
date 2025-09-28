from prometheus_client import Counter

# create a simple counter for requests to /data
DATA_REQUESTS = Counter("app_data_requests_total", "Total /data requests")
