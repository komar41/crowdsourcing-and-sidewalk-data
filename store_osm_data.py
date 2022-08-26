import subprocess
import osmium
import os
from geopy.geocoders import Nominatim


def store_osm_data(city_abb, input_file, bbox = [], geo_loc = None, history = False):
    
    folder = 'historical' if history else 'latest'
    filename = 'data/osm/'+ folder +'/%s.osm.pbf'%(city_abb)
    input_filename = 'data/osm/'+ folder +'/%s'%(input_file)

    if(geo_loc):
        geolocator = Nominatim(user_agent='uic')
        location = geolocator.geocode(geo_loc).raw
        bbox = [float(x) for x in location['boundingbox']]
        
    bbox = [{'lat': bbox[0], 'lon': bbox[2]}, {'lat': bbox[1], 'lon': bbox[3]}]

    aux = '%f,%f,%f,%f'%(bbox[0]['lon'],bbox[0]['lat'],bbox[1]['lon'],bbox[1]['lat'])
    osm_extr = ['osmium', 'extract', '-b', aux, '-o', filename, '--overwrite', input_filename]
    if(history): osm_extr.insert(4, '-H')
    subprocess.call(osm_extr, shell=True) # WSL wasn't required!

    return

# Historical data extract from: https://osm-internal.download.geofabrik.de