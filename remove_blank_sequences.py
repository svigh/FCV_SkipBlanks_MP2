import numpy as np
import cv2
import os
import tkinter.filedialog
import argparse

DEBUG_STUFF = False

VIDEO_CAPTURE_GET_WIDTH = 3
VIDEO_CAPTURE_GET_HEIGHT = 4
VIDEO_CAPTURE_GET_CHANNELS = 3

THRESHOLD = 8457252

# https://stackoverflow.com/questions/189943/how-can-i-quantify-difference-between-two-images
# transform to grey -> normalize ->

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--input_video", dest="input_video_path", action="store",
		help="The input video that needs frames to be cut from it")
	parser.add_argument("--debug", dest="debug", action="store_true",
		help="Show video window and remove frames during the video")

	args = parser.parse_args()

	if args.debug:
		global DEBUG_STUFF
		DEBUG_STUFF = True

	return args

# Skips over frames that are too similar to the previous frame
# returns the number of skipped frames and total read frames
def remove_similar_frames(video_path, threshold=THRESHOLD):
	video_basename = os.path.basename(video_path).split(".")[0]	# Only get the name of the file

	# TODO: get the cv2 constants for these so that i dont define them
	capture = cv2.VideoCapture(video_path)
	frame_width = int(capture.get(VIDEO_CAPTURE_GET_WIDTH))
	frame_height = int(capture.get(VIDEO_CAPTURE_GET_HEIGHT))
	channels = VIDEO_CAPTURE_GET_CHANNELS
	fps = capture.get(cv2.CAP_PROP_FPS)

	# Define the fps to be equal to 10. Also frame size is passed.
	output = cv2.VideoWriter(video_basename + "_out" + ".avi", cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))
	frame_count = 0
	skipped_frames = 0

	previous_frame = np.zeros((frame_height, frame_width, channels))

	if not capture.isOpened():
		print("Cant capture video %s" % (video_path))
		return 1

	while capture.isOpened():
		ret, current_frame = capture.read()

		if ret == True:
			frame_count += 1
			skip_frame = False

			# Apply blur to act as a noise removing filter
			blurred_frame = cv2.GaussianBlur(current_frame, (5, 5), 0)

			# Define the similarity between frames as the bigness of their difference
			difference = abs(blurred_frame - previous_frame)
			difference_array_sum = np.sum(difference)

			if DEBUG_STUFF:
				print(difference_array_sum)

			# If two frames are too similar skip the current one
			if difference_array_sum < threshold:
				skipped_frames += 1
				if DEBUG_STUFF:
					print("Skipped frame %d.\n" % (frame_count) + "%d vs %d".center(10) % (difference_array_sum, threshold))
				previous_frame = blurred_frame

				if DEBUG_STUFF:
					text = "X"
					font = cv2.FONT_HERSHEY_SIMPLEX
					offset = 100
					cv2.putText(img=current_frame, text=text,org=(frame_height//2 - offset, frame_width//2 + offset), fontFace=font, fontScale=20, color=(0, 0, 255), thickness=15, lineType=cv2.LINE_AA)
					cv2.imshow("frame", current_frame)
					skip_frame = True

			if DEBUG_STUFF:
				cv2.imshow("frame", current_frame)

			if not skip_frame:
				output.write(current_frame)

			previous_frame = blurred_frame

			# Press Q on keyboard to exit
			if cv2.waitKey(25) & 0xFF == ord('q'):
				return skipped_frames, frame_count
		else:
			return skipped_frames, frame_count

	capture.release()
	output.release()

	return skipped_frames, frame_count


def main():
	args = parse_args()
	if args.input_video_path is not None:
		skipped_frames, frame_count = remove_similar_frames(args.input_video_path)
	else:
		input_video_path = tkinter.filedialog.askopenfilename(title="INPUT VIDEO")
		skipped_frames, frame_count = remove_similar_frames(input_video_path)

	print("Skipped frames: %d\nWritten frames: %d" % (skipped_frames, frame_count - skipped_frames))

	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()

