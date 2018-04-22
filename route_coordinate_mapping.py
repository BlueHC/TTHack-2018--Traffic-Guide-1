import pandas as pd
import numpy as np
import gpxpy
import math
from sharingMobilityAPI import sharingMobilityAroundLocation


class HVVCoordinateMapper:
    def __init__(self):
        self.df = None
        self.stop_to_index = {}
        self.lat_lon_to_index = {}
        self.index_to_lat_lon = {}
        self.bike_coordinates = []
        self.stop_to_parent = {}
        self._load_bus_data()
        self._load_bike_data()

    def _load_bus_data(self, file="data/stops.txt"):
        print('Loading bus data')
        self.df = pd.read_csv(filepath_or_buffer=file, sep=",")
        for i, row in self.df.iterrows():
            # only record coordinates of 'parent stations'
            if isinstance(row["parent_station"], float) and math.isnan(row["parent_station"]):
                self.stop_to_index[row["stop_name"]] = i
                self.lat_lon_to_index[(row["stop_lat"], row["stop_lon"])] = i
                self.index_to_lat_lon[i] = (row["stop_lat"], row["stop_lon"])
            else:
                self.stop_to_parent[row["stop_id"]] = row["parent_station"]

    def _load_bike_data(self, file='data/1-StadtRAD_Hamburg_Stationen.gpx'):
        print('Loading bike data')
        with open(file, 'r') as f:
            gpx = gpxpy.parse(f)
        for p in gpx.waypoints:
            self.bike_coordinates.append((p.latitude, p.longitude))

    def stop_to_coordinates(self, stop_name):
        row = self.df.iloc[self.stop_to_index[stop_name]]
        return row["stop_lat"], row["stop_lon"]

    def coordinates_to_stop(self, latitude, longitude):
        row = self.df.iloc[self.lat_lon_to_index[(latitude, longitude)]]
        return row["stop_name"]

    @staticmethod
    def get_distance(lat1, lon1, lat2, lon2):
        """ Calculate euclidean distance between two points, defined by their latitude and longitude"""
        start_vec = np.array([lat1, lon1])
        dest_vec = np.array([lat2, lon2])
        dist = np.linalg.norm(start_vec - dest_vec)  # euclidean distance between start and destination coordinates
        return dist

    def bike_stations_in_range(self, lat_start, lon_start, range=0.008):
        bike_stations = []
        for lat, lon in self.bike_coordinates:
            dist = self.get_distance(lat_start, lon_start, lat, lon)
            if dist <= range:
                bike_stations.append((lat, lon, dist))
        return bike_stations
    
    def bus_stations_in_range(self, lat_start, lon_start, range=0.007):
        stations = []
        for name, index in self.stop_to_index.items():
            (lat, lon) = self.index_to_lat_lon[index]
            dist = self.get_distance(lat_start, lon_start, lat, lon)
            if dist <= range:
                stations.append((name, dist))
        return stations

    def cars_in_range(self, lat_start, lon_start, range=0.005):
        nearby_cars = []
        for car in sharingMobilityAroundLocation(lat_start, lon_start):
            dist = self.get_distance(lat_start, lon_start, float(car[0]), float(car[1]))
            if dist <= range:
                nearby_cars.append((float(car[0]), float(car[1]), dist))
        return nearby_cars

    def get_bike_capacity(self, lat, lon):
        bike_stations = self.bike_stations_in_range(lat, lon)
        #return sum([get_station_cap(*s[:2]) for s in bike_stations)
    
    def get_car_capacity(self, lat, lon):
        return
    
    def get_opvn_capacity(self, lat, lon):
        return
    
    def get_passenger_distribution(self, lat, lon, num_passengers, predictor, 
                                    scenarios, weights):
        """Wichtig.
        
        lat, lon - wo die Strecke ausfällt
        num_passengers - absolute Anzahl an Passagieren, die Strecke genutzt hätte
        predictor - Predictor-Objekt, welches das Modell geladen hat
        scenarios - model inputs (einer für jede mögliche Zielstation)
        weights - Gewichte für jede Zielstation (Wahrscheinlichkeiten)
        """
        distribution = predictor.predict(scenarios, weights)
        abs_distribution = distribution * num_passengers
        actual_distribution = self.get_actual_distribution(abs_distribution, lat, lon)
        return actual_distribution
    
    def get_actual_distribution(self, abs_dist, lat, lon):
        """Caps the absolute distribution at the max capacities
            
        Also returns the intended distribution for calculating the passengers
        that need to be transported by different means.
        """
        bike_capacity = self.get_bike_capacity(lat, lon)
        car_capacity = self.get_car_capacity(lat, lon)
        opvn_capacity = self.get_opvn_capacity(lat, lon)
        foot_capacity = abs_dist["foot"]
        
        deficits = {"bike_actual": min(bike_capacity, abs_dist["bike"]),
                    "car_actual": min(car_capacity, abs_dist["car"]),
                    "opvn_actual": min(opvn_capacity, abs_dist["opvn"]),
                    "foot_actual": foot_capacity}
                    
        #return (abs_distribution, capped_distribution)


if __name__ == "__main__":
    mapper = HVVCoordinateMapper()
    lat, lon = mapper.stop_to_coordinates("Bornkampsweg")
    print(lat, lon)
    bike_stations = mapper.bike_stations_in_range(lat, lon)
    print(bike_stations)
    lat, lon = mapper.stop_to_coordinates("Bornkampsweg")
    stations = mapper.bus_stations_in_range(lat, lon)
    for s in stations:
        print(s)
