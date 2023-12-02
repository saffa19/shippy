# shippy

Uses AIS data to track ships within a certain zone. Aim is to build a cool dashboard or something

![413113000 2023-11-29](https://github.com/saffa19/shippy/assets/31897351/f8b1dd19-90e7-47cf-9380-82a9a31cfbc6)

export [AIS Stream](https://aisstream.io/) API key to env

`export AISSTREAM='valid_key'`

## data

https://www.naturalearthdata.com/downloads/10m-physical-vectors/

## satellite

maybe do someting with SAR satellite tiles 

https://github.com/jasonmanesis/Ship-Detection-on-Remote-Sensing-Synthetic-Aperture-Radar-Data

https://github.com/summitgao/SAR_CD_DDNet

https://aisstream.io/documentation


## papers

https://arxiv.org/pdf/2311.04442.pdf


## tracking

```
Traceback (most recent call last):
  File "/home/saffa/.local/lib/python3.10/site-packages/pandas/core/indexes/base.py", line 3790, in get_loc
    return self._engine.get_loc(casted_key)
  File "index.pyx", line 152, in pandas._libs.index.IndexEngine.get_loc
  File "index.pyx", line 181, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/hashtable_class_helper.pxi", line 7080, in pandas._libs.hashtable.PyObjectHashTable.get_item
  File "pandas/_libs/hashtable_class_helper.pxi", line 7088, in pandas._libs.hashtable.PyObjectHashTable.get_item
KeyError: 'ShipName'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/saffa/shippy/main.py", line 118, in <module>
    main()
  File "/home/saffa/shippy/main.py", line 114, in main
    loop.run_until_complete(connect_ais_stream())
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/saffa/shippy/main.py", line 105, in connect_ais_stream
    mapper(message['MetaData']['MMSI'])
  File "/home/saffa/shippy/main.py", line 74, in mapper
    plt.title(f'{df["MMSI"].iloc[0]} {df["ShipName"].iloc[0].strip()}')
  File "/home/saffa/.local/lib/python3.10/site-packages/geopandas/geodataframe.py", line 1474, in __getitem__
    result = super().__getitem__(key)
  File "/home/saffa/.local/lib/python3.10/site-packages/pandas/core/frame.py", line 3893, in __getitem__
    indexer = self.columns.get_loc(key)
  File "/home/saffa/.local/lib/python3.10/site-packages/pandas/core/indexes/base.py", line 3797, in get_loc
    raise KeyError(key) from err
KeyError: 'ShipName'
```
