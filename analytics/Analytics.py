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
    def __init__(self):
        pass

    def getThresholdScore(self, data_path='../sensor/GetData/steps.txt'):

        self.df = pd.read_csv(data_path, skiprows=1, header=None, usecols=[1,2])
        self.pca = PCA(n_components = 1)
        self.df =  self.pca.fit_transform(self.df)
        
        N = len(self.df)
        L = 200
        self.X_train = hankel(self.df[:L],self.df[L-1:]) # Creating trajectory matrix
        eigenValues, eigenVectors = eigh(np.matmul(self.X_train, self.X_train.T))
        self.idx = eigenValues.argsort()[::-1]
        eigenValues = eigenValues[self.idx]
        eigenVectors = eigenVectors[:,self.idx]

        r = 1
        # Extracted Training signals
        U, Sigma, V = np.linalg.svd(self.X_train)
        V = V.T
        # d = np.linalg.matrix_rank(self.X_train)
        X_elem = np.array( [Sigma[i] * np.outer(U[:,i], V[:,i]) for i in range(0,r)] )
        X_train_extracted = X_elem.sum(axis=0)
        # X_train_extracted_data = np.asarray(list(X_train_extracted[:,0]) + list(X_train_extracted[:,-1]))

        U = eigenVectors[:,:r] # r as statistical dimension
        UT = U.T
        pX = np.matmul(UT,X_train_extracted)
        centroid = np.mean(pX, axis=1)
        centroid = centroid[:,np.newaxis]

        # Calculating the departure threshold in signal subspace using centroid and UT

        #For training phase
        # Xtrg = hankel(self.df[:L], self.df[L-1:])
        # pXtrg = np.matmul(UT,Xtrg)
        # dtrg_matrix = centroid - pXtrg
        # dtrg_scores = np.linalg.norm(dtrg_matrix, axis=0, ord=2)

        # For Validation phase and threshold calculation
        Xt = hankel(self.df[:L],self.df[L-1:])
        print(Xt.shape)

        pXt = np.matmul(UT,Xt)
        print(pXt.shape)
        dt_matrix = centroid - pXt
        dt_scores = np.linalg.norm(dt_matrix, axis=0, ord=2)
        # d_scores = np.asarray([np.matmul(d_matrix[:,i].T, d_matrix[:,i]) for i in range(d_matrix.shape[1])])
        dt_theta = np.max(dt_scores)
        print(dt_scores)
        return UT, centroid, dt_theta

    def getScore(self, UT, centroid, threshold, df):
        # print(df.shape)
        self.pca = PCA(n_components = 1)
        lag_vector =  self.pca.fit_transform(df)
        projected_lag_vector = np.matmul(UT, lag_vector)    
        dist = centroid - projected_lag_vector
        score = np.linalg.norm(dist, ord=2)
        return score    


         