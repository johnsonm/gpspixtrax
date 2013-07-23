#!/usr/bin/python
#
# Copyright 2013 Michael K Johnson
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from lxml import etree
from lxml import objectify

import ddict

MODE = ddict.ddict((
    ('valid', 1),
    ('gps', 2),
    ('projected', 4),
    ('interpolated', 8),
))

class KMLPaths(object):
    def __init__(self, slice):
        self.slice = slice

    def coordinateString(self, modemask):
        matches = []
        match = None

        def gpscoord(i):
            if i.GPSMeasureMode == 3:
                return (i.GPSLongitude, i.GPSLatitude, i.GPSAltitude)
            else:
                return (i.GPSLongitude, i.GPSLatitude)

        for image in self.slice:
            if image.GPSStatus == 'A':
                match = gpscoord(image)
            elif modemask & MODE.gps and 'GPSStatus' in image:
                match = gpscoord(image)
            elif modemask & MODE.projected and 'projlat' in image:
                match = (image.projlon, image.projlat)
            elif modemask & MODE.interpolated and 'fuzzlat' in image:
                match = (image.fuzzlon, image.fuzzlat)
            if match and (not matches or match != matches[-1]):
                matches.append(match)
        if matches:
            return ' '.join(','.join(str(y) for y in x) for x in matches)
        else:
            return ''

    def KML(self, name, modemask):
        E = objectify.ElementMaker(annotate=False,
                                   namespace="http://www.opengis.net/kml/2.2",
                                   nsmap={None : "http://www.opengis.net/kml/2.2"})
        return E.kml(E.Document(E.Placemark(
            E.name(name),
            E.LineString(
                E.extrude("0"),
                E.tesselate("0"),
                E.altitudeMode("clampToGround"),
                E.coordinates(self.coordinateString(modemask))
            )
        )))
