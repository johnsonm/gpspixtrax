#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from dateutil import parser as dateparser
from datetime import datetime
import math
import os
import sys

import ddict

class GPSPixTrax(object):
    def __init__(self, imagedata):
        self.imagedata = imagedata

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        'distance between points on a circular earth'
        # formula from http://www.movable-type.co.uk/scripts/latlong.html
        R = 6371.0 # km
        dLat = math.radians(lat2-lat1)
        dLon = math.radians(lon2-lon1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        a = (math.pow(math.sin(dLat/2), 2) +
             math.pow(math.sin(dLon/2), 2) * math.cos(lat1) * math.cos(lat2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    @staticmethod
    def bearing(lat1, lon1, lat2, lon2):
        'initial bearing from location 1 to location 2 on great circle route'
        # formula from http://www.movable-type.co.uk/scripts/latlong.html
        dLat = math.radians(lat2-lat1)
        dLon = math.radians(lon2-lon1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        y = math.sin(dLon) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dLon))
        return (math.degrees(math.atan2(y, x)) + 360) % 360

    @staticmethod
    def project(lat, lon, bearing, distance):
        'project lat, lon destination from start point, bearing, distance'
        # formula from http://www.movable-type.co.uk/scripts/latlong.html
        R = 6371.0 # km
        dR = distance/R
        lat = math.radians(lat)
        lon = math.radians(lon)
        dlat = math.asin(math.sin(lat) * math.cos(dR) +
                         math.cos(lat) * math.sin(dR) * math.cos(bearing))
        dlon = lon + math.atan2(math.sin(bearing) * math.sin(dR) * math.cos(lat),
                                math.cos(dR) - math.sin(lat) * math.sin(dlat))
        return (math.degrees(dlat), math.degrees(dlon))

    @staticmethod
    def total_seconds(delta):
        # preserves sign
        return (delta.microseconds * 0.000001) + delta.seconds + delta.days * 24 * 3600

    @staticmethod
    def iso8601(datestring):
        'convert EXIF date string to iso8601 or close enough to parse'
        return datestring.replace(':', '-', 2).replace(' ', 'T', 1)

    def round_offset(self, image):
        offset = image.gpstime - image.pseudolocaltime
        offset = int(self.total_seconds(offset))
        # find closest 30-minute offset and assume it is correct
        image['tzoffset'] = int(round(offset / 1800.0) * 0.5)
        image['tzseconds'] = int(image.tzoffset * 3600)

    def match_offset(self, notzImage, image, range):
        offset = notzImage.localtime - image.localtime
        if abs(int(self.total_seconds(offset))) <= range:
            notzImage['tzoffset'] = image.tzoffset
            notzImage['tzseconds'] = image.tzseconds

    def guess_offset(self, image, epsilon, range):
        # set offset if timestamps are within ± epsilon seconds of an integer
        # number of hours apart and within range
        # 30-minute-off timestamps are relatively unusual; basically, do not
        # assume a 30-minute-off timestamp without at least one verified fix
        offset = image.gpstime - image.pseudolocaltime
        offset = int(self.total_seconds(offset))
        off = abs(offset)
        if off < range and (off + epsilon) % 3600 < epsilon * 2:
            image['tzoffset'] = int(offset / 3600.0)
            image['tzseconds'] = int(image.tzoffset * 3600)


    def parsetime(self):
        for slice in self.imagedata:
            for image in slice:
                image['gpstime'] = dateparser.parse(self.iso8601(image.GPSDateTime))
                image['localtime'] = dateparser.parse(self.iso8601(image.DateTimeOriginal))
                # localtime as if it were UTC to allow datetime math with
                # offset calculation
                image['pseudolocaltime'] = datetime(
                    *image.localtime.timetuple()[0:6],
                    tzinfo=image.gpstime.tzinfo)

                if image.GPSStatus == 'A':
                    # good enough to pretend the naive camera time is GPS UTC, 
                    # calculate nearest offset
                    self.round_offset(image)

    def imagecmp(self, first, second):
        #     Return negative if x<y, zero if x==y, positive if x>y.
        delta = self.total_seconds(first.gpstime-second.gpstime)
        if delta > 0:
            return 1
        if delta < 0:
            return -1

        name1 = os.path.basename(first.SourceFile)
        name2 = os.path.basename(second.SourceFile)
        if name1[0:2] == name2[0:2]:
            # use integer part only if they are in the same series
            name1 = int(''.join(x for x in name1 if x.isdigit()))
            name2 = int(''.join(x for x in name2 if x.isdigit()))
            return name1-name2

        return 0

    def sortslices(self):
        for slice in self.imagedata:
            slice.sort(cmp=self.imagecmp)

    def pass2(self):
        missingOffset = []
        for i in range(len(self.imagedata)):
            for j in range(len(self.imagedata[i])):
                image = self.imagedata[i][j]

                if j == 0:
                    # first in the slice; do not look across slices in this pass
                    last = image
                    lastTZimage = None

                if 'tzoffset' in image:
                    for oldImage in missingOffset:
                        oldImage['tzoffset'] = image.tzoffset
                        oldImage['tzseconds'] = image.tzseconds
                    missingOffset = []
                    lastTZimage = image
                else:
                    missingOffset.append(image)

                image['durationGPS'] = image.gpstime - last.gpstime
                image['durationLocal'] = image.localtime - last.localtime
                image['deltaDistance'] = self.haversine(
                    image.GPSLatitude, image.GPSLongitude,
                    last.GPSLatitude, last.GPSLongitude)
                image['initialBearing'] = self.bearing(
                    image.GPSLatitude, image.GPSLongitude,
                    last.GPSLatitude, last.GPSLongitude)
                seconds = self.total_seconds(image.durationGPS)
                if seconds:
                    image['averageSpeed'] = math.fabs(image.deltaDistance /
                                                      (seconds / 3600.0))
                else:
                    image['averageSpeed'] = 0
                image['deltaAltitude'] = image.GPSAltitude - last.GPSAltitude
                last = image

            if missingOffset and lastTZimage:
                for notzImage in missingOffset:
                    self.match_offset(notzImage, lastTZimage, 28800)


    def pass3(self):
        missingGPS = []
        lastAcq = None
        for i in range(len(self.imagedata)):
            for j in range(len(self.imagedata[i])):
                image = self.imagedata[i][j]

                if j == 0:
                    if image.GPSStatus == 'V':
                        lastAcq = None
                if image.GPSStatus == 'V' and lastAcq:
                    missingGPS.append(image)

                if not 'tzseconds' in image:
                    # this only happens if there were no verified fixes in the
                    # whole slice of pictures being taken...
                    self.guess_offset(image, 300, 28800)

                if 'tzseconds' in image:
                    image['gpsStampAge'] = int(
                        self.total_seconds(image.pseudolocaltime -
                                           image.gpstime) + image.tzseconds)

                if image.GPSStatus == 'A':
                    if lastAcq and missingGPS:
                        interval = self.total_seconds(image.gpstime-lastAcq.gpstime)
                        bearing = self.bearing(lastAcq.GPSLatitude, lastAcq.GPSLongitude,
                                               image.GPSLatitude, image.GPSLongitude)
                        distance = self.haversine(lastAcq.GPSLatitude, lastAcq.GPSLongitude,
                                                  image.GPSLatitude, image.GPSLongitude)
                        plat, plon = self.project(
                            lastAcq.GPSLatitude, lastAcq.GPSLongitude, lastAcq.GPSTrack,
                            interval * lastAcq.GPSSpeed)
                        error = self.haversine(plat, plon, image.GPSLatitude, image.GPSLongitude)
                        errorSpeed = error * (interval/3600.0)
                        # assign locations to intermediate images in missingGPS
                        # based on speed projection
                        for fuzz in missingGPS:
                            # need to use camera clock because GPS clock can stand still
                            # when not at least trying to acquire
                            fint = self.total_seconds(fuzz.localtime-lastAcq.localtime)
                            fuzzdistance = (distance * (fint/interval))
                            fuzz['fuzzdistance'] = fuzzdistance
                            fuzz['errSpeed'] = errorSpeed
                            fuzz['fuzzlat'], fuzz['fuzzlon'] = self.project(
                                lastAcq.GPSLatitude, lastAcq.GPSLongitude,
                                bearing, fuzzdistance)
                            fuzz['fuzzbearing'] = bearing
                            fuzz['projlat'], fuzz['projlon'] = self.project(
                                lastAcq.GPSLatitude, lastAcq.GPSLongitude,
                                lastAcq.GPSTrack, fint * lastAcq.GPSSpeed)
                            fuzz['projerr'] = self.haversine(
                                fuzz.projlat, fuzz.projlon,
                                fuzz.fuzzlat, fuzz.fuzzlon)

                    lastAcq = image
                    missingGPS = []

    def parse(self):
        self.parsetime()
        self.sortslices()
        self.pass2()
        self.pass3()
