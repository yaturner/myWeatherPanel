#!/usr/bin/python
from samplebase import SampleBase
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from PIL import Image
import time
from datetime import datetime
import paho.mqtt.client as mqtt # Import the MQTT library
import json
import signal
import sys
import requests
import io
from cStringIO import StringIO
import numpy as np
from os import path
import configparser


class panelApp(SampleBase):

    def handler(self, signum, frame):
        self.offscreen_canvas.Clear()
        sys.exit(0)

    """
    Initialize
    """
    def __init__(self, *args, **kwargs):
        super(panelApp, self).__init__(*args, **kwargs)
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGTERM, self.handler)
    
    """
    get the curent weather data, if it is unavailable then just use what we have
    from the last successful call
    """
    def getWeather(self):
        print("getting weather from {}?{} at {}".format(self.weatherUri, self.params,
                                                        datetime.now().strftime("%c")))
        try:
            r = requests.get(url=self.weatherUri, params=self.params)
        except:
            e = sys.exc_info()[0]
            print("Exception found while getting weather data: " + str(e))
            return
        data = r.json()
        self.parseData(data)
        
    """
    parse the Json returned from getWeather()
    """
    def parseData(self, data):
        current=data["current"]
        self.sunrise=current["sunrise"]
        self.sunset=current["sunset"]
        self.temperatureNow=current["temp"]
        self.clouds=current["clouds"]
        self.windSpeed=current["wind_speed"]
        self.windDir=self.degToCompass(int(current["wind_deg"]))
        self.humidity=current["humidity"]
        # there may not be any alerts currently
        try:
            alerts=data["alerts"]
        except:
            alerts=[]
        iconId = current["weather"][0]["icon"]
        self.loadAndSaveIcon(iconId)
        filename = "./icons" + iconId + ".png"
        self.weatherIcon = Image.open(filename)

        i = 0
        self.alertArray = []
        for alert in alerts:
            self.alertArray.append(alert["description"].replace("\n", " "))
            i = i + 1

        self.daily = data["daily"]
        temperatures = self.daily[0]["temp"]
        self.minTemp = temperatures["min"]
        self.maxTemp = temperatures["max"]


    def degToCompass(self, num):
        val=int((num/22.5)+.5)
        arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
        return arr[(val % 16)]
    

    """
    Image handlers
    """
    def trimImage(self, image):
        width, height = image.size
        image_data = np.asarray(image)
        image_data_bw = image_data.max(axis=2)
        non_empty_columns = np.where(image_data_bw.max(axis=0)>0)[0]
        non_empty_rows = np.where(image_data_bw.max(axis=1)>0)[0]
        cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns),
                   max(non_empty_columns))
        image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]
        new_image = Image.fromarray(image_data_new)
        return new_image


    """
    load and save the png to disk iffi it is not already saved
    """
    def loadAndSaveIcon(self, iconId):
        url = "http://openweathermap.org/img/w/" + iconId + ".png"
        filename = "./icons" + iconId + ".png"
        if not path.exists(filename): 
            r = requests.get(url, allow_redirects=True)
            imgfile = StringIO(r.content)
            img = Image.open(imgfile)
            rgba = np.array(img)
            rgba[rgba[...,-1]==0] = [0, 0, 0, 0]
            im = Image.fromarray(rgba)
            im = self.trimImage(im)
            im.thumbnail((36, 36))
            im.save(filename)
        
        
    def drawImage(self, imageFilename):
        image=Image.open(imageFilename)
        image.thumbnail((self.iconSize, self.iconSize), Image.ANTIALIAS)
        self.matrix.SetImage(image.convert('RGB'), self.xpos, 30)
        


    def drawScreen(self):
        pos = 0
        alertNo = 0
        lineHeight = 10

        data = self.getWeather()

        ypos = self.offscreen_canvas.height - self.lineSpacing
        self.xpos=self.offscreen_canvas.width

        loopCounter = 0
        halfhour = 8 * 30 * 60 
        tensec = 8 * 10 
        
        dayIndex = 0
        dayName = "Today"
        
        # initialize the weather info iffi the http request has completed
        #
        if not self.weatherIcon == None:
            temperatures = self.daily[0]["temp"]
            minTemp = temperatures["min"]
            maxTemp = temperatures["max"]
            iconId = self.daily[0]["weather"][0]["icon"]
            self.loadAndSaveIcon(iconId)
            filename = "./icons" + iconId + ".png"
            weatherIcon = Image.open(filename)


        while True:
            # use this to time the loop and set the intervals for getWeather() and dayIndex
            # on a Pi Zero W it's 8 loops/sec
            # print("loopCounter = {} at {}".format(loopCounter, datetime.now().strftime("%c")))
            self.offscreen_canvas.Clear()
            now = datetime.now()
            timeNow = now.strftime("%I:%M")
            dateNow = now.strftime("%a %b %-d %Y")
            self.offscreen_canvas.Clear()

            # get the weather info every 30 min
            if loopCounter % halfhour == 0:
                data = self.getWeather()
                loopCounter = 0

            # init the weather info iffi the http request has completed
            #
            if not self.weatherIcon == None:
                # increment the dayIndex every minute
                if loopCounter % tensec == 0:
                    dayIndex = (dayIndex + 1) % 7
                    if dayIndex == 0:
                        dayName = "Today"
                    else:
                        dayName = time.strftime("%a", time.localtime(self.daily[dayIndex]["dt"]))
                    temperatures = self.daily[dayIndex]["temp"]
                    minTemp = temperatures["min"]
                    maxTemp = temperatures["max"]
                    iconId = self.daily[dayIndex]["weather"][0]["icon"]
                    self.loadAndSaveIcon(iconId)
                    filename = "./icons" + iconId + ".png"
                    weatherIcon = Image.open(filename)

                
            # draw the date
            slen1 = graphics.DrawText(self.offscreen_canvas, self.font,
                                    12, lineHeight, self.textColor, dateNow)
            # draw the time
            slen2 = graphics.DrawText(self.offscreen_canvas, self.fontB,
                                    50, 2 * lineHeight, self.textColor, timeNow)
            # draw the alert text
            if len(self.alertArray) > 0 and alertNo < len(self.alertArray):
                slen3 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                         self.xpos, ypos, graphics.Color(255, 20, 20),
                                         self.alertArray[alertNo])
    
            # draw the weather info iffi the http request has completed
            #
            if not self.weatherIcon == None:
                self.offscreen_canvas.SetImage(weatherIcon.convert('RGB'), 42,
                                               2*lineHeight + self.lineSpacing)

                # draw the label
                slen = graphics.DrawText(self.offscreen_canvas, self.fontSmall,
                                         2, 2*lineHeight+self.lineSpacing, graphics.Color(255, 255, 255),
                                         "Now:")
                
                # draw the current temperature
                slen4 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                          2, 3*lineHeight+self.lineSpacing, graphics.Color(0, 255, 0),
                                          str(int(self.temperatureNow)) + u'\u00b0'+"F")
                # draw the hunidity
                slen4 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                          2, 4*lineHeight+self.lineSpacing, graphics.Color(0, 128, 255),
                                          str(int(self.humidity)) + "%")
                # draw the wind speed and direction
                slen4 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                          12, 5*lineHeight + 1, graphics.Color(0, 255, 255),
                                          str(int(self.windSpeed)) + "mph from the " + self.windDir)
                
                
                # draw the label
                slen = graphics.DrawText(self.offscreen_canvas, self.fontSmall,
                                         50+46, 2*lineHeight+self.lineSpacing, graphics.Color(255, 255, 255),
                                         dayName + ":")
                
                # draw the min/max temperatures
                slen5 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                          50+36, 3*lineHeight+self.lineSpacing,
                                          graphics.Color(0, 255, 128),
                                          str(int(minTemp)) + "/" +
                                          str(int(maxTemp)) + u'\u00b0'+"F")
                
            
            self.xpos = self.xpos - 1;
            if len(self.alertArray) > 0 and (self.xpos + slen3) < 0:
                self.xpos = self.offscreen_canvas.width 
                alertNo = alertNo + 1
                if alertNo >= len(self.alertArray):
                    alertNo = 0
                
            time.sleep(0.05)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            loopCounter = loopCounter + 1

    """
    error handler for options, if second arg is '', the the whole section is missing
    or invalid
    """
    def handleOptionsError(self, section, key):
        if key == '':
            print("The options section '"+section+"' is missing or invalid")
        else:
            print("The key '"+key+"' in section '"+section+"' is missing or invalid")
        self.offscreen_canvas.Clear()
        sys.exit(-1)


    def setup(self):
        config = configparser.ConfigParser()
        config.read('weatherApp.cfg')
        
        # Configuration for the led panels, if it doesn't exist
        options = RGBMatrixOptions()
        #set the default values
        options.cols = 64
        options.rows = 32
        options.chain_length = 4
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.pixel_mapper_config="U-mapper"
        if 'LED' in config:
            ledOptions = config['LED']
            if 'cols' in ledOptions:
                options.cols = int(ledOptions['cols'])
            if 'rows' in ledOptions:
                options.rows = int(ledOptions['rows'])
            if 'chain_length' in ledOptions:
                options.chain_length = int(ledOptions['chain_length'])
            if 'parallel' in ledOptions:
                options.parallel = int(ledOptions['parallel'])
            if 'hardware_mapping' in ledOptions:
                options.hardware_mapping = ledOptions['hardware_mapping']
            if 'pixel_mapper_config' in ledOptions:
                options.pixel_mapper_config = ledOptions['pixel_mapper_config']
        self.matrix = RGBMatrix(options = options)

        if 'WEATHER' in config:
            weatherOptions = config['WEATHER']
            if 'lat' in weatherOptions:
                lat = weatherOptions['lat']
            else:
                self.handleOptionsError('WEATHER', 'lat')
            if 'lon' in weatherOptions:
                lon = weatherOptions['lon']
            else:
                self.handleOptionsError('WEATHER', 'lon')
            if 'units' in weatherOptions:
                units = weatherOptions['units']
            else:
                units = 'imperial'
            if 'appid' in weatherOptions:
                appid = weatherOptions['appid']
            else:
                self.handleOptionsError('WEATHER', 'appid')
        else:
            self.handleOptionsError('WEATHER', '')
        self.weatherUri="https://api.openweathermap.org/data/2.5/onecall"
        self.params="lat="+lat+"&lon="+lon+"&appid="+appid+"&units="+units
                

        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.font.LoadFont("./fonts/7x13.bdf")
        self.fontB = graphics.Font()
        self.fontB.LoadFont("./fonts/7x13B.bdf")
        self.fontMed = graphics.Font()
        self.fontMed.LoadFont("./fonts/6x9.bdf")
        self.fontSmall = graphics.Font()
        self.fontSmall.LoadFont("./fonts/5x8.bdf")
        self.textColor = graphics.Color(0, 0, 128)
        self.xpos = 0
        self.lineSpacing = 1
    
        self.degreeSign = '\u00B0'
        
        self.alertArray = []
        self.weatherIcon = None

def main():
    app = panelApp()
    app.setup()
    app.drawScreen()

        
# Main function
if __name__ == "__main__":
    main()
    
        

