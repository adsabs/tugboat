import os
 
APP_NAME = 'tugboat' 
LOG_DIR = '/tmp'

bind = "unix:/app/gunicorn.sock"
workers = 6
max_requests = 200
max_requests_jitter = 15
preload_app = True
chdir = os.path.dirname(__file__)
daemon = False
debug = False
errorlog = '{}/{}.error.log'.format(LOG_DIR, APP_NAME)
accesslog = '{}/{}.access.log'.format(LOG_DIR, APP_NAME)
loglevel = "info"
