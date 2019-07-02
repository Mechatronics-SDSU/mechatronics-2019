#!/bin/bash
gst-launch-1.0 udpsrc port=5200 ! tee name=t t. ! queue ! application/x-rtp, payload=96 ! rtpjpegdepay ! jpegdec ! autovideosink t. ! queue ! application/x-rtp, payload=96 ! rtpjpegdepay ! jpegdec ! decodebin ! videoconvert ! filesink location=SubPOV.mp4
