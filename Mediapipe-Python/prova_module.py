import cv2
import numpy as np
import os
#from matplotlib import pyplot as plt
import time
import mediapipe as mp
import pathlib
import pickle


#############Keypoints using MP Holistic

mp_pose = mp.solutions.pose # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities

def mediapipe_detection(image, model):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
	image.flags.writeable = False                  # Image is no longer writeable
	results = model.process(image)                 # prende il frame e ti ritorna i punti presenti a seconda del modello passato
	image.flags.writeable = True                   # Image is now writeable 
	image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
	return image, results

def draw_styled_landmarks(image, results):
	# Draw pose connections
	mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2),
                             mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2)
                             )


#######################
'''
cap = cv2.VideoCapture(0)
# Set mediapipe model 
list = []
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as iter_pose:
	while cap.isOpened():

		# Read feed
		ret, frame = cap.read()

		# Make detections
		image, results = mediapipe_detection(frame, iter_pose)
		print(results)

		# Draw landmarks
		draw_styled_landmarks(image, results)

		# Show to screen
		cv2.imshow('OpenCV Feed', image)

		frame_pose=extract_keypoints(results)
		list.append(frame_pose)

		# Break gracefully
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break
	cap.release()
	cv2.destroyAllWindows()
#
with open('mat.pkl', 'wb') as outfile:
	pickle.dump(list, outfile, pickle.HIGHEST_PROTOCOL)


with open('mat.pkl', 'rb') as infile:
	result = pickle.load(infile)
print("result:")
print(result)
print("list:")
print(list)
if list==result:
	print("UGUALI")
'''
##########extract keypoint values

#pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(132)



#print(pose)
##############setup folders
'''
alzateLaterali0 = braccia piegate
alzateLaterali1 = braccia non in sincro
alzateLaterali2 = angolo spalle non arriva ai 90 gradi
alzateLaterali3 = giuste
'''

def folderCreation():
	# Path for exported data, numpy arrays
	DATA_PATH = os.path.join("data\\exercise\\alzateLaterali")

	# Actions that we try to detect
	actions = np.array(['alzateLaterali0', 'alzateLaterali1', 'alzateLaterali2' , 'alzateLaterali3'])

	# Thirty videos worth of data
	no_sequences = 30


	path=pathlib.Path(__file__).parent.resolve() #restituisce il path del progetto

	finalPath=os.path.join(path,DATA_PATH)
	print(finalPath)

	for action in actions:
		#da 1 a 30 compresi
		for sequence in range(1,no_sequences+1):
			try:
				os.makedirs(os.path.join(finalPath, action, str(sequence)))
			except:
				print("exeption")
				pass

#############5 collect keypoint values for train and test





# Actions that we try to detect
#actions = np.array(['alzateLaterali0', 'alzateLaterali1', 'alzateLaterali2' , 'alzateLaterali3'])



#print(label_map)



from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed
from tensorflow.keras.utils import to_categorical
import numpy as np

model = Sequential()

model.add(LSTM(32, return_sequences=True, input_shape=(None, 5)))
model.add(LSTM(8, return_sequences=True))
model.add(TimeDistributed(Dense(2, activation='sigmoid')))

print(model.summary(90))

model.compile(loss='categorical_crossentropy',optimizer='adam')

def train_generator():
	while True:
		sequence_length = np.random.randint(10, 100)
		x_train = np.random.random((1000, sequence_length, 5))
		# y_train will depend on past 5 timesteps of x
		y_train = x_train[:, :, 0]
		for i in range(1, 5):
			y_train[:, i:] += x_train[:, :-i, i]
		y_train = to_categorical(y_train > 2.5)
		print("x train"+ str(x_train.shape))
		print(x_train)
		print("y train "+ str(y_train.shape))
		print(y_train)
		yield x_train, y_train

model.fit_generator(train_generator(), steps_per_epoch=1, epochs=5, verbose=1)