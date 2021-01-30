#!/usr/bin/python
from samplebase import SampleBase
from rgbmatrix import graphics
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

class panelApp(SampleBase):
    global offscreen_canvas
    global font
    global textColor
    global xpos
    global pos
    global weather_icons
    global iconSize
    global weatherClient
    global todaysIcon
    global alertArray
#    global lineSpacing

    def handler(self, signum, frame):
        sys.exit(0)

    """
    Initialize
    """
    def __init__(self, *args, **kwargs):
        super(panelApp, self).__init__(*args, **kwargs)
        self.sig = signal.SIGINT
        signal.signal(self.sig, self.handler)
    

    """
    MQTT
    """
    def onMessage(self, client, userdata, message):
        topic = str(message.topic)
        msg = str(message.payload)
        jsonString=json.loads(msg)
        current=jsonString["current"]
        self.sunrise=current["sunrise"]
        self.sunset=current["sunset"]
        self.temperatureNow=current["temp"]
        self.clouds=current["clouds"]
        self.windSpeed=current["wind_speed"]
        alerts=jsonString["alerts"]
        iconId = current["weather"][0]["icon"]
        self.loadAndSaveIcon(iconId)
        filename = iconId + ".png"
        self.weatherIcon = Image.open(filename)

        i = 0
        self.alertArray = []
        for alert in alerts:
            self.alertArray.append(alert["description"].replace("\n", " "))
            i = i + 1

        daily = jsonString["daily"]
        temperatures = daily[0]["temp"]
        self.minTemp = temperatures["min"]
        self.maxTemp = temperatures["max"]

        
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
        r = requests.get(url, allow_redirects=True)
        filename = iconId + ".png"
        if not path.exists(filename): 
            imgfile = StringIO(r.content)
            img = Image.open(imgfile)
            rgba = np.array(img)
            rgba[rgba[...,-1]==0] = [0, 0, 0, 0]
            im = Image.fromarray(rgba)
            im = self.trimImage(im)
            im.thumbnail((36, 36))
            im.save(filename)
        
#        output = io.BytesIO()
#        im.save(output, format='png')
#        self.icons[iconId] = output.getvalue()

        
    def setup(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.font.LoadFont("../../../../fonts/7x13.bdf")
        self.fontB = graphics.Font()
        self.fontB.LoadFont("../../../../fonts/7x13B.bdf")
        self.fontMed = graphics.Font()
        self.fontMed.LoadFont("../../../../fonts/6x9.bdf")
        self.textColor = graphics.Color(0, 0, 128)
        self.xpos = 0
        self.lineSpacing = 4
        self.degreeSign = str("\u00B0")
        self.alertArray = []
# prime the directory with the most common
        self.loadAndSaveIcon("01d")
        self.loadAndSaveIcon("02d")
        self.loadAndSaveIcon("03d")
        self.loadAndSaveIcon("10d")
        self.loadAndSaveIcon("10n")
        self.loadAndSaveIcon("02n")
        self.loadAndSaveIcon("03n")
        
        self.weatherClient = mqtt.Client("IoTMaster")
        self.weatherClient.connect("IoTMaster.local", 1883)
        self.weatherClient.subscribe("weather")
        self.weatherClient.on_message=self.onMessage

        self.weatherIcon = None


    def drawImage(self, imageFilename):
        image=Image.open(imageFilename)
        image.thumbnail((self.iconSize, self.iconSize), Image.ANTIALIAS)
        self.matrix.SetImage(image.convert('RGB'), self.xpos, 30)
        


    def drawScreen(self):
        first = True
        pos = 0
        alertNo = 0
        slen1=0
        slen2=0
        slen3=0
        lineHeight = 10

        ypos = self.offscreen_canvas.height - self.lineSpacing
        self.xpos=self.offscreen_canvas.width
        
        while True:
            self.offscreen_canvas.Clear()
            now = datetime.now()
            timeNow = now.strftime("%I:%M")
            dateNow = now.strftime("%a %b %-d %Y")
            self.offscreen_canvas.Clear()

            # draw the date
            slen1 = graphics.DrawText(self.offscreen_canvas, self.font,
                                    12, lineHeight, self.textColor, dateNow)
            # draw the time
            slen2 = graphics.DrawText(self.offscreen_canvas, self.fontB,
                                    50, 2 * lineHeight, self.textColor, timeNow)
            # draw the alert text
            if len(self.alertArray) > 0:
                slen3 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                         self.xpos, ypos, graphics.Color(255, 20, 20),
                                         self.alertArray[alertNo])
            # draw the weather icon
            if not self.weatherIcon == None:
                self.offscreen_canvas.SetImage(self.weatherIcon.convert('RGB'), 42,
                                               2*lineHeight + self.lineSpacing)

                # draw the current temperature
                slen4 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                          2, 2*(lineHeight+self.lineSpacing), graphics.Color(0, 255, 0),
                                          self.temperatureNow)
                # draw the min/max temperatures
                slen5 = graphics.DrawText(self.offscreen_canvas, self.fontMed,
                                          50+36, 2*(lineHeight+self.lineSpacing),
                                          graphics.Color(0, 255, 128),
                                          str(int(self.minTemp))+"/"+
                                          str(int(self.maxTemp))+"")
                
            
            self.xpos = self.xpos - 1;
            if (self.xpos + slen3) < 0:
                self.xpos = self.offscreen_canvas.width 
                alertNo = alertNo + 1
                if alertNo >= len(self.alertArray):
                    alertNo = 0
                
            if first:
                first = False
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            else:
                time.sleep(0.05)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            

# Main function
if __name__ == "__main__":
    app = panelApp()
    if (not app.process()):
        app.print_help()
    else:
        app.setup()
        app.weatherClient.loop_start()
        app.drawScreen()
        
        

