from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .views import *
from datetime import timedelta, datetime

# Create your tests here.
class WeatherAPITests(TestCase):
    """
    Tests that there are appropriate responses from the API
    """
    city = 'London'
    now = datetime.now()

    def test_error_when_start_gt_end(self):
        """
        Tests to see it errors if the start time is greater than end time
        """
        in_five_days = self.now + timedelta(days=5)
        in_three_days = self.now + timedelta(days=3)
        start = in_five_days.strftime('%d-%m-%Y')
        end = in_three_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertEquals(400, response.status_code)


    def test_error_when_start_gt_end_close(self):
        """
        Checks it errors if time difference is close
        """
        in_three_days = self.now + timedelta(days=3)
        start = in_three_days.strftime('%d-%m-%Y')
        end = in_three_days.strftime('%d-%m-%Y')
        start_time = '12-21'
        end_time = '12-20'
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + start_time
        api_url += '/' + end + '/' + end_time
        request = factory.get(api_url, format='json')
        response = get_weather_specific(request, self.city, start,\
                                 start_time, end, end_time)
        response.render()
        self.assertEquals(400, response.status_code)


    def test_end_too_far_in_future(self):
        """
        Check it errors if we read to far into the future
        """
        in_three_days = self.now + timedelta(days=3)
        in_fifteen_days = self.now + timedelta(days=15)
        start = in_three_days.strftime('%d-%m-%Y')
        end = in_fifteen_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertEquals(400, response.status_code)


    def test_start_too_far_in_future(self):
        """
        Check it errors if we read to far into the future
        """
        in_three_days = self.now + timedelta(days=3)
        in_fifteen_days = self.now + timedelta(days=15)
        start = in_fifteen_days.strftime('%d-%m-%Y')
        end = in_three_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertEquals(400, response.status_code)


    def test_error_if_start_in_past(self):
        """
        We cannot read historial data, so errors if start in past
        """
        back_one_day = self.now - timedelta(days=1)
        in_three_days = self.now - timedelta(days=3)
        start = back_one_day.strftime('%d-%m-%Y')
        end = in_three_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertEquals(400, response.status_code)


    def test_error_if_end_and_start_in_past(self):
        """
        We cannot read historial data, so errors if start in past
        """
        back_one_day = self.now - timedelta(days=1)
        back_three_days = self.now - timedelta(days=3)
        start = back_three_days.strftime('%d-%m-%Y')
        end = back_one_day.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertEquals(400, response.status_code)


    def test_well_formed_data_daily_forecast(self):
        """
        Check all appropriate fields are present for daily forecast
        """
        in_three_days = self.now + timedelta(days=3)
        in_ten_days = self.now + timedelta(days=10)
        start = in_three_days.strftime('%d-%m-%Y')
        end = in_ten_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertIsNotNone(response.data.get('min_temp'))
        self.assertIsNotNone(response.data.get('max_temp'))
        self.assertIsNotNone(response.data.get('median_temp'))
        self.assertIsNotNone(response.data.get('mean_temp'))
        self.assertIsNotNone(response.data.get('min_humid'))
        self.assertIsNotNone(response.data.get('max_humid'))
        self.assertIsNotNone(response.data.get('median_humid'))
        self.assertIsNotNone(response.data.get('mean_humid'))
        self.assertEquals(200, response.status_code)


    def test_well_formed_data_3_hourly_forecast(self):
        """
        Check all appropriate fields are present for 3 hour forecast
        """
        in_three_days = self.now + timedelta(days=3)
        in_four_days = self.now + timedelta(days=4)
        start = in_three_days.strftime('%d-%m-%Y')
        end = in_four_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        self.assertIsNotNone(response.data.get('min_temp'))
        self.assertIsNotNone(response.data.get('max_temp'))
        self.assertIsNotNone(response.data.get('median_temp'))
        self.assertIsNotNone(response.data.get('mean_temp'))
        self.assertIsNotNone(response.data.get('min_humid'))
        self.assertIsNotNone(response.data.get('max_humid'))
        self.assertIsNotNone(response.data.get('median_humid'))
        self.assertIsNotNone(response.data.get('mean_humid'))
        self.assertEquals(200, response.status_code)


    def test_min_always_less_equal_to_max(self):
        """
        Check all appropriate fields are present for 3 hour forecast
        """
        in_three_days = self.now + timedelta(days=3)
        in_four_days = self.now + timedelta(days=4)
        start = in_three_days.strftime('%d-%m-%Y')
        end = in_four_days.strftime('%d-%m-%Y')
        factory = APIRequestFactory()
        api_url = '/' + self.city + '/' + start + '/' + end
        request = factory.get(api_url, format='json')
        response = get_weather(request, self.city, start, end)
        response.render()
        ltt = response.data.get('min_temp') <= response.data.get('max_temp')
        lth = response.data.get('min_humid') <= response.data.get('max_humid')
        self.assertTrue(ltt)
        self.assertTrue(lth)
        self.assertEquals(200, response.status_code)
