class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(f'videos/{filename}', 'rb')
		except:
			raise IOError
		self.frameNum = 0

	def get_filename(self):
		return self.filename

	def resetVideo(self):
		self.file.close()
		self.file = open(f'videos/{self.filename}', 'rb')
		
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Get the framelength from the first 5 bits
		if data: 
			framelength = int(data)
							
			# Read the current frame
			data = self.file.read(framelength)
			self.frameNum += 1
		else:
			self.resetVideo()

			return self.nextFrame()
		return framelength, data
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	
	