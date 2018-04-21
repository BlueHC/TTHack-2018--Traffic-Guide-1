import urllib.request
import urllib.parse
import json

def alternativeTransportDistance(originLat, originLong, destinationLat, destinationLong, transportMode):
    # transport Mode can be either 'walking', 'bicycling', 'driving'
    baseurl = 'https://maps.googleapis.com/maps/api/directions/json?'
    origin = 'origin=' + str(originLat) + ',' + str(originLong) + '&'
    destination = 'destination=' + str(destinationLat) + ',' + str(destinationLong) + '&'
    mode = 'mode=' + transportMode + '&'
    key = 'key=AIzaSyAuCXKqX1w2_pL5UoM02J81a5PIDx2sh9o'

    url = baseurl + origin + destination + mode + key

    f = urllib.request.urlopen(url)
    payload = f.read().decode('utf-8')
    payloadjson = json.loads(payload)

    # print(payloadjson['routes'][0]['legs'][0]['distance']['text'])
    # print(payloadjson['routes'][0]['legs'][0]['duration']['text'])

    result = {'distanceInMeters': payloadjson['routes'][0]['legs'][0]['distance']['value'],
              'durationInSeconds': payloadjson['routes'][0]['legs'][0]['duration']['value']}

    return result
