from rest_framework.test import APITestCase
from django.urls import reverse
from weather.models import SearchHistory
from django.core.cache import cache


class WeatherAPITestCase(APITestCase):

    def setUp(self):
        cache.clear()

    def test_forecast_valid_city(self):
        url = reverse('weather-forecast')
        response = self.client.post(url, {'city': 'Tashkent'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('current_weather', response.data)

    def test_forecast_invalid_city(self):
        url = reverse('weather-forecast')
        response = self.client.post(url, {'city': 'invalidcityname123'}, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)

    def test_forecast_without_city(self):
        url = reverse('weather-forecast')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_forecast_caching(self):
        city = "Tashkent"
        url = f"/api/forecast/?city={city}"

        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['source'], 'api')

        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['source'], 'cache')


class SearchStatsAPITestCase(APITestCase):

    def test_search_stats_empty(self):
        url = reverse('search-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_search_stats_with_data(self):
        SearchHistory.objects.create(user_ip='127.0.0.1', city='Tashkent', count=5)
        SearchHistory.objects.create(user_ip='127.0.0.1', city='Bukhara', count=2)

        url = reverse('search-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        cities = [item['city'] for item in response.data]
        self.assertIn('Tashkent', cities)
        self.assertIn('Bukhara', cities)
