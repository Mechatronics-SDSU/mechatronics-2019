'''
Copyright 2019, Alexa Becerra, All rights reserved
Author: Alexa Becerra <alexa.becerra99@gmail.com>
Description: Aquisition of camera images and UDP streaming.
'''
import os
import signal
import PySpin
import sys
import gi
import io
from io import BytesIO

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst
from gi.repository import GdkX11, GstVideo

#Gst.debug_set_active(True)
#Gst.debug_set_default_threshold(3)
GObject.threads_init()
Gst.init(None)
global pipeline
global camera

'''
Gstreamer pipeline to handle buffers of images and UDP streaming.
'''
class PointGrey_AppSrc:

	def __init__(self):
		self.is_push_buffer_allowed = None
		self._mainloop = GObject.MainLoop.new(None, False)
		udp_sink_pipeline = "appsrc name=source ! image/jpeg,framerate=(fraction)30/1 ! decodebin ! videoscale ! capsfilter caps=video/x-raw,width=640,height=480 ! queue ! jpegenc ! rtpjpegpay ! udpsink host=127.0.0.1 port=5200"

		self._pipeline = Gst.parse_launch(udp_sink_pipeline)

		self._src = self._pipeline.get_by_name('source')
		self._src.connect('need-data', self.start_feed)
		self._src.connect('enough-data', self.stop_feed)

		self._src.set_property('format','time')
		self._src.set_property('do-timestamp', True)


	def start_feed(self,src,length):
		self.is_push_buffer_allowed = True

	def stop_feed(self,src):
		self.is_push_buffer_allowed = False

	def play(self):
		self._pipeline.set_state(Gst.State.PLAYING)

	def stop(self):
		self._pipeline.set_state(Gst.State.NULL)

	def run(self):
		self._mainloop.run()

	def push(self, filename):
		if self.is_push_buffer_allowed:
			handle = open(filename, 'rb');
			data = handle.read()
			handle.close()
			buf = Gst.Buffer.new_allocate(None, len(data),None)
			buf.fill(0,data)
			sample = Gst.Sample.new(buf, Gst.caps_from_string("image/jpeg, framerate=(fraction)30/1"),None,None)
			gst_flow_return = self._src.emit('push-sample',sample)

			if gst_flow_return != Gst.FlowReturn.OK:
				print("Error, Stopped streaming")

			else:
				'''print("Enough data on buffer.")'''

class Camera:
	def __init__(self):
		self._system = PySpin.System.GetInstance()
		# Get camera object
		self._cam_list = self._system.GetCameras()
		self._cam = self._cam_list.GetByIndex(0)
		# Initialize camera/Node mode/color format
		self._cam.Init()
		node_map = self._cam.GetNodeMap()

		node_acq_mode = PySpin.CEnumerationPtr(node_map.GetNode('AcquisitionMode'))
		node_acq_mode_cont = node_acq_mode.GetEntryByName('Continuous')
		acq_mode_cont = node_acq_mode_cont.GetValue()
		node_acq_mode.SetIntValue(acq_mode_cont)
		self._cam.PixelFormat.SetValue(PySpin.PixelFormat_RGB8)
		self._cam.BeginAcquisition()

        def saveImage(self, filename):
		# every 3rd image is saved
		image = self._cam.GetNextImage()
		image.Release()
		image = sel._cam.GetNextImage()
		image.Release()
		image = self._cam.GetNextImage()
		image.Save(filename)
		image.Release()
		
	def __deinit__(self):
		self._cam.EndAcquisition()
		self._cam.DeInit()
		del self._cam
		self._cam_list.Clear()
		self._system.ReleaseInstance()


#handles ctr-C for graceful exiting
def signalHandler(sig, frame):
	print('Exiting')
	pipeline.stop()
	camera.__deinit__()
	sys.exit(0)

if __name__ =='__main__':
	signal.signal(signal.SIGINT, signalHandler)
	pipeline = PointGrey_AppSrc()
	camera = Camera()
	pipeline.play()
	index = 1
	while True:
		filename = 'Acquisition-%d.jpg' % index
		camera.saveImage(filename)
		pipeline.push(filename)
		#image deleted immediately after
		os.remove(filename)
		index += 1
