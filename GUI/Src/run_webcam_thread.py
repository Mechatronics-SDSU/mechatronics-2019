#TEST SCRIPT FOR RUNNING WEBCAM THREAD

from webcam_thread import Webcam_Thread

def main():

    print("BEGIN")
    web_thread = Webcam_Thread()
    web_thread.start()

if __name__ == "__main__":
    main()


