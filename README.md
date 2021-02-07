WeatherPanel
============

My wife is always wondering about the weather, if it going to be too hot today, too hunid, and what about the rest of the week. So I deciced to create a LED panel display for her that would answer all her questions and give me an excuse to learn about LED Panels.

Ok, full disclosure, the lockdown was driving me nutz and I really didn't care all that much about the weather, I just needed something to do.

This work is based largely on the work of others and I try to give credit where I can


OverView
--------

This project was written in python on a Raspberry Pi 3B+, however almost any RPi can be used that supports WiFi. I actually run the project on a Raspberry Pi Zero WH. The project evolved as I learned more and more about using LED Panels and writing large python projects, so I am sure there are multiple places where the code can be made better, feel free to give me feedback. Here is an example of what the completed project looks like.


![Figure 1!](/images/figure1.jpg)

The left hand side shows today's temperature and humidity, the right hand side cycles through the week showing the high/low temperatures and the weather icon for each day. Below that is the wind speed and direction, and below that is a scrolling text that shows today's weather alerts, if there are any.

Hardware
--------

1. 4 64x32 Led Panels with magnetic feet, these can be ordered from Amazon, AdaFruit or DigiKey among others. I used a 4mm pitch (that is the distance between LEDs)
2. 2 Power supplies for the Led Panels, I used ALITOVE 5V 15Amp Power Supplies because they are specifically designed for LED Panels
3. 1 Rasperry Pi that supports WiFi, I developed this on a RPi 3B+ for speed, but I run the actual project on a Rpi Zero WH
4. 1 AdaFruit RGB Matrix Bonnet for Raspberry Pi
5. 1 M3 Male-Female Brass Spacer Standoff & Stainless Steel Screw Nut Assortment Kit (optional)
6. 8 MINI-MAGNET Feet for RGB LED Matric (optional)
7.5 16 Pins Connector Flat Ribbon Cable Female Connector Length 30cm 2.54mm Pitch (optional)
8. 2 6"x18" steel sheets (optional)

I do not have any wood/metalworking abilities or facilities, so the optional items were used to mount the LED panels without any kind of a custom frame. 

Software
--------



This code uses two main assets,

for detailed directions 
1. the excellant hzeller rpi-rgb-led-matrix, check out the github page 
   <https://github.com/hzeller/rpi-rgb-led-matrix>