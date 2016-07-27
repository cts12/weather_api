## Simple Weather API

This API uses open weather map to obtain weather information on temperature and humidity. Currently the weather API only performs calculations on forecasts

The mean, max, min and median are calculated over a user specified time period. If the time period specified is within 5 days we calculate these stats using 3 hourly forecasts. However if the end date is beyond 5 days, it calculates these stats using daily forecasts. Forecasts only predict 14 days thus if the dates are beyond this point, the API will error.

### Usage:
The application runs on your local server at 127.0.0.1:8000.
The following calls can be made to the API.
Firstly we can render a html barchart to view the aforementioned statistics, at these two following urls.
The user has a choic to make their forecast range more specific by supplying *start_time* and *end_time* arguments.

1. http://127.0.0.1:8000/v1/barchart/*city*/*start_date*/*start_time*/*end_date*/*end_time*/
2. http://127.0.0.1:8000/v1/barchart/*city*/*start_date*/*end_date*/

The user can omit the barchart from the url and obtain JSON data of the same statistics.

1. http://127.0.0.1:8000/v1/*city*/*start_date/*start_time*/*end_date*/*end_time*/
2. http://127.0.0.1:8000/v1/*city*/*start_date/*end_date*/

The format of *start_date* and *end_date* is 'day-month-year' for example '08-09-2016'. Note you must supply a '0' before single digits like '08' and '09' in this example.
The format of *start_time* and *end_time* is 'hour-minute' for example '09-30'. Note you must supply a '0' before single digits like '09' in this example. This API uses the 24 hour clock for its hour. For example '22-30' would also be a valid example.
*city* is just the name of a popular city, for example 'London'.

#### Concrete examples
The following examples will not work if the current date has surpassed these dates. However if you increase the dates to ones with in 14 days from the current time, it will return successfully.

1.http://127.0.0.1:8000/v1/barchart/London/01-07-2016/12-12/03-08-2016/20-10/

2.http://127.0.0.1:8000/v1/barchart/London/01-07-2016/12-12/03-08-2016/20-10/

3.http://127.0.0.1:8000/v1/London/01-07-2016/03-08-2016/

4.http://127.0.0.1:8000/v1/London/01-07-2016/12-12/03-08-2016/20-10/
  
#### Future
More tests can be created to make sure functionality is kept over time.
