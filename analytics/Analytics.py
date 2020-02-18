'''
Analytics on time series based on the paper
'Truth Will Out: Departure-Based Process-Level Detection of 
Stealthy Attacks on Control Systems' 
Link:(https://dl.acm.org/doi/10.1145/3243734.3243781)'

'''
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from scipy.linalg import hankel, eigh

class ObluAnalytics():
    def __init__(self, lag_vector_length=50):
        self.lag_vector_length = lag_vector_length

    def getThresholdScore(self, data_path='../sensor/GetData/steps.txt'):

        df = pd.read_csv(data_path, skiprows=1, header=None, usecols=[1,2])
        X_train_data = (df[1]+df[2])/2
        
        N = len(X_train_data)
        L = self.lag_vector_length
        print(L)
        X_train = hankel(X_train_data[:L],X_train_data[L-1:]) # Creating trajectory matrix
        eigenValues, eigenVectors = eigh(np.matmul(X_train, X_train.T))
        idx = eigenValues.argsort()[::-1]
        eigenValues = eigenValues[idx]
        eigenVectors = eigenVectors[:,idx]

        r = 1 # Statistical dimension decided as per scree plot
        U, Sigma, V = np.linalg.svd(X_train)
        V = V.T
        X_elem = np.array( [Sigma[i] * np.outer(U[:,i], V[:,i]) for i in range(0,r)] )
        X_train_extracted = X_elem.sum(axis=0)

        U = eigenVectors[:,:r] 
        UT = U.T
        pX = np.matmul(UT,X_train_extracted)
        centroid = np.mean(pX, axis=1)
        centroid = centroid[:,np.newaxis]

        # Calculating the departure threshold in signal subspace using centroid and UT

        Xt = hankel(X_train_data[:L],X_train_data[L-1:])
        pXt = np.matmul(UT,Xt)
        dt_matrix = centroid - pXt
        dt_scores = np.linalg.norm(dt_matrix, axis=0, ord=2)
        theta = np.max(dt_scores)
        return UT, centroid, theta

    def getScore(self, UT, centroid, x, y):
        x, y = np.array(x, dtype='float64'), np.array(y, dtype='float64')
        stream = [np.sum(z)/2 for z in list(zip(x,y))]
        stream = np.array(stream, dtype='float64')
        lag_vector = stream[:,np.newaxis]
        projected_lag_vector = np.matmul(UT, lag_vector)    
        dist = centroid - projected_lag_vector
        score = np.linalg.norm(dist, ord=2)
        print(score)
        return score    


         