import csv, shapely.geometry, shapely.wkt, utm, sys, os
from os.path import abspath as path_absoulte
from os.path import join as path_join

BASE_PATH = path_absoulte("../../data/private/napierModel")
CSV_BUILDINGS = path_join(BASE_PATH, "BUILDINGS.csv")

def pointToM(pt):
    x, y = pt
    return (x - 421000) * 100, (y - 816000) * 100

def OGCGeoToShapely(str):
    return shapely.wkt.loads(str)

def parseOGCGeo(str):
    shapely_geo = OGCGeoToShapely(str)
    assert shapely_geo.geom_type == "Polygon"
    return shapely_geo

def writeOpenSCADPolygon(geo, height, bottom):
    points = [pointToM(pt) for pt in geo.exterior.coords]
    strValue = str(points).replace("(", "[").replace(")", "]")
    print "translate([0, 0, %s]) linear_extrude(%s) polygon(points=%s);" % (str(bottom * 100), str(height * 100), strValue, )

def read_csv_dict(filename):
    f = open(filename, "rb")
    reader = csv.DictReader(f)
    rows = [row for row in reader]
    f.close()
    return rows

if __name__ == "__main__":
    buildingData = read_csv_dict(CSV_BUILDINGS)
    # print "loaded", len(buildingData), "buildings"
    i = 0
    for building in buildingData:
        geo = building["OGC_GEOMETRY"]
        height = building["BLD_HEIGHT"]
        bottom = building["BOTTOM"]
        parsed_geo = parseOGCGeo(geo)
        if (parsed_geo.centroid.x < 0 or parsed_geo.centroid.y < 0):
            continue
        writeOpenSCADPolygon(parsed_geo, float(height), bottom)