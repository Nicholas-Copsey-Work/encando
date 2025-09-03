# System Requirements

* Python >= v3.13.2 installed
* NPM >= v11.5.2 installed
* Ubuntu/Debian system, or gitbash on Windows.

# Installation

1. Extract the zip file into a directory
2. CD to the directory that the zip file was decompressed into.
3. Run `python -m venv ./venv`
4. Active Virtual Environment
    * Windows
        * Run `source venv/Scripts/activate` in the terminal.
    * Ubuntu/Debian
        * Run `source venv/bin/activate` in the terminal.
4. Run `python -m pip install -r backend/requirements.txt` in the terminal.
5. Run `npm i` in the terminal.
4. Run `npm run test` in the terminal.
5. Go to `http://localhost:5000` and input html.

    * An example is below 
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Welcome Page</title>
        <style>
            .hidden-text { display: none; }
        </style>
    </head>
    <body>
    <h1>Welcome!</h1>
        <p style="color: #ccc;">This is a sample page.</p>
            <button onclick="alert('Submitted')">Submit</button>
        <div class="hidden-text">Hidden instructions</div>
    </body>
</html>
```

# Notable Features

Dynamically importing all API Paths
- This application will dynamically require all api path files and add them to the flask application so that they are accessible.

API hosting the frontend.
- The application currently hosts it's own frontend, this can be easily modified later if the scale of the service becomes great enough to require a separate front end and backend.
- The file structure it built in a way that it is very easy to transplant the frontend into a service like AWS S3 to serve the static files independently.