# Sample module that imports the datetime class and time function directly.

from datetime import datetime
from time import time

def get_info():
    return (time(), datetime.utcnow())
