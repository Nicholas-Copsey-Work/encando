import sys

def versionCheck():
    VERSION_INFO = ( 3, 13, 2 )
    version_info = sys.version_info
    python_version_mismatch = False
    i = 0
    if version_info[i] < VERSION_INFO[i]:
        python_version_mismatch = True
    i += 1
    if version_info[i] < VERSION_INFO[i]:
        python_version_mismatch = True
    i += 1
    if version_info[i] < VERSION_INFO[i]:
        python_version_mismatch = True
    if python_version_mismatch:
        print("Using an outdated python version.")
        print(f"Expected v{VERSION_INFO[0]}.{VERSION_INFO[1]}.{VERSION_INFO[2]}")
        print(f"Got v{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
        exit(1)
    return

versionCheck()
import flask
import os

def getAbsolutePath(path):
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))

FRONTEND_FOLDER = getAbsolutePath(os.path.join('..', '..', 'frontend'))

app = flask.Flask(__name__, static_url_path=None)

"""API endpoints"""

from app import helpers

helpers.RegisterRoutes(app, getAbsolutePath("./routes/v1"), "/v1")

print("API Endpoints registered.")

"""Static Files"""

@app.get("/")
def index():
    return flask.send_from_directory(
        FRONTEND_FOLDER, "index.html"
    )

@app.get("/<path:filename>")
def file(filename):
    return flask.send_from_directory(
        FRONTEND_FOLDER, filename
    )

if __name__ == "__main__":
    app.run()