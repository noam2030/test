# Hello World

A minimal Python web app (standard library only).

Run locally:

    python app.py          # http://localhost:8080
    PORT=3000 python app.py

With Docker:

    docker build -t hello .
    docker run -p 8080:8080 hello
