#Copyright (c) 2024 Harry Wang and Timo Aranjo

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import cv2
import serial

# These variables were made globals to ensure they could quickly be edited.

scale_Factor = 1.1
neighbor_Count = 9

# Defines the center line of the video input
center_X = 320

# The required visible area in pixels before centering or shooting can occur
face_Pixel_Area_Threshold = 3600

# The max x pixel distance allowed from the center to consider a target centered
max_X_Center_Delta = 80

# These don't really equate exactly to any physical units
# We didn't have the time to calibrate exact units

# Default amount of movement to inch closer to a target
default_Move = 170 

# Default rotation used to center a target
default_Rotate = 40

# Default firing time in seconds
default_Fire = 3

# Default rotation used when there are no targets visible
scan_Rotate = 50

# Whenever the Arduino has finished executing a movement command, it send a
# single character (any character) as a receipt.
# This determines whether or not a receipt has been detected
def action_Completed(ser):
	if ser.inWaiting() > 0:
		ser.read(1)
		return True
	return False

# Command format for Arduino:
# <command><space><parameter><newline>

# <command> - A digit from 1 - 5 indicating which
# command to execute.
# 1 - Move forward
# 2 - Move backwards
# 3 - Rotate clockwise
# 4 - Rotate counterclockwise
# 5 - Fire Nerf Bullet

# <space> - a single ASCII space.

# <parameter> - Commands 1 - 4 don't use real units,
# so it is more guess and check than anything.
# Command 5 takes seconds as the parameter.

# <newline> - A single ASCII newline.

# Send a rotate command over serial connection (ser)
def rotate(degrees, ser):
	print("Rotate Degrees: " + str(degrees))
	if (degrees > 0):
		ser.write( (str(3) + " " + str(int(degrees)) + "\n").encode('utf-8') )
		# Sometimes the command won't be written unless flush is called
		ser.flush()
	if (degrees < 0):
		# Parameters are always positive so we negate the degrees
		ser.write( (str(4) + " " + str(int(-1 * degrees)) + "\n").encode('utf-8') )
		ser.flush()
# Send a move command over serial connection (ser)
def move(tiles, ser):
	print("Move Tiles: " + str(tiles))
	if (tiles > 0):
		ser.write( (str(1) + " " + str(int(tiles)) + "\n").encode('utf-8') )
		ser.flush()
	if (tiles < 0):	
		ser.write( (str(2) + " " + str(int(-1 * tiles)) + "\n").encode('utf-8') )
		ser.flush()

# Send a fire command over serial connection (ser)
def fire(seconds,ser):
	print("Fire Seconds: " + str(seconds))
	ser.write( (str(5) + " " + str(int(seconds)) + "\n").encode('utf-8') )
	ser.flush()

# Given a list of face tupples found in an image,
# find the biggest (usually closest) face. 
def get_Biggest_Face(faces):
	# We must initialize biggest_Face so we have a value to compare to
	biggest_Face = faces[0]
	for (x,y,w,h) in faces:
		# If the current face is bigger than the old biggest face
		# It becomes the new biggest face
		if (biggest_Face[2] * biggest_Face[3]) < w * h:
			biggest_Face = (x,y,w,h)

	return biggest_Face

# -1 if it suggests to turn left
# 1 if it suggest to turn right
# 0 if in range

# Determines if a target is in range or if left or right movements need to
# be made.
# Returns 0 if in range.
# Returns 1 if it is necessary to turn right
# Returns -1 if it is necessary to turn left
def x_Center_Delta_In_Range(face):
	# Calculates the x coordinate center of a face
	face_Center = (face[0] + (face[2]/2))
	# Determine the distance of the middle of the face from the center
	x_Center_Delta = face_Center - center_X
	# If less than the threshold, no turn neccesary
	if abs(x_Center_Delta) <= max_X_Center_Delta:
		return 0
	if x_Center_Delta < 0:
		return -1
	return 1


# Given a specific target, take the necessary action to either get
# closer to the target or shoot the target.
def take_Action(face,ser):
	# If face is close enough within range (big enough area),
	# then determine if target centering needs to be done
	if (face[2] * face[3] > face_Pixel_Area_Threshold):
		in_Range = x_Center_Delta_In_Range(face)
		# If no target centering needs to be done, fire
		if in_Range == 0:
			fire(default_Fire, ser)
		else:
			# Otherwise rotate to center target
			if in_Range == -1:
				rotate(-default_Rotate, ser)
			else:
				rotate(default_Rotate, ser)
	else:
		# If target isn't close enough, move closer
		move(default_Move, ser)

# This loop runs forever and controls all movement of the robot
def loop(cap, cascade, ser):
	pending_Action = False

	while True:
		if pending_Action == True:
			# If we get an Arduino command receipt, 
			# we stop skipping frames
			if action_Completed(ser):
				pending_Action = False
				continue
			# Discard frames while we are waiting for the Arduino to finish a command
			_, img = cap.read()
		else:
			# Retrieve a frame
			_, img = cap.read()
			# Convert it to grayscale because Haar needs grayscale frames
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			# Retrieve faces from the grayscale image using the face classifier
			faces = cascade.detectMultiScale(gray, scale_Factor, neighbor_Count)
			#If there are no faces, we rotate until we see some
			if len(faces) <= 0:
				rotate(scan_Rotate, ser)
				pending_Action = True
				continue

			# If there are more than one face, find
			# the biggest face
			biggest_Face = get_Biggest_Face(faces)
			print(biggest_Face)
			# Take the appropriate actions to go to the nearest face
			take_Action(biggest_Face, ser)
			# Since we have taken a movement action, we know there is a pending action
			pending_Action = True
	
def main():
	# Create a capture handle
	cap = cv2.VideoCapture(0)
	# Set the default frame size.
	# Our other variables are relative to these
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
	# Use OpenCVs pretrained Haar face classifier
	cascade = cv2.CascadeClassifier('/scripts/haarcascade_frontalface_default.xml')
	# Create a serial device handle to talk to the arduino with
	ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600)
	# When we create a serial connection with the Arduino, it
	# will be in bootloader mode for 2 seconds.
	# Wait until this time has elapsed because it will cause communication issues
	import time
	time.sleep(3)
	# Enter main loop
	loop(cap, cascade, ser)
main()
