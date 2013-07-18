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

import json
import mock
import os
import unittest

from gpspixtrax import ddict
from gpspixtrax import exiftool

class Test_exiftool(unittest.TestCase):
    def test_invoke_exiftool(self):
        directory = os.path.dirname(__file__)
        images = [
            directory + '/data/dsc05521_arw.jpg',
            directory + '/data/dsc05870_arw.jpg',
            directory + '/data/dsc08142.jpg',
        ]
        d = exiftool.invoke_exiftool(images)
        expectedData = r'''[{
  "SourceFile": "%s/data/dsc05521_arw.jpg",
  "GPSDateTime": "2013:06:11 17:31:10.577Z",
  "GPSAltitude": 11.4,
  "GPSLatitude": 70.0833613888889,
  "GPSLongitude": 16.0796983333333,
  "GPSSpeed": 36.2,
  "GPSStatus": "V",
  "GPSTrack": 52.74,
  "GPSMeasureMode": 3,
  "DateTimeOriginal": "2013:06:12 07:27:01",
  "ShotNumberSincePowerUp": 1
},
{
  "SourceFile": "%s/data/dsc05870_arw.jpg",
  "GPSDateTime": "2013:06:12 13:49:52Z",
  "GPSAltitude": -0.6,
  "GPSLatitude": 70.984505,
  "GPSLongitude": 25.9636263888889,
  "GPSSpeed": 1.7,
  "GPSStatus": "V",
  "GPSTrack": 325.31,
  "GPSMeasureMode": 3,
  "DateTimeOriginal": "2013:06:12 20:29:38",
  "ShotNumberSincePowerUp": 198
},
{
  "SourceFile": "%s/data/dsc08142.jpg",
  "GPSDateTime": "2013:06:18 06:36:57.463Z",
  "GPSAltitude": 93.9,
  "GPSLatitude": 58.1362883333333,
  "GPSLongitude": 7.99556972222222,
  "GPSSpeed": 0.8,
  "GPSStatus": "A",
  "GPSTrack": 130.03,
  "GPSMeasureMode": 3,
  "DateTimeOriginal": "2013:06:18 08:37:01",
  "ShotNumberSincePowerUp": 1
}]
'''
        self.assertEquals(d, expectedData %(directory, directory, directory))

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_fetchdata(self, I):
        I.return_value = '''[{
  "SourceFile": "1/dsc05521_arw.jpg",
  "GPSDateTime": "2013:06:11 17:31:10.577Z",
  "GPSAltitude": 11.4,
  "GPSLatitude": 70.0833613888889,
  "GPSLongitude": 16.0796983333333,
  "GPSSpeed": 36.2,
  "GPSStatus": "V",
  "GPSTrack": 52.74,
  "GPSMeasureMode": 3,
  "DateTimeOriginal": "2013:06:12 07:27:01",
  "ShotNumberSincePowerUp": 1
},
{
  "SourceFile": "1/dsc05870_arw.jpg",
  "GPSDateTime": "2013:06:12 13:49:52Z",
  "GPSAltitude": -0.6,
  "GPSLatitude": 70.984505,
  "GPSLongitude": 25.9636263888889,
  "GPSSpeed": 1.7,
  "GPSStatus": "V",
  "GPSTrack": 325.31,
  "GPSMeasureMode": 3,
  "DateTimeOriginal": "2013:06:12 20:29:38",
  "ShotNumberSincePowerUp": 198
},
{
  "SourceFile": "2/dsc08142.jpg",
  "GPSDateTime": "2013:06:18 06:36:57.463Z",
  "GPSAltitude": 93.9,
  "GPSLatitude": 58.1362883333333,
  "GPSLongitude": 7.99556972222222,
  "GPSSpeed": 0.8,
  "GPSStatus": "A",
  "GPSTrack": 130.03,
  "GPSMeasureMode": 3,
  "DateTimeOriginal": "2013:06:18 08:37:01",
  "ShotNumberSincePowerUp": 1
}]
        '''
        i = exiftool.fetchdata(['1/dsc05521_arw.jpg',
                                '1/dsc05870_arw.jpg',
                                '2/dsc08142.jpg'])
        self.assertEquals(len(i), 2)
        self.assertEquals(len(i[0]), 2)
        self.assertEquals(len(i[1]), 1)
        self.assertEquals(isinstance(i[0][0], ddict.ddict), True)
        I.assert_called('-n', '-j',
                        '-GPSDateTime',
                        '-GPSAltitude',
                        '-GPSLatitude',
                        '-GPSLongitude',
                        '-GPSSpeed',
                        '-GPSStatus',
                        '-GPSTrack',
                        '-GPSMeasureMode',
                        '-DateTimeOriginal',
                        '-ShotNumberSincePowerUp',
                        'dsc05521_arw.jpg',
                        'dsc05870_arw.jpg',
                        'dsc08142.jpg')
