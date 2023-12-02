# shippy

![413113000 2023-11-29](https://github.com/saffa19/shippy/assets/31897351/f8b1dd19-90e7-47cf-9380-82a9a31cfbc6)

plotting is fun but should write coords to .shp file for better mapping in browser

comething like
```path = LineString(coords)
d = {'col1': ['shipID'], 'geometry': [path]}
df = gpd.GeoDataFrame(d, crs="")
df.to_file('./shippies.shp')
```

## data

https://www.naturalearthdata.com/downloads/10m-physical-vectors/

## satellite

maybe do someting with SAR satellite tiles 

https://github.com/jasonmanesis/Ship-Detection-on-Remote-Sensing-Synthetic-Aperture-Radar-Data

https://github.com/summitgao/SAR_CD_DDNet

https://aisstream.io/documentation


## papers

https://arxiv.org/pdf/2311.04442.pdf
