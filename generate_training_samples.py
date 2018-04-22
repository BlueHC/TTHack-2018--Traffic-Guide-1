import pandas as pd
import numpy as np
import sys
from main import Main
import random


if __name__ == "__main__":

    valid_pairs = []
    good_ids = pd.read_csv("data/good_trips.csv").values.reshape(-1)
    stops = pd.read_csv("data/stops.txt", usecols=["stop_id", "stop_name"], 
                        dtype={"stop_id":"str"})
    stop_times = pd.read_csv("data/stop_times.txt", usecols=["stop_id", "trip_id", "stop_sequence"], dtype={"stop_id":"str"})
    merged = stop_times.merge(stops, on="stop_id").sort_values(by=["trip_id", "stop_sequence"]).drop(["stop_id"], axis=1)
    merged["next_stop"] = merged["stop_name"].shift(-1)
    merged["next_trip_id"] = merged["trip_id"].shift(-1)
    merged = merged.iloc[:-1]
    merged["next_stop"] = merged["next_stop"].astype("str")
    merged["next_trip_id"] = merged["next_trip_id"].astype(int)
    merged = merged.drop(["stop_sequence"], axis=1)
    merged = merged.loc[[idee in good_ids for idee in merged["trip_id"]]]
    merged = merged.drop_duplicates(subset=["stop_name", "next_stop"])
    
    for i, row in enumerate(merged.iterrows()):
        r = row[1]
        if r.trip_id == r.next_trip_id:
            valid_pairs.append([(r.stop_name, r.next_stop)])
        
    m = Main()
    pairs = random.sample(valid_pairs, 10)
    
    ins = []
    outs = []
    for i, pair in enumerate(pairs):
        feat, out = m.add_disruption(*pair[0], time=random.randint(0, 23))
        if feat == []:
            continue
        print("feat", feat)
        print("out", out)
        print("ins before:", ins)
        ins.append(feat[:])
        print("ins after", ins)
        outs.append(out[:])
        print("------------------- Finished {} pairs".format(i))
    
    ins = np.array(ins)
    outs = np.array(outs)
    
    print(ins)
    print(outs)
    total = np.concatenate((ins, outs), axis=1)
    print(total)
    df_dict = {}
    for i in range(len(total)):
        df_dict[i] = total[i]
    
    print(df_dict)
    df = pd.DataFrame.from_dict(df_dict, orient="index")
    identifier = random.randint(0, 2000000)
    df.to_csv("data/export_test_{}.csv".format(identifier), index=False)
    
