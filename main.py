from route_coordinate_mapping import HVVCoordinateMapper
from data_generator import DataGenerator


class Main:

    def __init__(self):
        self.generator = DataGenerator()

    def add_disruption(self, begin, end, time=12):
        affected_routes = self.generator.filter_disrupted_routes(begin, end)
        walkers = 0
        bikers = 0
        car_drivers = 0
        pt_users = 0
        for route in self.generator.routes["stations"][affected_routes]:
            got_first_stop = False
            for i, stop in enumerate(route):
                if stop == begin or stop == end:
                    if got_first_stop:
                        walking_prob, bike_prob, car_prob, pt_prob = self.generator.generate_features_for_dest(stop, route[-1])
                        #TODO: replace 1 with capacity
                        walkers += walking_prob * 1
                        bikers += bike_prob * 1
                        car_drivers += car_prob * 1
                        pt_users += pt_prob * 1
                    else:
                        walking_prob, bike_prob, car_prob, pt_prob = self.generator.generate_features_for_dest(stop, route[0])
                        walkers += walking_prob * 1
                        bikers += bike_prob * 1
                        car_drivers += car_prob * 1
                        pt_users += pt_prob * 1
        print("Walkers: %f" % walkers)
        print("Bikers: %f" % bikers)
        print("Car drivers: %f" % car_drivers)
        print("PT users: %f" % pt_users)

if __name__ == "__main__":
    main = Main()
    main.add_disruption("Hamburg Hbf", "Jungfernstieg")