#    Sample main.py Tornado file
#    (for Tornado on Heroku)
#
#    Author: Mike Dory | dory.me
#    Created: 11.12.11 | Updated: 06.02.13
#    Contributions by Tedb0t, gregory80
#
# ------------------------------------------

#!/usr/bin/env python
import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import autoreload, websocket

from Sun import Sun
import simplejson as json

# import and define tornado-y things
from tornado.options import define
define("port", default=5000, help="run on the given port", type=int)


# application settings and handle mapping info
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/sun", SunHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


# the main page
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if 'GOOGLEANALYTICSID' in os.environ:
            google_analytics_id = os.environ['GOOGLEANALYTICSID']
        else:
            google_analytics_id = False

        self.render(
            "main.html",
            page_title='Heroku Funtimes',
            page_heading='Hi!',
            google_analytics_id=google_analytics_id,
        )

class SunHandler(tornado.web.RequestHandler):
    def get(self):
        arguments = self.request.arguments
        if 'lat' in arguments and 'lon' in arguments:
            lat = float(self.get_argument('lat'))
            lon = float(self.get_argument('lon'))
            extended = True if 'extended' in arguments else False
                

            year = 2013
            month = 6
            day = 21
            obj = {}
            obj["extended"] = extended
            obj["lat"] = lat
            obj["lon"] = lon

            obj["year"] = year
            obj["month"] = month
            obj["day"] = day

            obj["sunrise"], obj["sunset"] = Sun.sunRiseSet(year, month, day, lon, lat)
            obj["sunRiseSet"] = Sun.sunRiseSet(year, month, day, lon, lat)
            obj["dayLength"] = Sun.dayLength(year, month, day, lon, lat)

            if extended is True:
                obj["aviationTime"] = Sun.aviationTime(year, month, day, lon, lat)
                obj["civilTwilight"] = Sun.civilTwilight(year, month, day, lon, lat)
                obj["dayCivilTwilightLength"] = Sun.dayCivilTwilightLength(year, month, day, lon, lat)
                obj["nauticalTwilight"] = Sun.nauticalTwilight(year, month, day, lon, lat)
                obj["dayNauticalTwilightLength"] = Sun.dayNauticalTwilightLength(year, month, day, lon, lat)
                obj["astronomicalTwilight"] = Sun.astronomicalTwilight(year, month, day, lon, lat)
                obj["dayAstronomicalTwilightLength"] = Sun.dayAstronomicalTwilightLength(year, month, day, lon, lat)

            self.write(json.dumps(obj))
        else:
            self.write('missing lat or lon')

# RAMMING SPEEEEEEED!
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)

    # start it up
    ioloop = tornado.ioloop.IOLoop.instance()
    autoreload.start(ioloop)
    ioloop.start()


if __name__ == "__main__":
    main()
