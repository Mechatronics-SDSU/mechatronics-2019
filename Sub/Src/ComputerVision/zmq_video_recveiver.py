import cv2
import imagezmq
import time
import threading
import os

image_hub = imagezmq.ImageHub("tcp://*:6969")

def save_image(image, name, dir, type="jpg"):
    '''
    Save the images to a directory with the given file type.

    Parameters:
        image: The Image you want to save.
        name: The name of the image.
        dir: The directory to which the images should be saved.
        type: The file type the images should be saved as. Default 'jpg'

    Returns:
        N/A
    '''
    image_save_path = os.path.join(dir,"%s.%s" % (name, type))
    cv2.imwrite(image_save_path, image)

if __name__ == "__main__":
    #How many frames to save.
    save_dir = '/home/piercedhowell/mechatronics-2019/training_images'
    save_images = True
    max_num_images = 100
    frame_save_interval = 40
    frame_count = 0
    image_count = 0

    while(True):
        frame_count += 1
        msg, image = image_hub.recv_image()

        if(save_images and (frame_count == frame_save_interval) and (image_count < max_num_images)):
            save_image(image, str(image_count), save_dir, type="jpg")
            image_count += 1
            frame_count = 1
        cv2.imshow(msg, image)
        cv2.waitKey(1)

        #Must send this reply!
        image_hub.send_reply(b'OK')
