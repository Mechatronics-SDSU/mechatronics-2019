#!/bin/bash
gst-launch-1.0 autovideosrc ! video/x-raw,width=1280,height=720 ! jpegenc ! rtpjpegpay ! udpsink host=192.168.1.1 port=5200
