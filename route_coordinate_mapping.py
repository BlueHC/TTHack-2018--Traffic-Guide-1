import pandas as pd


class HVVCoordinateMapper:
    def __init__(self):
        self.df = None
        self.stop_to_index = {}
        self.lat_lon_to_index = {}
        self.index_to_lat = {}
        self.index_to_lon = {}

    def load_bus_data(self, file="data/stops.txt"):
        self.df = pd.read_csv(filepath_or_buffer=file, sep=",")
        for i, row in self.df.iterrows():
            self.stop_to_index[row["stop_name"]] = i
            self.lat_lon_to_index[(row["stop_lat"], row["stop_lon"])] = i

    def stop_to_coordinates(self, stop_name):
        row = self.df.iloc[self.stop_to_index[stop_name]]
        return row["stop_lat"], row["stop_lon"]

    def coordinates_to_stop(self, latitude, longitude):
        row = self.df.iloc[self.lat_lon_to_index[(latitude, longitude)]]
        return row["stop_name"]


if __name__ == "__main__":
    mapper = HVVCoordinateMapper()
    mapper.load_bus_data()
    lat, lon = mapper.stop_to_coordinates("Billhorner Deich")
    print(lat, lon)
    name = mapper.coordinates_to_stop(lat, lon)
    print(name)
