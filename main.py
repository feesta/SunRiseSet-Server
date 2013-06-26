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
import datetime, time

# import and define tornado-y things
from tornado.options import define
define("port", default=5000, help="run on the given port", type=int)

MINUTE = 60.0 # number of seconds in a minute
HOUR = 3600.0 # number of seconds in an hour

# application settings and handle mapping info
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler)
        ]
        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        obj = {'notes':'Returns info about the sunrise/sunset for a location. All values are in UTC hours', 'credits':'Uses the Python port of sunsetrise.c: https://github.com/mabroor/suncal Host set up by Jeff Easter (http://feesta.com)'}

        arguments = self.request.arguments
        if 'lat' in arguments and 'lon' in arguments:

            lat = float(self.get_argument('lat'))
            lon = float(self.get_argument('lon'))
            obj["lat"] = lat
            obj["lon"] = lon

            extended = True if 'extended' in arguments else False
            obj["extended"] = extended

            now = datetime.datetime.now()
            year = int(self.get_argument('year')) if 'year' in arguments else now.year
            month = int(self.get_argument('month')) if 'month' in arguments else now.month
            day = int(self.get_argument('day')) if 'day' in arguments else now.day
            obj["year"] = year
            obj["month"] = month
            obj["day"] = day

            dt = datetime.datetime(year, month, day)
            day_seconds = time.mktime(dt.timetuple())

            obj["day_seconds"] = day_seconds
            obj["sunrise"], obj["sunset"] = Sun.sunRiseSet(year, month, day, lon, lat)
            obj["sunrise_seconds"] = int(obj["sunrise"] * HOUR + day_seconds)
            obj["sunRiseSet"] = Sun.sunRiseSet(year, month, day, lon, lat)
            obj["sunset_seconds"] = int(obj["sunset"] * HOUR + day_seconds)
            obj["dayLength"] = Sun.dayLength(year, month, day, lon, lat)
            obj["dayLength_seconds"] = int(obj["dayLength"] * HOUR)

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
            obj['status'] = 'error'
            obj['message'] = 'missing lat or lon'
            obj['arguments required'] = 'lat, lon'
            obj['arguments optional'] = 'extended, year, month, day'
            self.write(json.dumps(obj))

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)

    ioloop = tornado.ioloop.IOLoop.instance()
    autoreload.start(ioloop)
    ioloop.start()


if __name__ == "__main__":
    main()
