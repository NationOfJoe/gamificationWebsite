import os
import requests
import json
from .constants import *


class CalcHandler():
    def __init__(self):
        self.rest_session = requests.session()
        self.timestamp = get_the_time()
