import urllib.request
import urllib.parse
import json

def sharingMobilityAroundLocation(latitude, longitude):
    # Get available sharing mobility around the given location
    # Information is returned as a 3-tuple: latitude, longitude, TypeName
    baseurl = 'https://mymobilitymap.de/mappables?reservations=1&small=false&'
    latString = 'lat=' + str(latitude) + '&'
    lonString = 'lon=' + str(longitude)
    url = baseurl + latString + lonString

    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    result = []

    numberStations = len(payloadjson['sharables'])
    
    for i in range(0, numberStations):
        if payloadjson['sharables'][i]['type_name'] != 'Call a Bike':
            resultLat = payloadjson['sharables'][i]['latitude']
            resultLon = payloadjson['sharables'][i]['longitude']
            resultTypeName = payloadjson['sharables'][i]['type_name']
            resultTuple = (resultLat, resultLon, resultTypeName)
            result.append(resultTuple)

    return result
