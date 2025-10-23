import os
import re
import stat
import time
import platform
import subprocess
import urllib.request

CLOUDFLARE_DIST = {
    "cloudflared-fips-linux-amd64": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-fips-linux-amd64",
    "cloudflared-linux-386": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-linux-386",
    "cloudflared-linux-amd64": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-linux-amd64",
    "cloudflared-linux-arm": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-linux-arm",
    "cloudflared-linux-arm64": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-linux-arm64",
    "cloudflared-linux-armhf": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-linux-armhf",
    "cloudflared-windows-386.exe": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-windows-386.exe",
    "cloudflared-windows-amd64.exe": "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-windows-amd64.exe"
}

# Hmm... probably would move this into a single script later? IDK tho.
# I love working on projects like these, but it's still stressful, y'know?

def get(verbose=False):
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("i386", "i686", "x86"):
        arch = "386"
    elif machine in ("armv7l", "armv6l"):
        arch = "arm"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    if verbose: 
        print(f"* Operating system: {system.title()}")
        print(f"* Architecture: {arch}")

    if system == "windows":
        key = f"cloudflared-windows-{arch}.exe"
    elif system == "linux":
        key = f"cloudflared-linux-{arch}"
    elif system == "darwin":
        # Really?
        key = "cloudflared-linux-amd64"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    url = CLOUDFLARE_DIST.get(key)
    if not url:
        raise RuntimeError(f"No matching distribution for {system}/{arch}")

    if os.path.exists(key):
        if verbose:
            print(f"* File \"{key}\" already exists")
    else:
        if verbose:
            print(f"* Downloading \"{key}\" from \"{url}\"")
        urllib.request.urlretrieve(url, key)
        os.chmod(key, os.stat(key).st_mode | stat.S_IEXEC)

    return os.path.abspath(key)

def fetchurl(proc, timeout=15):
    url_regex = re.compile(r"https?://[a-z0-9\-]+\.trycloudflare\.com", re.I)
    start = time.time()

    if proc.stdout is None:
        raise ValueError("Process must be started with stdout=subprocess.PIPE")

    for line in iter(proc.stdout.readline, ""):
        if proc.poll() is not None or (time.time() - start) > timeout:
            break

        match = url_regex.search(line)
        if match:
            return match.group(0)

    return None

def start(url="http://localhost:16461/", verbose=True):
    cloudflared = get(verbose)
    cmd = [cloudflared, "tunnel", "--url", url]

    creationflags = 0
    start_new_session = False
    if os.name == "posix":
        start_new_session = True
    elif os.name == "nt":
        creationflags = (0x00000008 | 0x00000200)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=start_new_session,
        creationflags=creationflags,
        text=True
    )

    tunnel = fetchurl(proc, timeout=20)
    return proc, tunnel

if __name__ == "__main__":
    get(verbose=True)