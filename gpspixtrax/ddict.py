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

class ddict(dict):
    def __getattr__(self, key):
        # allow . for fetch for easier reading
        return self[key]
    def __setattr__(self, key, value):
        # add keys only explicitly by [] to avoid bugs
        self[key]
        self[key] = value
