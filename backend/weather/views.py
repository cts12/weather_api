"""
An API for users to collect weather data abotu future forecasts
"""
from django.shortcuts import render
from backend import settings
from datetime import datetime
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from serializers import WeatherSerializer
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import BarChart
import pyowm
import time


@api_view(['GET'])
def get_weather(_, city, start, end):
    """
    Return median, mean, min, max of temperature and humidity over given time
    """
    # Set up object which connects to teh open weather API
    owm = pyowm.OWM(settings.OWM_API_KEY)

    # assumes local time is used
    sdt, edt = get_datetime(start, end)
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
def get_weather_specific(_, city, start, start_time, end, end_time):
    """
    Return median, mean, min, max of temperature and humidity over given time
    Allowing for more specific time
    """
    # Set up object which connects to teh open weather API
    owm = pyowm.OWM(settings.OWM_API_KEY)
    sdt, edt = get_datetime_specific(start, start_time, end, end_time)

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
def get_barchart_specific(request, city, start, start_time, end, end_time):
    """
    Renders a barchart for weather data in teh specified time period
    """
    owm = pyowm.OWM(settings.OWM_API_KEY)
    sdt, edt = get_datetime_specific(start, start_time, end, end_time)

    response = check_arg_errors(sdt, edt)
    if response:
        return response
    return render_bar_chart(request, sdt, edt, owm, city)

@api_view(['GET'])
def get_barchart(request, city, start, end):
    """
    Renders a barchart for weather data in the specified time period
    """
    owm = pyowm.OWM(settings.OWM_API_KEY)
    sdt, edt = get_datetime(start, end)

    response = check_arg_errors(sdt, edt)
    if response:
        return response
    return render_bar_chart(request, sdt, edt, owm, city)

def render_bar_chart(request, sdt, edt, owm, city):
    """
    Returns the rendered barcharts
    """
    final_stats = get_weather_stats(sdt, edt, owm, city)
    temp_data = generate_barchart_data(final_stats,\
                                        'Temperature (Kelvin)', 'temp')
    humid_data = generate_barchart_data(final_stats,\
                                        'Humidity (heat index)', 'humid')
    temp_data = SimpleDataSource(data=temp_data)
    humid_data = SimpleDataSource(data=humid_data)
    temp_chart = BarChart(temp_data)
    humid_chart = BarChart(humid_data)
    context = {
               'humid_chart' : humid_chart,
               'temp_chart' : temp_chart
              }
    return render(request, 'weather/barchart.html', context)

def generate_barchart_data(final_stats, ident, measure):
    """
    Generates data compatible with graphos graphing library
    """
    minim = final_stats['min_'+measure]
    maxim = final_stats['max_'+measure]
    mean = final_stats['mean_'+measure]
    median = final_stats['median_'+measure]
    val = 'Heat Index'
    if measure == 'temp':
        val = 'Kelvin'
    data = [[ident, 'max '+ident, 'min '+ident,\
              'median '+ident, 'mean '+ident],
            ['Forecast', maxim, minim, median, mean]
           ]
    return data

def get_datetime_specific(start, start_time, end, end_time):
    """
    Return datetime object of start and end times
    """
    spec_start = start + '-' + start_time
    spec_end = end + '-' + end_time
    sdt = datetime.strptime(spec_start, '%d-%m-%Y-%H-%M')
    edt = datetime.strptime(spec_end, '%d-%m-%Y-%H-%M')
    return sdt, edt


def get_datetime(start, end):
    """
    Gets datetime when only the dates are specified
    """
    sdt = datetime.strptime(start, '%d-%m-%Y')
    edt = datetime.strptime(end, '%d-%m-%Y')
    return sdt, edt

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

    # These are all forms of malformed arguments
    if sdt < now or edt < now:
        return Response('Only returns forecasts', status.HTTP_400_BAD_REQUEST)

    if edt > in_fourteen_days or sdt > in_fourteen_days:
        return Response('There are no readings beyond 14 days',\
                          status.HTTP_400_BAD_REQUEST)
    if sdt > edt:
        return Response('Start date is greater than End date',\
                          status.HTTP_400_BAD_REQUEST)


def collect_data(fc, start_unix, end_unix, serial):
    """
    Serializes the collected weather data into JSON format
    """
    # Edit this function is more stats need to be collected
    # Will in future make it easier for the dev to extend this
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

    finalstats = {}
    finalstats = generate_stats(finalstats, humid_list, 'humid')
    finalstats = generate_stats(finalstats, temp_list, 'temp')
    if serial:
        serializer = WeatherSerializer(data=finalstats)
        return serializer
    else:
        return finalstats

def generate_stats(acc_stats, stat_list, measure):
    """
    Performs calculations on collected data
    """
    stat_len = len(stat_list)
    stat_list = sorted(stat_list)
    acc_stats['min_'+measure] = stat_list[0]
    acc_stats['max_'+measure] = stat_list[stat_len-1]
    acc_stats['median_'+measure] = stat_list[(stat_len-1)/2]
    acc_stats['mean_'+measure] = sum(stat_list)/stat_len

    return acc_stats


def get_serialized_data(sdt, edt, owm, city):
    """
    Serializes the incoming weather data
    """
    # Over 5 days we can make calculations every 3 hours. However if the
    # start or end date is more than 5 days we take daily readings.
    # There are no readings beyond 14 days
    fc, start_unix, end_unix = get_forecast(sdt, edt, owm, city)
    serialized = True
    serializer = collect_data(fc, start_unix, end_unix, serialized)
    return serializer

def get_weather_stats(sdt, edt, owm, city):
    """
    Returns the raw stats collected
    """
    fc, start_unix, end_unix = get_forecast(sdt, edt, owm, city)
    serialized = False
    data = collect_data(fc, start_unix, end_unix, serialized)
    return data

def get_forecast(sdt, edt, owm, city):
    """
    Connects to API and returns a forecast and its time period
    """
    now = datetime.now()
    start_unix, end_unix = get_unix_timestamps(sdt, edt)
    in_five_days = now + timedelta(days=5)
    if sdt < in_five_days and edt < in_five_days:
        fc = owm.three_hours_forecast(city)
    else:
        date_diff = edt - now
        fc = owm.daily_forecast(city, limit=date_diff.days)
    return fc, start_unix, end_unix
