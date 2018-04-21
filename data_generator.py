import pandas as pd
import weatherApi
from route_coordinate_mapping import HVVCoordinateMapper


class DataGenerator:
    """
    Features:
    (static) modal split: Fahrrad, Fuß, Auto?
    Anzahl Fahrradstationen in 1km?
    Anzahl Bus-/Bahnstationen in der Nähe (Richtung?)
    Destination Proximity(je näher -> mehr Fuß/Fahrrad)
    Wetter (Temperatur, Niederschlagswahrscheinlichkeit)
    """

    def __init__(self):
        self.mapper = HVVCoordinateMapper()
        pass

    def bike_probabilities_for_weather(self, weather):
        id = weather["WeatherTypeID"]
        temperature = weather["TemperatureInKelvin"] - 273.15
        # see https://openweathermap.org/weather-conditions
        if 200 <= id <= 300:
            bike_probability = 0
        elif id in [800, 801, 951, 952, 953]:
            bike_probability = 0.4
        elif id in [802, 803, 804, 954, 955, 701, 741, 600] or 300 <= id <= 311:
            bike_probability = 0.3
        elif 312 <= id <= 321:
            bike_probability = 0.2
        elif id in [500, 501, 601, 615, 616, 721]:
            bike_probability = 0.1
        else:
            bike_probability = 0
        # temperature adjustment
        if temperature < 5 or temperature > 30:
            bike_probability = bike_probability * 0
        elif 15 < temperature < 25:
            bike_probability = bike_probability * 1.2
        return bike_probability

    def get_foot_prob(self, weather, distance):
        base_prob = 1 - (distance * 200)
        return base_prob * self.bike_probabilities_for_weather(weather)

    def probable_destination(self):
        df = pd.read_csv(filepath_or_buffer="data/Hackathon.csv", delimiter=";")

    def generate_features_for_dest(self, start_station, dest_station):
        """
        Generates
        :param start_station:
        :param dest_station:
        :return:
        """
        weather = weatherApi.currentWeatherData()
        bike_prob = self.bike_probabilities_for_weather(weather)
        lat1, lon1 = self.mapper.stop_to_coordinates(start_station)
        bike_stations = self.mapper.bike_stations_in_range(lat1, lon1)
        lat2, lon2 = self.mapper.stop_to_coordinates(dest_station)
        dest_distance = self.mapper.get_distance(lat1, lon1, lat2, lon2)
        foot_prob = self.get_foot_prob(weather, dest_distance)

    def generate_modal_split(self, start, dest):
        following_stations = self.get_stations_on_route(start, dest)

    def get_stations_on_route(self, start, dest):
        return []

    def dummy_bus_data(self):
        pass

    def dummy_sub_data(self):
        pass


if __name__ == "__main__":
    gen = DataGenerator()
