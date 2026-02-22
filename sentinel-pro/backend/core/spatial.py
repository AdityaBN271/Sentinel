from typing import List, Tuple
import json

def is_point_in_polygon(x: float, y: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Ray-casting algorithm to determine if a point is inside a polygon.
    All coordinates should be normalized (0.0 to 1.0).
    """
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def get_zone_for_point(x: float, y: float, zones: List[dict]) -> str:
    """
    Find which zone a name falls into. 
    Zones should be a list of dicts with 'name' and 'polygon_data' (JSON string).
    """
    for zone in zones:
        try:
            poly = json.loads(zone['polygon_data'])
            if is_point_in_polygon(x, y, poly):
                return zone['name']
        except Exception as e:
            print(f"[Spatial] Error parsing zone {zone.get('name')}: {e}")
            continue
    return "default"
