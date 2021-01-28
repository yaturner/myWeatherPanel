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
    global icons

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

    def loadIcon(self, iconId):
        url = "http://openweathermap.org/img/w/" + iconId + ".png"
        r = requests.get(url, allow_redirects=True)
        imgfile = StringIO(r.content)
        img = Image.open(imgfile)
        rgba = np.array(img)
        rgba[rgba[...,-1]==0] = [0, 0, 0, 0]
        im = Image.fromarray(rgba)
        im = self.trimImage(im)
        im.thumbnail((36, 36))
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
        # prime the dictionary with the most common
        self.icons = {}
        self.loadIcon("01d")
        self.loadIcon("02d")
        self.loadIcon("03d")
        self.loadIcon("10d")
        self.loadIcon("10n")
        self.loadIcon("02n")
        self.loadIcon("03n")
        
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

        ypos = self.offscreen_canvas.height - 4
        self.xpos=self.offscreen_canvas.width

        imgfile = StringIO(self.icons["10n"])
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
            
            self.offscreen_canvas.SetImage(im.convert('RGB'), 42, 2*lineHeight + 4)

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
        
        

