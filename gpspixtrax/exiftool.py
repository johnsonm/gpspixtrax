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
import os

from plumbum.cmd import exiftool

import ddict

def invoke_exiftool(filelist):
    return exiftool(
        '-n', '-j',
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
        *filelist)

def fetchdata(filelist):
    'return list of lists of images per directory specified in assumed-sorted filelist'
    imagelist = [ddict.ddict(x)
                 for x in json.loads(invoke_exiftool(filelist))]
    imagedata = []
    currentslice = []
    last = imagelist[0]
    for image in imagelist:
        thisDir = os.path.dirname(image.SourceFile)
        if not currentslice:
            currentslice.append(image)
        else:
            if lastDir == thisDir:
                currentslice.append(image)
            else:
                imagedata.append(currentslice)
                currentslice = [image]
        lastDir = thisDir
    imagedata.append(currentslice)
    return imagedata
