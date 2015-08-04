# translate-extension

## Develop

The server is developed for Python 2.7. Virtualenv is not necessary but is nice to create a separate Python environment for installing just the modules needed for the server.
```
virtualenv serverenv
source serverenv/bin/activate
```

Then, install required packages:
```
pip install -r requirements.txt
```

Then, run the server:
```
python server.py
```

Install the extension in Chrome, then click Translate. Watch the server output to see data is being received and sent to the API. Click Stop to just wait for a response.