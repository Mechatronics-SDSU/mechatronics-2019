import cv2
import numpy as np

cam_matrix = np.array([[656.76117331, 0.0, 311.02000055], [0.0, 656.5199208, 235.31118765], [0.0, 0.0, 1.0]])
dist_matrix = np.array([[0.07935776, -0.0490818, -0.0281497, -0.00267198, -1.08707165]])

object_points = np.zeros((6*9, 3), np.float32)
object_points[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1, 2)

three_dim_points = []
two_dim_points = []
capture = cv2.VideoCapture(1)

while (True):

    ret, frame = capture.read()
    print(ret)
    #print(frame)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret2, board_corners = cv2.findChessboardCorners(gray_frame, (9, 6), None)

    if ret2 == True:
        three_dim_points.append(object_points)
        two_dim_points.append(board_corners)
        rvec, tvec = cv2.solvePnP(three_dim_points, two_dim_points, cam_matrix, dist_matrix)
        print(rvec)
        print(tvec)

        cv2.drawChessboardCorners(frame, (9, 6), board_corners, ret)
        cv2.imshow('picture', frame)
        cv2.waitKey(1)
        #three_dim_points.clear()
        #two_dim_points.clear()

    #height, width = frame.shape[:2]
    #new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_matrix, (width, height), 1, (width, height))
    #print(roi)

    #dst = cv2.undistort(frame, camera_matrix, distortion_matrix, None, new_camera_matrix)
    #x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]
    #cv2.imshow('frame', frame)
    #cv2.imshow('frame', dst)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
capture.destroyAllWindows()
