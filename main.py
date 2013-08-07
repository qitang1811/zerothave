#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import fix_path
import webapp2
from Handlers import *
from views import *
import logging
import time


url_map = [('/', MainHandler),
           ('/story', StoryHandler),
           ('/travel', TravelHandler),
           ('/opinion', OpinionHandler),
           ('/man', ManHandler),
           ('/art', ArtHandler),
           ('/woman', WomanHandler),
           ('/technology',TechnologyHandler),
           ('/life', LifeHandler),
           ('/books',BooksHandler),
           ('/SuperAdminQQ', SuperAdmin)]


app = webapp2.WSGIApplication(url_map, debug=True)



