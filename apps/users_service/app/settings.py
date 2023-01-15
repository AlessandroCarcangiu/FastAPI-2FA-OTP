import os


# DB
DB_URL = os.environ.get('DB_URL')

# JWT
TOKEN_SECRET_KEY = "secret_key"
TEMPORARY_TOKEN_SECRET_KEY = "temporary_secret_key"
ACCESS_TOKEN_EXPIRE = 3600
REFRESH_TOKEN_EXPIRE = 86400
TEMPORARY_TOKEN_EXPIRE = 240
JWT_ALGORITHM = "HS256"

# OTP
LOG_FILE = "./app/logs/otp-logs.txt"
