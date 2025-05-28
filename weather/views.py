import requests
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

from weather.models import SearchHistory
from weather.utils import log_search, get_client_ip


# где пользователь вводит название города и отображается погода
class WeatherView(APIView):

    def get(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response({"error": "Требуется ввести название города (city) "
                                      "формат: query_param (http://127.0.0.1:8181/api/forecast/?city=Berlin)"},
                            status=status.HTTP_400_BAD_REQUEST)
        return self.get_weather_data(city, request)

    def post(self, request):
        city = request.data.get('city')
        if not city:
            return Response({"error": "Требуется ввести название города (city) формат: data"},
                            status=status.HTTP_400_BAD_REQUEST)
        return self.get_weather_data(city, request)

    def get_weather_data(self, city, request):
        city_key = city.strip().lower()
        cached_data = cache.get(city_key)
        if cached_data:
            log_search(request, city_key)
            return Response({"source": "cache", **cached_data})

        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url).json()

        if "results" not in geo_response or not geo_response["results"]:
            return Response({"error": "Shahar topilmadi"},
                            status=status.HTTP_404_NOT_FOUND)

        location = geo_response['results'][0]
        lat, lon = location['latitude'], location['longitude']

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_response = requests.get(weather_url).json()
        weather_data = weather_response.get("current_weather", {})

        result = {
            "city": location["name"],
            "latitude": lat,
            "longitude": lon,
            "current_weather": {
                "temperature": weather_data.get("temperature"),
                "wind_speed": weather_data.get("windspeed"),
                "wind_direction": weather_data.get("winddirection"),
                "time": weather_data.get("time"),
                "description": (
                    f"{weather_data.get('temperature')}°C, "
                    f"ветер {weather_data.get('windspeed')} km/h "
                    f"({weather_data.get('winddirection')}°)"
                )
            }
        }

        cache.set(city_key, result, timeout=1800)
        log_search(request, city_key)

        return Response({"source": "api", **result})


# Получить статистику по всему сайту
class SearchStatsAPIView(APIView):

    def get(self, request):
        stats = (SearchHistory.objects
                 .values("city")
                 .annotate(total=Sum("count"))
                 .order_by("-total"))
        return Response(list(stats))


# API для автозаполнения
class CityAutocompleteAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {"error": "Параметр запроса q не может быть пустым. "
                          "формат: query_param (http://127.0.0.1:8181/api/autocomplete/?q=Berlin)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        db_cities_qs = (
            SearchHistory.objects.filter(city__istartswith=query)
            .values_list("city", flat=True)
            .distinct()
        )
        db_cities = list(db_cities_qs[:5])
        suggestions = [{"name": name, "country": ""} for name in db_cities]

        if len(suggestions) < 5:
            remaining = 5 - len(suggestions)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count={remaining}&language=en&format=json"
            response = requests.get(geo_url)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                existing_names = {s["name"] for s in suggestions}
                for city in results:
                    if city["name"] not in existing_names:
                        suggestions.append({
                            "name": city["name"],
                            "country": city.get("country", "")
                        })
                    if len(suggestions) >= 5:
                        break
            else:
                return Response(
                    {"error": "Произошла ошибка при обращении к внешнему API"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(suggestions)


# API для получения предыдущих запросов
class UserLastSearchAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            searches = (SearchHistory.objects
                        .filter(user=request.user)
                        .order_by("-id")
                        .values("city")
                        .distinct())
        else:
            ip = get_client_ip(request)
            searches = (SearchHistory.objects
                        .filter(user_ip=ip, user=None)
                        .order_by("-id")
                        .values("city")
                        .distinct())

        last_cities = [item["city"] for item in searches[:10]]

        return Response({"last_cities": last_cities})
