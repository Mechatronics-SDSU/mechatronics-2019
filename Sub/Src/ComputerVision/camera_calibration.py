import cv2
import numpy as np
import glob

def chess_board():

    #prepare 3d object points
    object_points = np.zeros((6*9, 3), np.float32)
    object_points[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1, 2)

    #list of 3d object points, 2d image points
    three_dim_points = []
    two_dim_points = []

    list_pics = glob.glob('chessboard_cal_pics/*.jpg')

    for index, pic in enumerate(list_pics):
        picture = cv2.imread(pic)
        gray_pic = cv2.cvtColor(picture, cv2.COLOR_BGR2GRAY)
        shape = gray_pic.shape[::-1]

        ret, board_corners = cv2.findChessboardCorners(gray_pic, (9, 6), None)

        if ret == True:

            three_dim_points.append(object_points)
            two_dim_points.append(board_corners)

            cv2.drawChessboardCorners(picture, (9, 6), board_corners, ret)
            cv2.imshow('picture', picture)
            cv2.waitKey(50)

    cv2.destroyAllWindows()
    return three_dim_points, two_dim_points, shape

if __name__ == '__main__':

    three_dim_points, two_dim_points, shape = chess_board()
    print(shape)
    ret, camera_matrix, distortion_matrix, rvecs, tvecs  = cv2.calibrateCamera(three_dim_points, two_dim_points, shape, None, None)
    print(camera_matrix)
    print(distortion_matrix)
    print(rvecs)
    print(tvecs)
