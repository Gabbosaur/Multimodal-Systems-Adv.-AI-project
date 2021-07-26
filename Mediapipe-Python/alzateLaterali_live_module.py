
import cv2
import mediapipe as mp
import numpy as np
import math

#nostri moduli
import math_module

"""
# VIDEO FEED
cap = cv2.VideoCapture(0)
while cap.isOpened():
	ret, frame = cap.read()
	cv2.imshow('Mediapipe Feed', frame)
	if cv2.waitKey(10) & 0xFF == ord('q'):	#0xFF è la variabile che fa lo store del tasto premuto, in questo caso quando premiamo q viene chiuso il feed video
		break

cap.release()
cv2.destroyAllWindows()
"""
def __extract_keypoints(results):
	pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
	return pose

def alzateLaterali_live(model,num_rep):

	mp_drawing = mp.solutions.drawing_utils  # drawing utilities
	mp_pose = mp.solutions.pose  # pose estimation model di mediapipe

	rep_counter=0
	flag_discesa=0
	flag_salita=0
	flag_fine_es=0
	flag_es_valido=0
	record_movimento=[]

	cap = cv2.VideoCapture(0)

	## Setup mediapipe instance
	with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
		while cap.isOpened():
			ret, frame = cap.read()

			# Recolor image to RGB
			image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			image.flags.writeable = False

			# Make detection
			results = pose.process(image)

			# Recolor back to BGR
			image.flags.writeable = True
			image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

			# Extract landmarks
			try:
				landmarks = results.pose_landmarks.landmark

				cv2.putText(image,"BODY FOUND",
							(400,15),
							cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA
				)
				# print(landmarks)

				"""
				ciclo ogni landmarks
				for lndmrk in mp_pose.PoseLandmark:
					print(lndmrk)

				accesso ai lendmark
				landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x oppure .y  .z  .visibility
				"""

				# get coordinates
				shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
				elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
				wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
				hip_left = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

				shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
				elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
				wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
				hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

				# calculate angles
				angle_elbow_left = math_module.calculate_angle(shoulder_left, elbow_left, wrist_left)
				angle_elbow_right = math_module.calculate_angle(shoulder_right, elbow_right, wrist_right)
				angle_shoulder_left = math_module.calculate_angle(hip_left, shoulder_left, elbow_left)
				angle_shoulder_right = math_module.calculate_angle(hip_right, shoulder_right, elbow_right)

				# Visualize angle
				cv2.putText(image,str(math.trunc(angle_elbow_left)) + "deg",
					tuple(np.multiply(elbow_left, [640, 480]).astype(int)),
					cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA
				)

				cv2.putText(image,str(math.trunc(angle_elbow_right)) + "deg",
					tuple(np.multiply(elbow_right, [640, 480]).astype(int)),
					cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA
				)

				cv2.putText(image,str(math.trunc(angle_shoulder_left)) + "deg",
							tuple(np.multiply(shoulder_left, [640, 480]).astype(int)),
							cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA
				)

				cv2.putText(image,str(math.trunc(angle_shoulder_right)) + "deg",
					tuple(np.multiply(shoulder_right, [640, 480]).astype(int)),
					cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA
				)

				#controlli per gli stati della tpose
				#################################################da main chiamamo questa funz, gli passiamo medel, e il numero di ripetizioni
				tollerance = 20

				if (angle_shoulder_left < 20 and angle_shoulder_right < 20 and angle_elbow_left >= (180 - tollerance) and angle_elbow_left <= (180 + tollerance) and angle_elbow_right >= (180 - tollerance) and angle_elbow_right <= (180 + tollerance)):
					flag_salita=1
					cv2.putText(image,"posizione di partenza riconosciuta",(60,90),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA)
				else:
					if (angle_shoulder_left >= 30 or angle_shoulder_right >= 30):
						flag_es_valido=1
						cv2.putText(image,"soglia validità es superata",
								(60,60),
								cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 255),2,cv2.LINE_AA
						)
						if (flag_discesa == 0):
							flag_salita=0
							flag_discesa = 1
					else:
						if (angle_shoulder_left < 20 and angle_shoulder_right < 20 and flag_es_valido==1):
							flag_discesa = 0
							rep_counter = rep_counter+1
							flag_fine_es = 1
				if(flag_salita==1 or flag_discesa==1):
					frame_pose=__extract_keypoints(results)
					record_movimento.append(frame_pose)
				else:
					if(flag_fine_es == 1):
						#calcolo feature
						#model.predict(feature)
						#tolgo return

						if(rep_counter==num_rep):
							#testo:es completato
							#aspetta 2 secondi
							cap.release()
							cv2.destroyAllWindows()
							#passi le classificazioni a main con un return
						#return record_movimento
			except:
				pass

			#status box
			cv2.rectangle(image, (0,0), (225,80), (245,117,16), -1)

			# Reps data
			cv2.putText(image, 'REPS',
						(15,15),
						cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
			cv2.putText(image, str(rep_counter),
						(10,63),
						cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

			# Render detections
			mp_drawing.draw_landmarks(image,results.pose_landmarks,mp_pose.POSE_CONNECTIONS,
				mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
				mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
			)  # color=(b,g,r)

			cv2.imshow("Mediapipe Feed", image)

			if cv2.waitKey(10) & 0xFF == ord("q"):
				break

		cap.release()
		cv2.destroyAllWindows()