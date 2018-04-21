
class ModalSplit:

    def __init__(self, kfz, opvn, bike, foot):
        self.kfz = kfz
        self.opvn = opvn
        self.bike = bike
        self.foot = foot

class DisruptionModel:

    def __init__(self, modalSplit, bikeData, weatherData, opvnData):
        self.modalSplit = modalSplit
        self.bikeData = bikeData
        self.weatherData = weatherData
        self.opvnData = opvnData

    def get_distribution(self, location, direction, time):
        weather = get_weather(location, time)
        availableBikes = get_available_bikes(location, time)
        availableCars = get_available_cars(location, time) 
        probableDestination = get_probable_destination(location, time, direction)
        destinationProximity = get_destination_proximity(probableDestination)
        altOpvn = get_alternative_opvn(location, time, probableDestination, direction)
        return get_distribution(weather, availableBikes, availableCars, destinationProximity, altOpvn)

    def get_distribution(self, weather, availableBikes, availableCars, destinationProximity, altOpvn):
        """

        parameters: 
            weather: [Weather, Temperature]
            availableBikes: [[distance, avail_bikes], ...]
            availableCars: [[distance, avail_cars], ...]
            destinationProximity: proximity
            altOpvn: [[alt1, noSeats], [alt2, noSeats], ...]
        
        also factor in self.modalSplit        
        """
        return 0

    def get_weather(self, location, time):
        """
        
        use weatherData to get weather for given point in time

        Weather scale: ?
        Temperature scale: ice cold - cold - neutral - warm - hot

        return:
            [int, int] -> Weather, Temperature
        """
        return 0

    def get_available_bikes(self, location, time):
        """

        takes into account both the distance to the nearest bike sharing station(s) 
        as well as the available bikes

        #TODO: Possible to introduce a threshold for distance of bike stations and take all available bikes of these stations
               or: increasing distance -> scale down available bikes
        return:
            [[distance, avail_bikes], ...]
        """
        return [[0, 0]]

    def get_available_cars(self, location, time):
        """

        return:            
            [[distance, avail_cars], ...]
        """
        return [[0, 0]]

    def get_probable_destination(self, location, time, direction):
        """
        
        use opvnData to guess the probable destination for the given location and time
        """
        return 0

    def get_destination_proximity(self, probableDestination):
        return 0
        
    def get_alternative_opvn(self, location, time, probableDestination, direction): #TODO: direction might be useless
        """
        
        use HVV network to extract alternatives for location, time and destination
        
        return:
            [[alt1, noSeats], [alt2, noSeats], ...]
        """
        return [[0, 0]]


    # für jede Folge-Station auf der Route: destProximity und und altOpvn -> und Prozente berechnen und dann gewichtet verrechnen
    # 
