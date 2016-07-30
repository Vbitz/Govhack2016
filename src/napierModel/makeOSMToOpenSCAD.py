import xml.etree.ElementTree as ET
import csv, shapely.geometry, shapely.wkt, utm, sys, os
from os.path import abspath as path_absoulte
from os.path import join as path_join

BASE_PATH = path_absoulte("../../data/private/napierModel")
OSM_INPUT = path_join(BASE_PATH, "napier_small.osm")
OUTPUT_DIR = path_absoulte("../../pub/napierModel/output_scad")
BUILDING_SCAD = path_join(OUTPUT_DIR, "buildings.scad")

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

def pointToM(x, y):
    e, n, _, _ = utm.from_latlon(float(x), float(y))
    return e, n

def pointsToGeo(points):
    return shapely.geometry.Polygon([(point["x"], point["y"]) for point in points])

def writeOpenSCADPolygon(height, geo):
    points = [pt for pt in geo.exterior.coords]
    strValue = str(points).replace("(", "[").replace(")", "]")
    return "linear_extrude(%s) polygon(points=%s);\n" % (str(height * 100), strValue, )

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
        else:
            raise Exception(child.tag)
    return ret

if __name__ == "__main__":
    osmData = parseOSMXML(OSM_INPUT)

    buildingFile = open(BUILDING_SCAD, "wb")

    for element in osmData:
        if element.get("building", "no") == "yes":
            buildingHeight = float(element.get("height", "3.0"))
            buildingFile.write(writeOpenSCADPolygon(buildingHeight, pointsToGeo(element.get("__points__"))))

    buildingFile.close()