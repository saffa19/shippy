import os
import json
import asyncio
import websockets
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString
import pylab as pl
from datetime import datetime, timezone, date
from pathlib import Path

def tracker(msg:json):
    Path(f'./tracking/{date.today()}').mkdir(parents=True, exist_ok=True)
    path = f'./tracking/{date.today()}/{msg["MetaData"]["MMSI"]}.json'
    entry = msg['Message']['PositionReport'] | msg['MetaData']
    #print(msg)

    if not os.path.exists(path):
        with open(path, 'w') as file:
            json.dump([entry], file, indent = 4)
        
    elif os.path.exists(path):
        with open(path, 'r') as file:
            data = json.load(file) #
        data.append(entry)
        with open(path, 'w') as file:
            json.dump(data, file, indent = 4)


def mapper(vessel_id:int):
    #with open(f'./tracking/{date.today()}/{vessel_id}.json', 'r') as file:
    #    data = json.load(file)
    #df = pd.DataFrame(data)
    df = pd.read_json(f'./tracking/{date.today()}/{vessel_id}.json')
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]   #create points from separate latlongs 
    geo_df = gpd.GeoDataFrame(df, geometry=geometry)

    #points shp (1 shapefile per ship per day)
    Path(f'./shapefiles/{date.today()}/{vessel_id}/').mkdir(parents=True, exist_ok=True)
    geo_df.to_file(f'./shapefiles/{date.today()}/{vessel_id}/{date.today()}_{vessel_id}.shp')

    #polyline tracking df
    if len(df.index) > 1:
        try:
            lines_gdf = geo_df.groupby(['MMSI'])['geometry'].apply(lambda x: LineString(x.tolist()))
            lines_gdf = gpd.GeoDataFrame(lines_gdf, geometry='geometry')
            print(f'\nlines_gdf (geodataframe): \n{lines_gdf.head()}\n')

            #daily summary
            if not os.path.exists(f'./tracking/0 {date.today()} summary.json'):
                print('creating new summary file...')
                lines_gdf.to_file(f'./tracking/0 {date.today()} summary.json')
            else:
                with open(f'./tracking/0 {date.today()} summary.json', 'r') as file:
                    summary = json.load(file)
                summ_df = gpd.GeoDataFrame.from_features(summary['features'])
                print(f'\n\summ_df: \n{summ_df.head()}\n')

                df = pd.concat([summ_df, lines_gdf])
                print(f'\n\summ_df: \n{df.head()}\n')

                #summ_df = gpd.GeoDataFrame(summ_df)
                #print(f'\n\summ_df: \n{summ_df.head()}\n')
                #summ_df.to_file(f'./tracking/0 {date.today()} summary.json')
        finally:
            pass

    basemap = gpd.read_file('./maps/ne_10m_ocean.shp')

    fig, ax = plt.subplots(figsize = (7,7))
    basemap.plot(ax = ax, alpha = 0.4, color ='grey')
    geo_df.plot(geo_df['Sog'], ax = ax, markersize = 10,legend=True, legend_kwds={'label': 'SoG', 'orientation': 'horizontal'})
    plt.title(f'{df["MMSI"].iloc[0]} {df["ShipName"].iloc[0].strip()}')
    posy, posx = geo_df['Latitude'].iloc[-1], geo_df['Longitude'].iloc[-1]
    #centre on ship last known location
    plt.xlim(posx-.8, posx+.8)
    plt.ylim(posy-.8, posy+.8)
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    #start/end annotations
    ax.annotate(geo_df['time_utc'].iloc[0][:16], (geo_df['Longitude'].iloc[0], geo_df['Latitude'].iloc[0]), xytext=(posx+.82, geo_df['Latitude'].iloc[0]), arrowprops = dict(arrowstyle='->'))
    ax.annotate(geo_df['time_utc'].iloc[-1][:16], (posx,posy), xytext=(posx+.82, posy), arrowprops = dict(arrowstyle='->'))

    Path(f'./images/{date.today()}').mkdir(parents=True, exist_ok=True)
    plt.savefig(f'./images/{date.today()}/{df["MMSI"].iloc[0]}.png', bbox_inches='tight')
    plt.close()

async def connect_ais_stream():
    async with websockets.connect('wss://stream.aisstream.io/v0/stream') as websocket:
        subscribe_message = {'APIKey': os.environ.get('AISSTREAM'), 'BoundingBoxes': [[[20,118], [24,119]]]}
        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            
            message = json.loads(message_json)
            #print(message)
            message_type = message['MessageType']
            
            if message_type == 'PositionReport':
                # the message parameter contains a key of the message type which contains the message itself
                ais_message = message['Message']['PositionReport']
                tracker(message)
                mapper(message['MetaData']['MMSI'])
                #print(f'Tracked vessels: {len([name for name in os.listdir('./tracking/') if os.path.isfile(name)])}')
                print(f'[{datetime.now()}] ShipId: {message["MetaData"]["MMSI"]} Latitude: {ais_message["Latitude"]:.6f} Longitude: {ais_message["Longitude"]:.6f}')
            else:
                print(f'[{datetime.now()}] Message Type: {message_type}')
                #print(message)
    

if __name__ == '__shippy__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_ais_stream())
    loop.close()