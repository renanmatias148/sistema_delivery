import json
from shapely.geometry import Point, Polygon
from app.models.zonaentrega import ZonaEntrega

def encontrar_zona_por_localizacao(lat, lng):
    zonas = ZonaEntrega.query.all()
    ponto = Point(lng, lat)  # shapely usa lng, lat
    for zona in zonas:
        coords = json.loads(zona.coordenadas)  # [[lat, lng], ...]
        poligono = Polygon([(c[1], c[0]) for c in coords])  # lng, lat
        if poligono.contains(ponto):
            return zona
    return None
