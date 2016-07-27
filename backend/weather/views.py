from django.shortcuts import render
from backend import settings
from datetime import datetime
from datetime import timedelta
from logic import WeatherLogic
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from serializers import WeatherSerializer
import pyowm
import time


@api_view(['GET'])
def get_weather(request, city, start, end):
    """
    Return median, mean, min, max of temperature and humidity over given time
    """
    # Set up object which connects to teh open weather API
    owm = pyowm.OWM(settings.OWM_API_KEY)
    forecast = owm.daily_forecast(city)

    # assumes local time is used
    sdt = datetime.strptime(start, '%d-%m-%Y')
    edt = datetime.strptime(end, '%d-%m-%Y')
    response = check_arg_errors(sdt, edt)
    if response:
        return response
    serializer = get_serialized_data(sdt, edt, owm, city)

    if serializer.is_valid():
        return Response(serializer.data)
    else:
        return Response(serializer.errors,\
                    status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_weather_specific(request, city, start, start_time, end, end_time):
    """
    Return median, mean, min, max of temperature and humidity over given time
    Allowing for more specific time
    """
    # Set up object which connects to teh open weather API
    owm = pyowm.OWM(settings.OWM_API_KEY)

    spec_start = start + '-' + start_time
    spec_end = end + '-' + end_time
    sdt = datetime.strptime(spec_start, '%d-%m-%Y-%H-%M')
    edt = datetime.strptime(spec_end, '%d-%m-%Y-%H-%M')

    start_unix, end_unix = get_unix_timestamps(sdt, edt)
    response = check_arg_errors(sdt, edt)
    if response:
        return response
    serializer = get_serialized_data(sdt, edt, owm, city)

    if serializer.is_valid():
        return Response(serializer.data)
    else:
        return Response(serializer.errors,\
                    status.HTTP_400_BAD_REQUEST)


def get_unix_timestamps(sdt, edt):
    """
    Given two dateime objects, create unix timestamps for each
    """
    start_unix = int(time.mktime(sdt.timetuple()))
    end_unix = int(time.mktime(edt.timetuple()))
    return start_unix, end_unix

def check_arg_errors(sdt, edt):
    """
    Performs checks to see if data is malformed
    """
    now = datetime.now()
    in_fourteen_days = now + timedelta(days=14)
    print in_fourteen_days
    print edt
    if edt > in_fourteen_days:
        print 'it is greater'
    # These are all forms of malformed arguments
    if sdt < now or edt < now:
        return Response('Only returns forecasts', status.HTTP_400_BAD_REQUEST)

    if edt > in_fourteen_days or sdt > in_fourteen_days:
        print 'it is greater'
        return Response('There are no readings beyond 14 days',\
                          status.HTTP_400_BAD_REQUEST)
    if sdt > edt:
        return Response('Start date is greater than End date',\
                          status.HTTP_400_BAD_REQUEST)


def collect_serialized_data(fc, start_unix, end_unix):
    """
    Serializes the collected weather data into JSON format 
    """
    f = fc.get_forecast()
    w_list = f.get_weathers()
    temp_list = []
    humid_list = []

    for weather in w_list:
        if start_unix < weather.get_reference_time() and\
            end_unix > weather.get_reference_time():
            temp_data = weather.get_temperature()

            if 'temp' in temp_data:
                temp_list.append(temp_data['temp'])
            else:
                temp_list.append(temp_data['morn'])
                temp_list.append(temp_data['day'])
                temp_list.append(temp_data['eve'])
                temp_list.append(temp_data['night'])
                
            humid_list.append(weather.get_humidity())

    finalstats  = {}
    finalstats = generate_stats(finalstats, humid_list, 'humid')
    finalstats  = generate_stats(finalstats, temp_list, 'temp')
    serializer = WeatherSerializer(data=finalstats)
    return serializer

def generate_stats(acc_stats, stat_list, measure):

    stat_len = len(stat_list)
    stat_list = sorted(stat_list)
    print stat_list
    acc_stats['min_'+measure] = stat_list[0]
    acc_stats['max_'+measure] = stat_list[stat_len-1]
    acc_stats['median_'+measure] = stat_list[(stat_len-1)/2]
    acc_stats['mean_'+measure] = sum(stat_list)/stat_len

    return acc_stats

def get_serialized_data(sdt, edt, owm, city):
    """
    Connects to owm api and obtains weather data
    """
    # Over 5 days we can make calculations every 3 hours. However if the
    # start or end date is more than 5 days we take daily readings.
    # There are no readings beyond 14 days
    now = datetime.now()
    start_unix, end_unix = get_unix_timestamps(sdt, edt)
    in_five_days = now + timedelta(days=5)
    if sdt < in_five_days and edt < in_five_days:
        fc = owm.three_hours_forecast(city)
    else:
        date_diff = edt - now
        fc = owm.daily_forecast(city, limit=date_diff.days)

    serializer = collect_serialized_data(fc, start_unix, end_unix)
    return serializer
