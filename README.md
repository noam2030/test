# test

A small, animated "Hello World!" web app served by a dependency-free Python HTTP server and deployed to Google Cloud Run.

## Features

- Glassmorphism card on an animated gradient background, with floating blobs and a particle network
- Typewriter text that cycles through messages
- Live clock and date
- 🎉 Celebrate button (or click the 👋) for confetti, plus a celebration counter saved in `localStorage`
- Light/dark theme toggle, saved between visits
- 3D tilt effect on the card that follows the mouse (turned off when the user prefers reduced motion)
- A text area with a "Click me" button

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Minimal HTTP server using only the Python standard library |
| `index.html` | The whole front end (HTML, CSS and JavaScript in one file) |
| `Dockerfile` | Container image for Cloud Run |
| `.github/workflows/deploy.yml` | GitHub Actions workflow that deploys to Cloud Run on every push to `main` |

## Routes

- `GET /` or `/index.html`: the app
- `GET /healthz`: health check, returns `ok`
- Any other path returns a 404

## Running locally

Requires Python 3.

```sh
python app.py
# open http://localhost:8080
```

Set the `PORT` environment variable to use a different port:

```sh
PORT=3000 python app.py
```

### With Docker

```sh
docker build -t test .
docker run -p 8080:8080 test
```

## Deployment

Every push to `main` runs the GitHub Actions workflow, which deploys the app to Cloud Run (service `test`, region `us-central1`). The workflow needs a `GCP_SA_KEY` repository secret containing the service account credentials.
