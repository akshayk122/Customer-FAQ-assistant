import re
import time
import logging
from collections import deque

# Configure logging
logging.basicConfig(filename='query_input.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MAX_QUERIES = 5
TIME_WINDOW = 60  # seconds
query_timestamps = deque()

def is_valid_query(query):
    return bool(re.match(r"^[\w\s\?\-\,\.\']{1,200}$", query))

def is_rate_limited():
    now = time.time()
    while query_timestamps and now - query_timestamps[0] > TIME_WINDOW:
        query_timestamps.popleft()
    if len(query_timestamps) >= MAX_QUERIES:
        return True
    query_timestamps.append(now)
    return False
