import os
import json
import asyncio
import websockets
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import pylab as pl
from datetime import datetime, timezone, date

def tracker(msg):
    vessel_id = msg['Message']['PositionReport']['UserID']
    if not os.path.exists(f'./tracking/{date.today()}'):
        os.mkdir(f'./tracking/{date.today()}')

    path = f"./tracking/{date.today()}/{vessel_id}.json"
    position_report = msg['Message']['PositionReport']
    metadata = msg['MetaData']
    entry = position_report | metadata
    #print(msg)

    if not os.path.exists(path):
        #print(f'creating {path}')
        with open(path, 'w') as file:
            json.dump([entry], file, indent = 4)
    elif os.path.exists(path):
        #print(f'updating {path}')
        with open(path, 'r') as file:
            data = json.load(file)
        data.append(entry)
        with open(path, 'w') as file:
            json.dump(data, file, indent = 4)

    else:
        print(f'bad vessel {vessel_id}')


def mapper(vessel_id):
    with open(f'./tracking/{date.today()}/{vessel_id}.json', 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
    geo_df = gpd.GeoDataFrame(df, geometry=geometry)
    #geo_df.head()

    map = gpd.read_file('./maps/ne_10m_ocean.shp')

    fig, ax = plt.subplots(figsize = (7,7))
    map.plot(ax = ax, alpha = 0.4, color ='grey')
    geo_df.plot(geo_df['Sog'], ax = ax, markersize = 10,legend=True, legend_kwds={"label": "Speed over Ground (SoG)", "orientation": "horizontal"})
    plt.title(f'{df["UserID"].iloc[0]} {df["ShipName"].iloc[0].strip()}')
    #plt.title('Ships')
    posy, posx = geo_df['Latitude'].iloc[-1], geo_df['Longitude'].iloc[-1]
    plt.xlim(posx-.8, posx+.8)
    plt.ylim(posy-.8, posy+.8)
    #plt.xlim(110,125)
    #plt.ylim(15,30)
    plt.xlabel("Latitude")
    plt.ylabel("Longitude")

    ax.annotate(geo_df['time_utc'].iloc[0][:16], (geo_df['Longitude'].iloc[0], geo_df['Latitude'].iloc[0]), xytext=(posx+.82, geo_df['Latitude'].iloc[0]), arrowprops = dict(arrowstyle="->"))
    ax.annotate(geo_df['time_utc'].iloc[-1][:16], (posx,posy), xytext=(posx+.82, posy), arrowprops = dict(arrowstyle="->"))

    if not os.path.exists(f'./images/{date.today()}'):
        os.mkdir(f'./images/{date.today()}')
    plt.savefig(f'./images/{date.today()}/{df["UserID"].iloc[0]}.png', bbox_inches='tight')
    plt.close()

async def connect_ais_stream():
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": os.environ.get('AISSTREAM'), "BoundingBoxes": [[[20,118], [24,119]]]}
        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            
            message = json.loads(message_json)
            #print(message)
            message_type = message["MessageType"]
            
            if message_type == "PositionReport":
                # the message parameter contains a key of the message type which contains the message itself
                ais_message = message['Message']['PositionReport']
                tracker(message)
                mapper(ais_message['UserID'])
                #print(f'Tracked vessels: {len([name for name in os.listdir("./tracking/") if os.path.isfile(name)])}')
                print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']}")
            else:
                print(f"[{datetime.now(timezone.utc)}] Message Type: {message_type}")
                #print(message)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_ais_stream())
    loop.close()

if __name__ == '__main__':
    main()