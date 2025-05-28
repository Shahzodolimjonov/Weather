from django.urls import path
from .views import WeatherView, SearchStatsAPIView, CityAutocompleteAPIView, UserLastSearchAPIView

urlpatterns = [
    path('forecast/', WeatherView.as_view(), name='weather-forecast'),
    path('search-stats/', SearchStatsAPIView.as_view(), name='search-stats'),
    path('autocomplete/', CityAutocompleteAPIView.as_view(), name='city-autocomplete'),
    path('last-searches/', UserLastSearchAPIView.as_view(), name='last-searches'),
]
