# DataSave

Tiny HTTP-based file host you can run anywhere. (Todo: Change the name) Intended to be used in small experimental or educational projects to sync data on the cloud to your data locally.

For example: Save model training checkpoints locally from Google Colab to avoid loosing them. (I know it's not your first time loosing hours of compute to an expired session)

## Usage

The project has no external dependencies that you need to install. Just follow these instructions and you're good to go (Intended cross-platform):

1. Run the file host server locally on your computer:
    ```shell
    $ git clone https://github.com/nickkipshidze/datasave
    $ cd datasave
    $ python main.py
    ```
    The script will download the Cloudflared binary in the working directory. (this doesn't install anything on your computer, all files are contained within ./datasave/ directory) After the download is complete, a Cloudflared temporary tunnel is started, and you should see an output like this:
    ```shell
    $ python main.py
    * Starting cloudflare tunnel...
    * Operating system: Linux
    * Architecture: amd64
    * Downloading "cloudflared-linux-amd64" from "https://github.com/cloudflare/cloudflared/releases/download/2025.10.0/cloudflared-linux-amd64"
    * Cloudflare tunnel started: https://buys-mighty-year-enjoyed.trycloudflare.com
    * HTTP server started
    ```

2. Copy the silly Cloudflare tunnel address:
    ```shell
    * Cloudflare tunnel started: https://buys-mighty-year-enjoyed.trycloudflare.com
    ```
    You will be using that address to upload files to it. In my case it is `https://buys-mighty-year-enjoyed.trycloudflare.com` but the name is randomly generated every time, for you it'll be different. You're expecting something like `https://<RANDOM_PHRASE>.trycloudflare.com` and this address is available publically everywhere!

3. Now that you have your Cloudflare tunnel address, you can use it to upload files to it from anywhere. Here's an example on how to upload a file to it with Python requests:
    ```python
    import requests

    filename = "<YOUR_FILE_NAME_HERE>"

    with open(filename, "rb") as f:
        response = requests.post("https://<RANDOM_PHRASE>.trycloudflare.com/up", files={"file": f})
        
    print(response.text)
    ```
    Just be sure to replace that address with the one that you got. Scroll down for more usage examples.

## Usage: For LLM users

After following the quick setup guide from above, you can simply paste the following prompt to your LLM to let it use the tool for you:

**Example: PyTorch training loop checkpoint saves**
```
I am using a file managment tool that is hosted at <YOUR_CLOUDFLARE_TUNNEL_URL>

When you need to save a file (like model weights or logs), use the endpoint POST /up with the file, and to retrieve it, use GET /down?f=filename. Use standard HTTP file uploads with multipart/form-data.”

Use the following helper function for uploads:

import requests
def upload_file(filename: str, address: str):
    url = address.rstrip("/") + "/up"
    with open(filename, "rb") as f:
        response = requests.post(url, files={"file": f})
    return response

Alternatively you can use CURL for file uploads:

$ curl -X POST -F "file=@filename.txt" <YOUR_CLOUDFLARE_TUNNEL_URL>

In case of successful upload request, you will get a plain text response: `File {filename} uploaded successfully.` Otherwise you will receive `Content-Type must be multipart/form-data` or `No file found in request`.

Additionally you can use the following endpoints for more complex tasks:
- `GET /list` - List uploaded files (Returns a JSON list of filenames)
- `GET /down?f=filename` - Download an uploaded file

Feel free to implement your own error handling.

With these instructions in mind. Use the file managment server for the given task: Write a simple PyTorch training loop with checkpoints.
```

Feel free to modify the prompt as needed.

> Side note: The address changes every time like I said, so make sure to update them in your scripts each time you start the server.