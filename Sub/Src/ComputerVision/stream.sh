#!/bin/bash
gst-launch-1.0 v4l2src ! 'video/x-raw, width=480, height=620, framerate=30/1' ! videoconvert ! jpegenc ! rtpjpegpay ! udpsink host=192.168.1 port=5200
