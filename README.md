# Simple Weather API
## This API uses open weather map to obtain weather information on temperature and humidity.
## Currently the weather API only performs calculations on forecasts
## The mean, max, min and median are calculated over a user specified time period.
### If the time period specified is within 5 days we calculate these stats using 3 hourly forecasts.
### However if the end date is beyond 5 days, it calculates these stats using daily forecasts.
