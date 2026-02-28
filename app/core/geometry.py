try:
    from shapely.geometry import Point, Polygon, box
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

def is_point_in_zone(point, zone):
    """
    Check if a point (x, y) is inside a zone definition.
    Zone dict format:
    - Point: {'type': 'point', 'x': ..., 'y': ...} (Not really a zone, but radius check?)
    - Rect: {'type': 'rect', 'x': ..., 'y': ..., 'w': ..., 'h': ...}
    - Poly: {'type': 'poly', 'points': [{'x':..., 'y':...}, ...]}
    """
    x, y = point
    
    if not HAS_SHAPELY:
        # Simple fallback for Rectangle only
        if zone.get('type') == 'rect':
            rx, ry, rw, rh = zone['x'], zone['y'], zone['w'], zone['h']
            return rx <= x <= rx + rw and ry <= y <= ry + rh
        return False

    # Shapely Implementation
    p = Point(x, y)
    
    if zone.get('type') == 'rect':
        rx, ry, rw, rh = zone['x'], zone['y'], zone['w'], zone['h']
        # Convert to polygon
        poly = box(rx, ry, rx + rw, ry + rh)
        return poly.contains(p)
        
    elif zone.get('type') == 'poly':
        points = [(pt['x'], pt['y']) for pt in zone['points']]
        if len(points) < 3: return False
        poly = Polygon(points)
        return poly.contains(p)
        
    return False

def is_box_in_zone(bbox, zone, threshold=0.5):
    """
    Check if a bounding box overlaps significantly with a zone.
    bbox: [x1, y1, x2, y2]
    """
    # Simply check center point for now
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return is_point_in_zone((center_x, center_y), zone)
