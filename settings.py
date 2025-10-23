# settings.py
# Small configuration script

HOST = "0.0.0.0"
PORT = 16461

# Having this option set to False means it will only run locally
# When set to True, a temporary Cloudflare tunnel will make it accessible publically
CLOUDFLARE_TUNNEL = True

# The directory in which uploaded files will be saved in
UPLOAD_DIR = "./data/"

# MAKE SURE IT EXISTS BRUH
import os
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allow querying uploaded files
ALLOW_LISTING = True

# Allow downloading uploaded files
ALLOW_DOWNLOAD = True
