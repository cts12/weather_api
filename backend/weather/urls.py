from django.conf.urls import patterns, url
from . import views

urlpatterns = [
        url(r'(?P<city>[a-zA-Z]+(?:[\-][a-zA-Z]+)*)/'\
              '(?P<start>(0[1-9]|[1-2][0-9]|3[0-1])-[0-9][0-9]-[0-9]+)/'\
              '(?P<end>(0[1-9]|[1-2][0-9]|3[0-1])-[0-9][0-9]-[0-9]+)/$',
                                                        views.get_weather),
        url(r'(?P<city>[a-zA-Z]+(?:[\-][a-zA-Z]+)*)/'\
              '(?P<start>(0[1-9]|[1-2][0-9]|3[0-1])-[0-9][0-9]-[0-9]+)/'\
              '(?P<start_time>[0-9][0-9]-[0-9][0-9])/'\
              '(?P<end>(0[1-9]|[1-2][0-9]|3[0-1])-[0-9][0-9]-[0-9]+)/'\
              '(?P<end_time>[0-9][0-9]-[0-9][0-9])/$',\
                                               views.get_weather_specific),
]
