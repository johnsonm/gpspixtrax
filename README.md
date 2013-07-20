gpspixtrax
==========

My camera records GPS stamps in pictures.  It does this without
regard for the current validity of the GPS reading; it just marks
invalid records.  This is good most of the time.

Given a set of pictures taken in sequence, it should be possible to
use heuristics to infer more accurate locations for some pictures,
and to remove location data from pictures without any reasonable
confidence in their location.

This project is an attempt to implement such semantics.  It is
currently a mess of scripting I'm writing as I look through data
to see whether there's anything useful to do here, or whether I
ought to just drop all the invalid fixes because there is too much
noise.

It is written in Python, works on at least Python 2.6, requires
python-plumbum, python-dateutil, and exiftool installed.  The test
suite requires the xz executable, testutils, and coverage as well.


Modifications
=============

You are welcome to fork gpspixtrax and to contribute your changes.
If you do so, please provide the "prominent notices stating that
You changed the files" as required in the Apache license as correct
and complete name and correct email address in the `Author` field
of the Git commits that you make, rather than changes in the
actual *contents* of the files, to avoid difficulty merging.  You
should of course add any necessary copyright statements to files.

The CONTRIBUTING.md file describes the sign-off process required
for contributions.

Please provide test cases for modifications.  Running `make test`
will run all test cases.

License
=======

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Copyright 2013 Michael K Johnson
