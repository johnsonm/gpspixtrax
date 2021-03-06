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

from plumbum.cmd import xz

from gpspixtrax import exiftool
from gpspixtrax import gpspixtrax

class Test_gpspixtrax(unittest.TestCase):
    def assertNoHalfHourTimezone(self, imagedata):
        for slice in imagedata:
            for image in slice:
                if 'tzoffset' in image:
                    self.assertEqual(image.tzoffset % 1.0, 0.0)

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_parse_process(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/selectdata.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        # 12 subdirectories for 12 days
        self.assertEquals(len(imagedata), 12)
        # images sorted within the slices
        G = gpspixtrax.GPSPixTrax(imagedata)
        for tag in ('gpstime', 'localtime', 'pseudolocaltime', 'tzoffset', 'tzseconds'):
            self.assertEqual(set(tag in i for i in imagedata), set((False,)))
        I.assert_called_once_with(filelist)

        G.parsetime()
        for slice in imagedata:
            for tag in ('gpstime', 'localtime', 'pseudolocaltime'):
                self.assertEqual(set(tag in i for i in slice), set((True,)))
            for tag in ('tzoffset', 'tzseconds'):
                self.assertEqual(
                    set(tag in i for i in slice if i.GPSStatus == 'A'),
                    set((True,)))
                self.assertEqual(
                    set(tag in i for i in slice if i.GPSStatus == 'V'),
                    set((False,)))

        G.sortslices()
        for slice in imagedata:
            filenames = [os.path.basename(x.SourceFile) for x in slice]
            self.assertEquals(filenames, sorted(filenames))

        G.pass2()
        G.pass3()
        self.assertNoHalfHourTimezone(imagedata)

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_parse_end_inactive(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/initialoffset.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parsetime()
        for tag in ('tzoffset', 'tzseconds'):
            # one has tz info, the others do not
            self.assertEqual(set(tag in i for i in imagedata[0]),
                             set((False, True)))
        G.sortslices()
        G.pass2()
        for tag in ('tzoffset', 'tzseconds'):
            # tz info has been copied from the one known good image
            self.assertEqual(set(tag in i for i in imagedata[0]), set((True,)))

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_parse_no_active(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/nooffset.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parsetime()
        for tag in ('tzoffset', 'tzseconds'):
            # no valid GPS stamps, so nothing to trust yet
            self.assertEqual(set(tag in i for i in imagedata[0]), set((False,)))
        G.sortslices()
        G.pass2()
        for tag in ('tzoffset', 'tzseconds'):
            # no valid GPS stamps to copy, so nothing to trust yet
            self.assertEqual(set(tag in i for i in imagedata[0]), set((False,)))
        G.pass3()
        for tag in ('tzoffset', 'tzseconds', 'gpsStampAge'):
            # now that we know no valid GPS stamps nearby, just guess
            self.assertEqual(set(tag in i for i in imagedata[0]), set((True,)))
        self.assertNoHalfHourTimezone(imagedata)

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_parse_too_far_apart(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/farapart.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parsetime()
        for tag in ('tzoffset', 'tzseconds'):
            # one has tz info, the others do not
            self.assertEqual(set(tag in i for i in imagedata[0]),
                             set((False, True)))
        G.sortslices()
        G.pass2()
        for tag in ('tzoffset', 'tzseconds'):
            # GPS stamp too far away to trust
            self.assertEqual(set(tag in i for i in imagedata[0]),
                             set((False, True)))
        G.pass3()
        for tag in ('tzoffset', 'tzseconds'):
            # localtime and gps time close enough together to guess
            self.assertEqual(set(tag in i for i in imagedata[0]), set((True,)))
        self.assertNoHalfHourTimezone(imagedata)

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_parse_disjoint_clocks(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/disjointclockinvalid.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parsetime()
        for tag in ('tzoffset', 'tzseconds'):
            self.assertEqual(tag in imagedata[0][0], False)
        G.sortslices()
        G.pass2()
        for tag in ('tzoffset', 'tzseconds'):
            self.assertEqual(tag in imagedata[0][0], False)
        G.pass3()
        for tag in ('tzoffset', 'tzseconds', 'gpsStampAge'):
            # localtime and gps time not close enough together to guess
            self.assertEqual(tag in imagedata[0][0], False)
        self.assertNoHalfHourTimezone(imagedata)

    @mock.patch('gpspixtrax.exiftool.invoke_exiftool')
    def test_parse_too_far_apart(self, I):
        directory = os.path.dirname(__file__)
        I.return_value = xz(
            '-d', '-c', directory + '/data/farapart.json.xz')
        filelist = mock.Mock()
        imagedata = exiftool.fetchdata(filelist)
        # hack the data to have the same timestamp but incomparable filenames that would
        # sort if they were comparable (had the same three-character prefix)
        imagedata[0][1].GPSDateTime = imagedata[0][0].GPSDateTime
        imagedata[0][1].SourceFile = imagedata[0][0].SourceFile.replace('dsc04', 'img03')
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parsetime()
        self.assertEquals(imagedata[0][0].SourceFile[0:5], 'dsc04')
        self.assertEquals(imagedata[0][1].SourceFile[0:5], 'img03')
        G.sortslices()
        # didn't change
        self.assertEquals(imagedata[0][0].SourceFile[0:5], 'dsc04')
        self.assertEquals(imagedata[0][1].SourceFile[0:5], 'img03')

        imagedata[0][1].SourceFile = imagedata[0][0].SourceFile.replace('dsc', 'img')

    @mock.patch('gpspixtrax.gpspixtrax.GPSPixTrax.parsetime')
    @mock.patch('gpspixtrax.gpspixtrax.GPSPixTrax.sortslices')
    @mock.patch('gpspixtrax.gpspixtrax.GPSPixTrax.pass2')
    @mock.patch('gpspixtrax.gpspixtrax.GPSPixTrax.pass3')
    def test_parse(self, P3, P2, S, T):
        imagedata = mock.Mock()
        G = gpspixtrax.GPSPixTrax(imagedata)
        G.parse()
        T.assert_called_once_with()
        S.assert_called_once_with()
        P2.assert_called_once_with()
        P3.assert_called_once_with()
