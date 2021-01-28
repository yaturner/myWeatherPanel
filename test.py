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

class panelApp(SampleBase):
    global offscreen_canvas
    global font
    global textColor
    global xpos
    global pos
    global weather_icons
    global iconSize
    global weatherClient
    global alertArray

    def handler(self, signum, frame):
        sys.exit(0)
    
    def __init__(self, *args, **kwargs):
        super(panelApp, self).__init__(*args, **kwargs)
        self.sig = signal.SIGINT
        signal.signal(self.sig, self.handler)
    

    # >>>>>>>>>MQTT<<<<<<<<<<< 
    def onMessage(self, client, userdata, message):
        topic = str(message.topic)
        msg = str(message.payload)
        jsonString=json.loads(msg)
        current=jsonString["current"]
        sunrise=current["sunrise"]
        sunset=current["sunset"]
        temp=current["temp"].split(u'\xb0')[0] + "'F"
        clouds=current["clouds"]
        windSpeed=current["wind_speed"]
        alerts=jsonString["alerts"]
        i = 0
        self.alertArray = []
        for alert in alerts:
            self.alertArray.append(alert["description"].replace("\n", " "))
            i = i + 1

    def loadIcon(self, iconId):
        url = "http://openweathermap.org/img/w/" + iconId + ".png"
        r = requests.get(url, allow_redirects=True)
        imgfile = StringIO(r.content)
        img = Image.open(imgfile)
        rgba = np.array(img)
        rgba[rgba[...,-1]==0] = [0, 0, 0, 0]
        im = Image.fromarray(rgba)
        im.thumbnail((24, 24))
        output = io.BytesIO()
        im.save(output, format='png')
        self.icons[iconId] = output.getvalue()

        
    def setup(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.font.LoadFont("../../../../fonts/7x13.bdf")
        self.textColor = graphics.Color(0, 0, 128)
        self.xpos = 0
        self.alertArray = []
        self.weatherIcons=["Moon.png", "Rain_Heavy.png", "Rain_Light.png",
                          "Rain_Light_Sun.png", "Rain_Medium.png", "Sun.png",
                          "Thunder.png", "Wind.png"]
        self.iconSize=16
        self.icons = {}
        # prime the dictionary with the most common

        self.weatherClient = mqtt.Client("IoTMaster")
        self.weatherClient.connect("IoTMaster.local", 1883)
        self.weatherClient.subscribe("weather")
        self.weatherClient.on_message=self.onMessage



    def drawImage(self, imageFilename):
        image=Image.open(imageFilename)
        image.thumbnail((self.iconSize, self.iconSize), Image.ANTIALIAS)
        self.matrix.SetImage(image.convert('RGB'), self.xpos, 30)
        


    def drawClock(self):
        first = True
        pos = 0
        alertNo = 0
        slen1=0
        slen2=0
        slen3=0
        lineHeight = 10

        ypos = self.offscreen_canvas.height - lineHeight
        self.xpos=self.offscreen_canvas.width

        self.loadIcon("01d")
        imgfile = StringIO(self.icons["01d"])
        im = Image.open(imgfile)

        while True:
            self.offscreen_canvas.Clear()
            now = datetime.now()
            timeNow = now.strftime("%I:%M")
            dateNow = now.strftime("%a %b %-d %Y")
            self.offscreen_canvas.Clear()
            slen1 = graphics.DrawText(self.offscreen_canvas, self.font,
                                    0, lineHeight, self.textColor, dateNow)
            slen2 = graphics.DrawText(self.offscreen_canvas, self.font,
                                    50, 2 * lineHeight, self.textColor, timeNow)
            if len(self.alertArray) > 0:
                slen3 = graphics.DrawText(self.offscreen_canvas, self.font,
                                         self.xpos, ypos, self.textColor,
                                         self.alertArray[alertNo])
            
            self.offscreen_canvas.SetImage(im.convert('RGB'), 42, 2*lineHeight)

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
        app.drawClock()
        
        

