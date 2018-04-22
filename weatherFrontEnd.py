import urllib.request
import urllib.parse
import json
import datetime

def weatherFrontEnd():
    """
    The function returns a json with the weather data, that will be used for the frontend

    TypeIDs: https://openweathermap.org/weather-conditions
             2xx: Thunderstorm
             3xx: Drizzle
             5xx: Rain
             6xx: Snow
             7xx: Atmosphere
             800: Clear
             80x: Clouds
             90x: Extreme
             9xx: Misc
    """

    # Call for the current weather
    url = 'https://api.openweathermap.org/data/2.5/weather?q=Hamburg&APPID=b5b4fb75e69eaf5754f4412ca9700d1b'
    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    iconBaseUrl = 'http://openweathermap.org/img/w/'
    iconUrl = iconBaseUrl + str(payloadjson['weather'][0]['icon']) + '.png'

    temperatureInCelsius = int(float(payloadjson['main']['temp']) - 273.15)

    today = int(datetime.datetime.today().day)
    month = int(datetime.datetime.today().month)
    
    resultToday = {'Day': today,
                   'Month': month,
              'TemperatureInCelsius': temperatureInCelsius,
              'WeatherTypeID': payloadjson['weather'][0]['id'],
              'WeatherMain': payloadjson['weather'][0]['main'],
              'WeatherDescription': payloadjson['weather'][0]['description'],
              'WeatherIconUrl': iconUrl}

    # Call for the weather forecast
    urlForecast = 'https://api.openweathermap.org/data/2.5/forecast?q=Hamburg&units=metric&APPID=b5b4fb75e69eaf5754f4412ca9700d1b'
    g = urllib.request.urlopen(urlForecast)
    payloadForecast = g.read().decode('utf-8')
    payloadForecastJson = json.loads(payloadForecast)

    resultList = []
    
    for i in range(0, len(payloadForecastJson['list'])):

        Timestamp = datetime.datetime.fromtimestamp(
                int(payloadForecastJson['list'][i]['dt'])
            )

        if Timestamp.hour == 14:
            day = int(Timestamp.day)
            month = int(Timestamp.month)
            temperatureInCelsius = int(payloadForecastJson['list'][i]['main']['temp'])
            WeatherTypeID = payloadForecastJson['list'][i]['weather'][0]['id']
            WeatherMain = payloadForecastJson['list'][i]['weather'][0]['main']
            WeatherDescription = payloadForecastJson['list'][i]['weather'][0]['description']
            iconUrl = iconBaseUrl + str(payloadForecastJson['list'][i]['weather'][0]['icon']) + '.png'

            resultWeatherPerDay = {'Day': day,
                                   'Month': month,
                                   'TemperatureInCelsius': temperatureInCelsius,
                                   'WeatherTypeID': WeatherTypeID,
                                   'WeatherMain': WeatherMain,
                                   'WeatherDescription': WeatherDescription,
                                   'WeatherIconUrl': iconUrl}

            resultList.append(resultWeatherPerDay)

    if int(datetime.datetime.today().day) == resultList[0]['Day']:
        del resultList[0]
        del resultList[3:]
    else:
        del resultList[3:]

    resultList.insert(0,resultToday)
    resultToJson = {'items': resultList}
    resultJson = json.dumps(resultToJson)
    
    # outout to file. Not sure if it works correctly.
    # with open('weatherFrontEndJSON.txt', 'w') as outfile:
    #    json.dump(resultJson, outfile)
    
    return resultJson

print(weatherFrontEnd())





