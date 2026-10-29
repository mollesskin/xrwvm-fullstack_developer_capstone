import json
import logging
from datetime import datetime

import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import CarModel
from .restapis import analyze_review_sentiments, get_request, post_review

logger = logging.getLogger(__name__)


def _body(request):
    try:
        return json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _backend_error(exc):
    logger.exception("Backend request failed")
    return JsonResponse({"status": 502, "error": str(exc)}, status=502)


@csrf_exempt
@require_POST
def login_user(request):
    data = _body(request)
    if data is None:
        return JsonResponse({"status": 400, "error": "Invalid JSON"}, status=400)
    username = data.get("userName", "").strip()
    user = authenticate(request, username=username, password=data.get("password", ""))
    if user is None:
        return JsonResponse({"status": 401, "error": "Invalid credentials"}, status=401)
    login(request, user)
    return JsonResponse({
        "status": "Authenticated", "userName": user.username,
        "firstName": user.first_name, "lastName": user.last_name,
    })


@require_GET
def logout_user(request):
    logout(request)
    return JsonResponse({"status": 200, "message": "Logged out"})


@csrf_exempt
@require_POST
def registration(request):
    data = _body(request)
    if data is None:
        return JsonResponse({"status": 400, "error": "Invalid JSON"}, status=400)
    username = data.get("userName", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not username or not email or len(password) < 8:
        return JsonResponse({"status": 400, "error": "Username, email and an 8-character password are required"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"status": 409, "error": "Username already exists"}, status=409)
    user = User.objects.create_user(
        username=username, email=email, password=password,
        first_name=data.get("firstName", "").strip(),
        last_name=data.get("lastName", "").strip(),
    )
    login(request, user)
    return JsonResponse({
        "status": 200, "userName": user.username,
        "firstName": user.first_name, "lastName": user.last_name,
    })


@require_GET
def get_dealerships(request, state=None):
    try:
        endpoint = "fetchDealers" if not state or state == "All" else f"fetchDealers/{state}"
        return JsonResponse({"status": 200, "dealers": get_request(endpoint)})
    except (requests.RequestException, ValueError) as exc:
        return _backend_error(exc)


@require_GET
def get_dealer_details(request, dealer_id):
    try:
        return JsonResponse({"status": 200, "dealer": get_request(f"fetchDealer/{dealer_id}")})
    except (requests.RequestException, ValueError) as exc:
        return _backend_error(exc)


@require_GET
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
        for review in reviews:
            try:
                review["sentiment"] = analyze_review_sentiments(review.get("review", ""))
            except (requests.RequestException, ValueError):
                review["sentiment"] = "neutral"
        reviews.sort(key=lambda item: item.get("time", ""), reverse=True)
        return JsonResponse({"status": 200, "reviews": reviews})
    except (requests.RequestException, ValueError) as exc:
        return _backend_error(exc)


@require_GET
def get_cars(request):
    cars = CarModel.objects.select_related("car_make").order_by("car_make__name", "name")
    return JsonResponse({"status": 200, "CarModels": [
        {"CarMake": car.car_make.name, "CarModel": car.name, "CarYear": car.year}
        for car in cars
    ]})


@csrf_exempt
@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 401, "error": "Log in to post a review"}, status=401)
    data = _body(request)
    if data is None:
        return JsonResponse({"status": 400, "error": "Invalid JSON"}, status=400)
    required = ("dealership", "review", "purchase_date", "car_make", "car_model", "car_year")
    if any(not data.get(key) for key in required):
        return JsonResponse({"status": 400, "error": "All review fields are required"}, status=400)
    try:
        review = {
            "user_id": request.user.id,
            "name": request.user.get_full_name() or request.user.username,
            "dealership": int(data["dealership"]),
            "review": str(data["review"]).strip(),
            "time": datetime.now().isoformat(timespec="seconds"),
            "purchase": bool(data.get("purchase", False)),
            "purchase_date": data["purchase_date"],
            "car_make": data["car_make"],
            "car_model": data["car_model"],
            "car_year": int(data["car_year"]),
        }
        return JsonResponse({"status": 200, "review": post_review(review)})
    except (ValueError, TypeError, requests.RequestException) as exc:
        return _backend_error(exc)
