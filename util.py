# **Qualifiers for different types of osm data**

def poi_qualifier(tags, type):
    return ('amenity' in tags or 'shop' in tags or 'tourism' in tags)

def building_qualifier(tags, type):
    return (type == 'W' or type == 'R') and ( ('building' in tags) or ('building:part' in tags) or (tags.get('type') == 'building') ) and ( (tags.get('location') != 'underground') or ('bridge' not in tags) )

def highway_qualifier(tags, type):
    return (type == 'W') and ('highway' in tags)

def highway_with_sidewalk(tags, type):
    return highway_qualifier(tags, type) and \
    ( 
        ('sidewalk' in tags and tags.get('sidewalk') in ['yes', 'left', 'right', 'both', 'separate']) or \
        ('sidewalk:left' in tags and tags.get('sidewalk:left') in ['yes', 'separate']) or \
        ('sidewalk:right' in tags and tags.get('sidewalk:right') in ['yes', 'separate']) or \
        ('foot' in tags and tags.get('foot') == 'use_sidepath')
    )

def highway_without_sidewalk(tags, type):
    return highway_qualifier(tags, type) and \
    (
        ('sidewalk' in tags and tags.get('sidewalk') in ['no', 'none']) or
        (('sidewalk:left' in tags and tags.get('sidewalk:left') in ['no', 'none'] and 'sidewalk:right' not in tags)) or
        (('sidewalk:right' in tags and tags.get('sidewalk:right') in ['no', 'none'] and 'sidewalk:left' not in tags)) or
        (('sidewalk:left' in tags and tags.get('sidewalk:left') in ['no', 'none']) and ('sidewalk:right' in tags and tags.get('sidewalk:right') in ['no', 'none']))
    )

def highway_with_sidewalk_tag(tags, type):
    return \
    (
        highway_with_sidewalk(tags, type) or
        highway_without_sidewalk(tags, type)
    )

def highway_without_sidewalk_tag(tags, type):
    return highway_qualifier(tags, type) and \
    (
        tags.get('highway') not in ['footway', 'escape', 'raceway', 'busway', 'bridleway', 'steps', 'corridor', 'path', 'cycleway', 'construction'] and
        not highway_with_sidewalk(tags, type) and
        not highway_without_sidewalk(tags, type)
    )

def footway_qualifier(tags, type):
    return highway_qualifier(tags, type) and \
    (
        (tags.get('highway') in ['footway', 'living_street', 'pedestrian']) or
        ('foot' in tags and tags.get('foot') in ['yes', 'designated', 'permissive', 'private', 'destination'])
    )
    '''
        foot:private -> Its only for the owners to walk or people they give permission to
        foot:destination -> The public has right of access only if this is the only road to your destination. This route should only be used as a means of getting to or from a specific point. It should not be used for transit to somewhere else.
    '''

def sidewalk_qualifier(tags, type):
    return highway_qualifier(tags, type) and (tags.get('highway') == 'footway' and tags.get('footway')=='sidewalk')

def highway_crossing_qualifier(tags, type):
    return highway_qualifier(tags, type) and (tags.get('highway') == 'footway' and tags.get('footway')=='crossing')

def bridge_qualifier(tags, type):
    return highway_qualifier(tags, type) and (tags.get('highway') == 'footway' and 'bridge' in tags)