from route_coordinate_mapping import HVVCoordinateMapper
from data_generator import DataGenerator


class Main:

    def __init__(self):
        self.generator = DataGenerator()

    def add_disruption(self, begin, end, time=12):
        weather = self.generator.generate_weather()
        affected_routes = self.generator.filter_disrupted_routes(begin, end)
        walkers = 0
        bikers = 0
        car_drivers = 0
        pt_users = 0
        routes = self.generator.routes["stations"][affected_routes]
        for index, route in enumerate(routes):
            got_first_stop = False
            for i, stop in enumerate(route):
                if stop == begin or stop == end:
                    if got_first_stop:
                        station_prob_mapping = self.generator.generate_prob_mapping(stop, route[-1], affected_routes[index])
                        stations_to_target = route[i+1:]
                        for station in stations_to_target:
                            walking_prob, bike_prob, car_prob, pt_prob = self.generator.generate_features_for_dest(stop, station, time, weather=weather)
                            walkers += walking_prob * station_prob_mapping[station]
                            bikers += bike_prob * station_prob_mapping[station]
                            car_drivers += car_prob * station_prob_mapping[station]
                            pt_users += pt_prob * station_prob_mapping[station]
                    else:
                        station_prob_mapping = self.generator.generate_prob_mapping(stop, route[0], affected_routes[index])
                        stations_to_target = reversed(route[:i])
                        for station in stations_to_target:
                            walking_prob, bike_prob, car_prob, pt_prob = self.generator.generate_features_for_dest(stop, station, time, weather=weather)
                            walkers += walking_prob * station_prob_mapping[station]
                            bikers += bike_prob * station_prob_mapping[station]
                            car_drivers += car_prob * station_prob_mapping[station]
                            pt_users += pt_prob * station_prob_mapping[station]
                        got_first_stop = True
        return walkers / len(routes), bikers / len(routes), car_drivers / len(routes), pt_users / len(routes)

if __name__ == "__main__":
    main = Main()
    print(main.add_disruption("Hamburg Hbf", "Jungfernstieg"))