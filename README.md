# Full Stack Application Development Capstone

A car dealership portal built with Django, React, Express, MongoDB, and a Flask/VADER sentiment service. Visitors can browse and filter dealerships, inspect reviews, and see About and Contact pages. Registered users can post reviews. Django admin manages car makes and models.

## Run locally

1. Create a Python virtual environment and install `server/requirements.txt` and `server/djangoapp/microservices/requirements.txt`.
2. In `server/frontend`, run `npm ci && npm run build`.
3. In `server/database`, run `npm ci && node app.js`. MongoDB is used when available; the service falls back to bundled sample data for local development.
4. Run `python server/djangoapp/microservices/app.py` for sentiment analysis.
5. In `server`, run `python manage.py migrate`, `python manage.py seed_cars`, and `python manage.py runserver`.
6. Visit `http://127.0.0.1:8000/`.

Set `BACKEND_URL` and `SENTIMENT_ANALYZER_URL` when services run on other hosts. See `server/.env.example` for configuration. To create an admin account, run `python server/manage.py createsuperuser` and choose your own credentials.

## Containers

`docker compose up --build` starts MongoDB and all three application services. The web application is available on port 8000. The container entrypoint runs Django migrations and populates example car makes and models.

`deploy/deployment.yml` provides Kubernetes deployments, services, and data claims. Build or publish the three images under the names `dealership-web`, `dealership-api`, and `dealership-sentiment`, then create a `dealership-secrets` secret containing `django-secret-key` before applying the manifest. Change `DJANGO_ALLOWED_HOSTS` to your public hostname for a real deployment.

## Main endpoints

| Endpoint | Purpose |
| --- | --- |
| `/djangoapp/get_dealers` | List all dealerships |
| `/djangoapp/get_dealers/Kansas` | Filter dealerships by state |
| `/djangoapp/dealer/15` | Dealer details |
| `/djangoapp/reviews/dealer/15` | Dealer reviews with sentiment |
| `/djangoapp/register`, `/djangoapp/login`, `/djangoapp/logout` | User accounts |
| `/djangoapp/get_cars` | Car makes and models |
| `/djangoapp/add_review` | Post an authenticated review |

## Verification

The React production build completes, Django's system check and migrations complete, and the local API flow has been exercised from registration through posting a review and logging out. The GitHub Actions workflow repeats build and server checks and builds all three container images.
