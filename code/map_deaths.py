import pandas as pd
import os
import numpy as np
import sys
import folium

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')
from alarms_coord import update_coord

min_deaths = {'בארי': 112, 'ניר עוז': 35, 'יכיני':4, 'נתיב העשרה': 21, 'כפר עזה': 72, 'עלומים': 20, 'כיסופים': 16,
              'רעים': 5, 'נירים': 5, 'אופקים':30, 'נחל עוז': 35, 'חולית': 13, 'ניר יצחק': 3, 'עין השלושה': 3,
              'מגן': 1, 'סופה': 3, 'כרם שלום': 2, 'שלומית': 2}  # from: https://www.ynet.co.il/news/article/yokra13627562
def map_deaths():
    df = pd.read_csv('data/deaths.csv')
    # coo = pd.read_csv('data/coord.csv')
    locs = [x for x in df['from'] if type(x) == str]
    locu = np.unique(locs)
    for md in list(min_deaths.keys()):
        if md not in locu:
            locu = np.array(list(locu)+[md])
    update_coord(latest=locu, coord_file='data/coord_deaths.csv')
    coo = pd.read_csv('data/coord_deaths.csv')
    center = [coo['lat'].mean(), coo['long'].mean()]
    ##
    map = folium.Map(location=center, zoom_start=7.5)#, tiles='openstreetmap')
    # folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png',
    #                  attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)
    # folium.TileLayer('openstreetmap').add_to(map)
    folium.TileLayer('cartodbpositron').add_to(map)
    now = np.datetime64('now', 'ns')
    nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
    nowstr = str(nowisr)[:16].replace('T', ' ')
    title_html = f'''
                 <h3 align="center" style="font-size:16px"><b>War deaths in Israel since 7-Oct-23, by residence. data from <a href="https://ynet-projects.webflow.io/news/attackingaza" target="_blank">ynet</a>
                 . last checked: {nowstr}</b></h3>
                 '''
    map.get_root().html.add_child(folium.Element(title_html))
    locs = np.array(locs)
    size = np.zeros(len(locu), int)
    for iloc in range(len(locu)):
        row_coo = coo['loc'] == locu[iloc]
        if np.sum(row_coo) == 1:
            size[iloc] = np.sum(locs == locu[iloc])
            if locu[iloc] in min_deaths.keys():
                size[iloc] = np.max([min_deaths[locu[iloc]], size[iloc]])
            lat = float(coo['lat'][row_coo])
            long = float(coo['long'][coo['loc'] == locu[iloc]])
            tip = f'{locu[iloc]}  {size[iloc]}'
            radius = (size[iloc]/np.pi)**0.5
            folium.Circle(location=[lat, long],
                                tooltip=tip,
                                radius=float(np.max([radius*750, 1])),
                                fill=True,
                                fill_color='#ff0000',
                                color='#ff0000',
                                opacity=0,
                                fill_opacity=0.5
                                ).add_to(map)
            # folium.CircleMarker(location=[lat, long],
            #                     tooltip=tip,
            #                     radius=float(np.max([radius, 1])),
            #                     fill=True,
            #                     fill_color='#ff0000',
            #                     color='#ff0000',
            #                     opacity=0,
            #                     fill_opacity=0.5
            #                     ).add_to(map)
        else:
            print('cannot find coord for '+locu[iloc])
    folium.Circle(location=[31.4025912, 34.4724382],
                  tooltip='המסיבה ברעים, 260',
                  radius=float((260/np.pi)**0.5 * 750),
                  fill=True,
                  fill_color='#555555',
                  color='#555555',
                  opacity=0,
                  fill_opacity=0.5
                  ).add_to(map)
    map.save("docs/war_deaths23.html")
    print('done')


if __name__ == '__main__':
    map_deaths()