import cv2
import numpy as np
import time

cam_matrix = np.array([[656.76117331, 0.0, 311.02000055], [0.0, 656.5199208, 235.31118765], [0.0, 0.0, 1.0]])
print(cam_matrix)
dist_matrix = np.array([[0.07935776, -0.0490818, -0.0281497, -0.00267198, -1.08707165]])

object_points = np.zeros((6*9, 3), np.float32)
object_points[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1, 2)

#three_dim_points = []
#two_dim_points = []
capture = cv2.VideoCapture(1)

while(True):

    ret, frame = capture.read()
    #time.sleep()
    #print(ret)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret2, board_corners = cv2.findChessboardCorners(gray_frame, (9, 6), None)
    #print(ret2)
    if ret2:
        #print(board_corners)
        #three_dim_points.append(object_points)
        #two_dim_points.append(board_corners)
        #print(three_dim_points.shape)
        #print(two_dim_points.shape)
        #print(object_points.shape)
        #print(object_points)
        #print(board_corners.shape)
        #print(board_corners)
        #print(three_dim_points)
        image_points = board_corners.reshape((board_corners.shape[0], -1), order = 'F')
        #print(image_points)
        #print('3-D coordinates: ', object_points)
        #print('2-D coordinates: ', image_points)
        #print(image_points.shape)

        working, rvec, tvec = cv2.solvePnP(object_points,
                               image_points,
                               cam_matrix,
                               dist_matrix)

        #print('Rotation vector: ', rvec)
        print('Translation vector: ', tvec)
        #rmat = cv2.Rodrigues(rvec)
        #print('Rotation matrix: ', rmat[0])
        #print(rmat[0].shape)
        #print(tvec.shape)
        #print('Rotation matrix: ', rmat[0])

        #predicted_points = cv2.projectPoints(object_points, rvec, tvec, cam_matrix, dist_matrix)
        #print('Projected image points: ', predicted_points[0])
        #print('Actual image points: ', image_points)
        #movement_matrix = np.concatenate((rmat[0], tvec), axis = 1)
        #print('Rt matrix: ', movement_matrix)
        #ones_vector = np.ones((54, 1))
        #print(ones_vector)
        #three_dim_points = np.concatenate((object_points, ones_vector), axis = 1)
        #two_dim_points = np.concatenate((image_points, ones_vector), axis = 1)
        #print(image_points)
        #print(two_dim_points)
        #print(three_dim_points.shape)
        #print(two_dim_points.shape)
        #product_A = np.dot(cam_matrix, movement_matrix)
        #print('Step A: ', product_A)
        #print(product_A)
        #print('Transpose: ', three_dim_points.transpose())
        #print('Transpose shape: ', three_dim_points.transpose().shape)
        #product_B = np.dot(product_A, three_dim_points.transpose())
        #print(two_dim_points)
        #print(product_B)
        #predicted_points = cv2.projectPoints(t)
        #print(two_dim_points.shape)
        #print(product_B.shape)
        #print('Acutal coordinates: ', two_dim_points[0])
        #print('Projected coordinates: ', product_B.transpose()[0])
        #print(product_B)
        #difference = np.subtract(two_dim_points, np.abs(product_B.transpose()))
        #print('Errors: ', difference)
        #im_coordinates = rmat.dot(object_points)
        #three_dim_points.append(object_points)
        #two_dim_points.append(board_corners)

        cv2.drawChessboardCorners(frame, (9, 6), board_corners, ret2)
#        cv2.imshow('picture', picture)
#        cv2.waitKey(1)

#        cv2.drawChessboardCorners(frame, (9, 6), board_corners, ret)

    cv2.imshow('frame', frame)
    '''
    #print(board_corners)

    if ret2 == True:
        three_dim_points.append(object_points)
        two_dim_points.append(board_corners)
        rvec, tvec = cv2.solvePnP(three_dim_points, two_dim_points, cam_matrix, dist_matrix)
        #print(rvec)
        #print(tvec)

        cv2.drawChessboardCorners(frame, (9, 6), board_corners, ret)
        cv2.imshow('picture', frame)
        '''
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
