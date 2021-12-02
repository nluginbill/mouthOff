#USAGE: python facial_68_Landmark.py

import dlib,cv2
import numpy as np
from facePoints import facePoints

def writeFaceLandmarksToLocalFile(faceLandmarks, fileName):
  with open(fileName, 'w') as f:
    for p in faceLandmarks.parts():
      f.write("%s %s\n" %(int(p.x),int(p.y)))

  f.close()

# location of the model (path of the model).
Model_PATH = "shape_predictor_68_face_landmarks.dat"


# now from the dlib we are extracting the method get_frontal_face_detector()
# and assign that object result to frontalFaceDetector to detect face from the image with 
# the help of the 68_face_landmarks.dat model
frontalFaceDetector = dlib.get_frontal_face_detector()


# Now the dlip shape_predictor class will take model and with the help of that, it will show 
faceLandmarkDetector = dlib.shape_predictor(Model_PATH)

# We now reading image on which we applied our face detector
image = "test.jpg"

# Now we are reading image using openCV
img= cv2.imread(image)
imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# landmarks of the face image  will be stored in output/image_k.txt
faceLandmarksOuput= "output/image"

# Now this line will try to detect all faces in an image either 1 or 2 or more faces
allFaces = frontalFaceDetector(imageRGB, 0)


print("List of all faces detected: ",len(allFaces))

# List to store landmarks of all detected faces
allFacesLandmark = []

# Below loop we will use to detect all faces one by one and apply landmarks on them

for k in range(0, len(allFaces)):
  # dlib rectangle class will detecting face so that landmark can apply inside of that area
  faceRectangleDlib = dlib.rectangle(int(allFaces[k].left()),int(allFaces[k].top()),
      int(allFaces[k].right()),int(allFaces[k].bottom()))

  # Now we are running loop on every detected face and putting landmark on that with the help of faceLandmarkDetector
  detectedLandmarks = faceLandmarkDetector(imageRGB, faceRectangleDlib)
  
  # count number of landmarks we actually detected on image
  if k==0:
    print("Total number of face landmarks detected ",len(detectedLandmarks.parts()))

  # Svaing the landmark one by one to the output folder
  allFacesLandmark.append(detectedLandmarks)

  # Now finally we drawing landmarks on face
  facePoints(img, detectedLandmarks)

  fileName = faceLandmarksOuput +"_"+ str(k)+ ".txt"
  print("Lanmdark is save into ", fileName)

  # Write landmarks to disk
  writeFaceLandmarksToLocalFile(detectedLandmarks, fileName)

#Name of the output file
outputNameofImage = "output/image.jpg"
print("Saving output image to", outputNameofImage)
cv2.imwrite(outputNameofImage, img)

cv2.imshow("Face landmark result", img)

# Pause screen to wait key from user to see result
cv2.waitKey(0)
cv2.destroyAllWindows()
