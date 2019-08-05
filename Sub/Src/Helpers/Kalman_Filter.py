'''
Copyright 2019, David Pierce Walker-Howell, All rights reserved

Author: David Pierce Walker-Howell<piercedhowell@gmail.com>
Last Modified 08/05/2019

Description: The base Kalman Filter algorithm to implement probabilistic
                sensor fusion and data filtering.
'''
class Kalman_Filter():
    '''
    A class that contains the mathmatics for a kalman filter. The
    state transistions, measurment predictions and parameter covariances
    need to be set, then predictions can be made about the state of data.
    '''
    def __init__(self, A, B, R, C, Q):
        '''
        Initialize the parameter matrices for state transistions, measurement
        predictions, and parameter covariances.

        Parameters:
            A:
        '''
        self.A = A
        self.B = B
        self.R = R
        self.C = C
        self.Q = Q

    def predict(self, mu_prev, cov_prev, control, measurement):
        '''
        Perform the Kalman Filter provided the previous state estimation, previous
        covariance, current control input, and current measurement input.

        Parameters:
            mu_prev: For state transition matrix A (being nxn), the previous state
                        vector should be a numpy matrix of dimension nx1.
        '''
        mu_exp = np.dot(self.A, mu_prev) + np.dot(self.B, control)

        cov_exp = np.dot(np.dot(self.A, cov_prev), self.A.T) + self.R

        temp = np.linalg.inv(np.dot(np.dot(self.C, cov_exp), self.C.T) + self.Q)
        K = np.dot(np.dot(cov_exp, self.C.T), temp)

        mu = mu_exp + np.dot(K, measurement - np.dot(self.C, mu_exp))

        I = np.identity(K.shape[0])
        cov = np.dot((I - np.dot(K, self.C)), cov_exp)

        return mu, cov
