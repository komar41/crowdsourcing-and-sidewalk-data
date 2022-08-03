def poi_qualifier(tags, type):
    return ('amenity' in tags or 'shop' in tags or 'tourism' in tags)

def building_qualifier(tags, type):
    return (type == 'W' or type == 'R') and ( ('building' in tags) or ('building:part' in tags) or (tags.get('type') == 'building') ) and ( (tags.get('location') != 'underground') or ('bridge' not in tags) )

def road_qualifier(tags, type):
    return (type == 'W') and ('highway' in tags)