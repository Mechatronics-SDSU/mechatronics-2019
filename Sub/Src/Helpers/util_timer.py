import datetime
import time

class Timer:
    '''
    Provides timing information such a net time and relative time.
    '''
    def __init__(self):
        '''
        Initialize timer variables

        Parameters:
            N/A

        Returns:
            N/A
        '''
        self.net_time = 0
        self.net_time_iteration = 0
        self.initial_time = time.time()
        self._restart_timer = False

    def get_cpu_time_in_seconds(self):
        '''
        Returns the cpu clock time in seconds

        Parameters:
            N/A

        Returns:
            cpu_time_in_seconds: The cpu clock time in
                        seconds.
        '''
        return time.time()

    def net_timer(self):
        '''
        Gives the net time since this Timer object was created or
        restarted (in seconds). It is based off the cpu clock time.

        Parameters:
            N/A

        Returns:
            The net time in seconds since this timer was either created or restarted.
        '''
        cpu_clock_in_seconds = time.time()

        self.net_time = cpu_clock_in_seconds - self.initial_time
        self.net_time_iteration += 1

        return self.net_time

    def restart_timer(self):
        '''
        Set the restart timer flag.

        Parameters:
            N/A
        Returns:
            N/A
        '''
        self.net_time_iteration = 0
        self.initial_time = time.time()
