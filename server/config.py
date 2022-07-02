

# MINIO_ENDPOINT = 'minio:9000'
MINIO_ENDPOINT = '127.0.0.1:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_BUCKET_NAME = 'imaging'

# MONGO_ENDPOINT = 'mongodb://admin:admin@mongodb:27017/imaging'
MONGO_ENDPOINT = 'mongodb://admin:admin@127.0.0.1:27017/imaging'
MONGO_DATABASE = 'imaging'


AUTH_ACCESS_TOKEN_EXPIRE_DAYS = 365
AUTH_ALGORITHM = 'HS256'
AUTH_SECRET_KEY = '6e7603195a6463ac16babb3b8542eb4a8ed3a8b104ea3367'

PUBLIC_IP = 'http://127.0.0.1:8888'

# waiting time for the code to sleep after loading the model to memory (in seconds)
WAIT_TIME_AFTER_LOADING_MODEL = 10
