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

import mock
import os
import unittest

from lxml import etree

from plumbum.cmd import xz

from gpspixtrax import ddict
from gpspixtrax import exiftool
from gpspixtrax import gpspixtrax
from gpspixtrax import kml

class Test_KMLPaths(unittest.TestCase):
    def assert_no_repeats(self, xml):
        coordinates = str(xml.Document.Placemark.LineString.coordinates).split()
        for i in range(len(coordinates)-1):
            self.assertNotEqual(coordinates[i], coordinates[i+1])

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_all(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/selectdata.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parse()
        for slice in imagedata:
            K = kml.KMLPaths(slice)
            k = K.KML('foo', kml.MODE.valid)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.gps)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.projected)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.interpolated)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.valid & kml.MODE.projected)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.valid & kml.MODE.interpolated)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.gps & kml.MODE.projected)
            self.assert_no_repeats(k)
            k = K.KML('foo', kml.MODE.gps & kml.MODE.interpolated)
            self.assert_no_repeats(k)
