import pandas as pd

def load_routes(stops="data/stops.txt", stop_sequences="data/route_id_to_stop_sequence.csv", out="data/stop_sequence_with_names.csv"):
    try:
        routes = pd.read_csv(filepath_or_buffer=out, sep=",")
    except IOError:
        stop_df = pd.read_csv(filepath_or_buffer=stops, sep=",")
        sequence_df = pd.read_csv(filepath_or_buffer=stop_sequences, sep=",")
        df = pd.merge(sequence_df, stop_df[['stop_id', 'stop_name']], on="stop_id", how="left")
        routes = []
        current_route = df["route_id"].iloc[0]
        current_stops = []
        for i, row in df.iterrows():
            new_route = row["route_id"]
            if current_route != new_route:
                routes.append((current_route, current_stops))
                current_route = new_route
                current_stops = []
            current_stops.append(row["stop_name"]) 
        routes = pd.DataFrame(routes) 
        routes.columns = ["id", "stations"]  
        routes.to_csv(out)

    return routes
