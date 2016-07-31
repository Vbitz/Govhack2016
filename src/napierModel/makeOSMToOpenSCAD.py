import xml.etree.ElementTree as ET
import csv, shapely.geometry, shapely.wkt, utm, sys, os
from os.path import abspath as path_absoulte
from os.path import join as path_join

BASE_PATH = path_absoulte("../../data/private/napierModel")
OSM_INPUT = path_join(BASE_PATH, "napier_large.osm")
OUTPUT_DIR = path_absoulte("../../pub/napierModel/output_scad")

RES_BUILDING_SCAD = path_join(OUTPUT_DIR, "resBuildings%s.scad")
COM_BUILDING_SCAD = path_join(OUTPUT_DIR, "comBuildings%s.scad")
IND_BUILDING_SCAD = path_join(OUTPUT_DIR, "indBuildings%s.scad")

SERVICES_SCAD = path_join(OUTPUT_DIR, "services%s.scad")
RES_SCAD = path_join(OUTPUT_DIR, "residential%s.scad")
HIGHWAY_SCAD = path_join(OUTPUT_DIR, "highway%s.scad")
FOOTWAY_SCAD = path_join(OUTPUT_DIR, "footway%s.scad")
GRASS_SCAD = path_join(OUTPUT_DIR, "grass%s.scad")
RESLAND_SCAD = path_join(OUTPUT_DIR, "residentialLand%s.scad")
COMLAND_SCAD = path_join(OUTPUT_DIR, "commercialLand%s.scad")
INDLAND_SCAD = path_join(OUTPUT_DIR, "industryLand%s.scad")
WALL_SCAD = path_join(OUTPUT_DIR, "wall%s.scad")
PARKING_SCAD = path_join(OUTPUT_DIR, "parking%s.scad")

ID_BLACKLIST = [
    "89197847",
    "89786272",
    "89786240",
    "89197868",
    "294160250",
    "430453726",
    "430453727",
    "116268161",
    "215036732",
    "215036734",
    "215036735",
    "215036737",
    "215036738",
    "215036740",
    "223520402",
    "223520412",
    "223520426",
    "223520473",
    "344611756",
    "351544130",
    "430300593",
    "430448721",
    "430463131",
    "430463510"
]

SPORT_LIST = [
    "cricket",
    "rugby",
    "skating",
    "bowls"
]

LEISURE_LIST = [
    "swimming_pool",
    "park",
    "stadium",
    "pitch",
    "playground"
]

AMENITY_LIST = [
    "cafe",
    "shelter",
    "post_office",
    "fuel",
    "veterinary"
]

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

class RotateWriter(object):
    def __init__(self, baseFile, maxI=50):
        self.x = 0
        self.i = 0
        self.maxI = maxI
        self.baseFile = baseFile
        self.fileObject = open(self.formatFilename(), "wb")
        print "writing to ", self.formatFilename()
    
    def formatFilename(self):
        return self.baseFile % (self.x, )

    def write(self, str):
        self.fileObject.write(str)
        self.i += 1
        if self.i > self.maxI:
            self.x += 1
            self.i = 0
            self.fileObject.close()
            self.fileObject = open(self.formatFilename(), "wb")
            print "writing to ", self.formatFilename()

    def close(self):
        self.fileObject.close()

def pointToM(x, y):
    e, n, _, _ = utm.from_latlon(float(x), float(y))
    return e, n

UNIFORM_SCALE = 1

def pointsToLine(points, buffer):
    return shapely.geometry.LineString([(point["x"] * UNIFORM_SCALE, point["y"] * UNIFORM_SCALE) for point in points]).buffer(buffer * UNIFORM_SCALE)

def pointsToPolygon(points):
    return shapely.geometry.Polygon([(point["x"] * UNIFORM_SCALE, point["y"] * UNIFORM_SCALE) for point in points])

def writeOpenSCADPolygon(height, geo):
    points = [pt for pt in geo.exterior.coords]
    strValue = str(points).replace("(", "[").replace(")", "]")
    return "linear_extrude(%s) polygon(points=%s);\n" % (str(height * UNIFORM_SCALE), strValue, )

def parseOSMXML(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    boundsMinX = 0
    boundsMinY = 0

    nodeList = {}
    wayList = {}
    ret = []

    for child in root:
        if child.tag == "bounds":
            boundsMinX, boundsMinY = pointToM(child.attrib.get("minlat"), child.attrib.get("minlon"))
        elif child.tag == "node":
            #print "node", child.attrib
            pX, pY = pointToM(child.attrib.get("lat"), child.attrib.get("lon"))
            newNode = {"x": pX - boundsMinX, "y": pY - boundsMinY}
            for subchild in child:
                if subchild.tag == "tag":
                    #print "node.tag", subchild.attrib
                    newNode[subchild.attrib.get("k")] = subchild.attrib.get("v")
                else:
                    raise Exception(subchild.tag)
            # print newNode
            nodeList[child.attrib.get("id")] = newNode
        elif child.tag == "way":
            # print "way", child.attrib
            newWay = {"type": "way", "id": child.attrib.get("id"), "__points__": []}
            for subchild in child:
                if subchild.tag == "tag":
                    # print "way.tag", subchild.attrib
                    newWay[subchild.attrib.get("k")] = subchild.attrib.get("v")
                elif subchild.tag == "nd":
                    # print "way.nd", subchild.attrib
                    nodeRef = nodeList[subchild.attrib.get("ref")]
                    if nodeRef == None:
                        raise "Bad Node"
                    newWay["__points__"] += [nodeRef]
                else:
                    raise Exception(subchild.tag)
            if newWay["id"] in ID_BLACKLIST:
                continue
            ret += [newWay]
        elif child.tag == "relation":
            continue
            print "relation", child.attrib
            for subchild in child:
                if subchild.tag == "tag":
                    print "way.tag", subchild.attrib
                elif subchild.tag == "member":
                    print "relation.member", subchild.attrib
                else:
                    raise Exception(subchild.tag)
        elif child.tag == "note":
            continue
        elif child.tag == "meta":
            continue
        else:
            raise Exception(child.tag)
    return ret

if __name__ == "__main__":
    osmData = parseOSMXML(OSM_INPUT)

    resBuildingFile = RotateWriter(RES_BUILDING_SCAD)
    comBuildingFile = RotateWriter(COM_BUILDING_SCAD)
    indBuildingFile = RotateWriter(IND_BUILDING_SCAD)


    residentialLandFile = RotateWriter(RESLAND_SCAD)
    commercialLandFile = RotateWriter(COMLAND_SCAD)
    industryLandFile = RotateWriter(INDLAND_SCAD)
    
    highwayFile = RotateWriter(HIGHWAY_SCAD)
    servicesFile = RotateWriter(SERVICES_SCAD)
    residentialFile = RotateWriter(RES_SCAD)
    footwayFile = RotateWriter(FOOTWAY_SCAD)
    grassFile = RotateWriter(GRASS_SCAD)
    wallFile = RotateWriter(WALL_SCAD)
    parkingFile = RotateWriter(PARKING_SCAD)

    for element in osmData:
        if element.get("building", "no") == "roof":
            buildingHeight = 1.2
            comBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
        elif element.get("service", "no") == "driveway" or element.get("highway", "no") == "service":
            servicesFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 2)))
        elif element.get("highway", "no") == "residential":
            residentialFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 5)))
        elif element.get("highway", "no") == "secondary" or element.get("highway", "no") == "unclassified":
            highwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 7)))
        elif element.get("highway", "no") == "secondary_link":
            highwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 4)))
        elif element.get("highway", "no") == "primary_link":
            highwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 5)))
        elif element.get("highway", "no") == "primary":
            highwayFile.write(writeOpenSCADPolygon(0.6, pointsToLine(element.get("__points__"), 10)))
        elif element.get("highway", "no") == "tertiary":
            highwayFile.write(writeOpenSCADPolygon(0.5, pointsToLine(element.get("__points__"), 3)))
        elif element.get("highway", "no") == "footway" or element.get("highway", "no") == "path":
            footwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 1)))
        elif element.get("highway", "no") == "trunk":
            highwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 15)))
        elif element.get("highway", "no") == "trunk_link":
            highwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 10)))
        elif element.get("railway", "no") == "rail":
            highwayFile.write(writeOpenSCADPolygon(0.4, pointsToLine(element.get("__points__"), 10)))
        elif element.get("tunnel", "no") == "culvert":
            pass
        elif element.get("leisure", "no") in LEISURE_LIST or element.get("sport", "no") in SPORT_LIST or element.get("landuse", "no") == "recreation_ground" or element.get("landuse", "no") == "forest" or element.get("landuse", "no") == "vineyard":
            grassFile.write(writeOpenSCADPolygon(0.2, pointsToPolygon(element.get("__points__"))))
        elif element.get("landuse", "no") == "residential":
            residentialLandFile.write(writeOpenSCADPolygon(0.2, pointsToPolygon(element.get("__points__"))))
        elif element.get("landuse", "no") == "religious":
            commercialLandFile.write(writeOpenSCADPolygon(0.2, pointsToPolygon(element.get("__points__"))))
        elif element.get("landuse", "no") == "retail" or element.get("landuse", "no") == "commercial" or element.get("landuse", "no") == "orchard":
            commercialLandFile.write(writeOpenSCADPolygon(0.2, pointsToPolygon(element.get("__points__"))))
        elif element.get("landuse", "no") == "industrial" or element.get("landuse", "no") == "farmland" or element.get("landuse", "no") == "farmyard":
            commercialLandFile.write(writeOpenSCADPolygon(0.2, pointsToPolygon(element.get("__points__"))))
        elif element.get("highway", "no") == "proposed":
            pass
        elif element.get("landuse", "no") == "construction":
            pass
        elif element.get("power", "no") == "sub_station":
            commercialLandFile.write(writeOpenSCADPolygon(5, pointsToPolygon(element.get("__points__"))))
        elif element.get("waterway", "no") == "riverbank" or element.get("waterway", "no") == "river" or element.get("waterway", "no") == "drain" or element.get("waterway", "no") == "stream":
            # TODO: Handle this
            pass
        elif element.get("barrier", "no") == "low":
            wallFile.write(writeOpenSCADPolygon(0.7, pointsToLine(element.get("__points__"), 0.1)))
        elif element.get("barrier", "no") == "fence":
            wallFile.write(writeOpenSCADPolygon(1.2, pointsToLine(element.get("__points__"), 0.1)))
        elif element.get("amenity", "no") == "parking":
            parkingFile.write(writeOpenSCADPolygon(0.4, pointsToPolygon(element.get("__points__"))))
        elif element.get("amenity", "no") == "school" or element.get("amenity", "no") == "kindergarten":
            commercialLandFile.write(writeOpenSCADPolygon(0.4, pointsToPolygon(element.get("__points__"))))
        elif element.get("power", "no") == "minor_line":
            # TODO: Handle this 
            pass
        elif element.get("building", "no") != "no" or element.get("height", "no") != "no":
            buildingHeight = float(element.get("height", "3.0"))
            keys = [key for key in element]
            if element.get("amenity", "no") in AMENITY_LIST:
                comBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif element.get("shop", "no") != "no" or element.get("product", "no") != "no" or element.get("website", "no") != "no":
                buildingHeight *= 2
                comBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif element.get("shop", "no") == "trade":
                buildingHeight *= 2
                indBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif element.get("building", "no") == "school":
                buildingHeight *= 2
                comBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif element.get("building", "no") == "church":
                buildingHeight *= 2
                comBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif element.get("building", "no") == "garage" or element.get("building", "no") == "residential":
                buildingHeight = 4.0
                resBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif element.get("leisure", "no") == "laser_tag":
                buildingHeight *= 2
                comBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif len(keys) == 4:
                resBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            elif len(keys) == 5:
                resBuildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToPolygon(element.get("__points__"))))
            else:
                print "error", element
                raise Exception()
        else:
            print "error", element
            raise Exception()