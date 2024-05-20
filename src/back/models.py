import pandas as pd
from scipy.integrate import cumtrapz
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

class Models:
    def __init__(self, data: pd.DataFrame, heating_rate: float):
        self.data = data
        self.heating_rate = heating_rate
        self.coefs = None
        self.Delta_q = 0
    def reaction_rate_model(self, params, T, HRR, Delta_q):
        A, logEa, n, m, alpha_zv = params
        Ea = np.exp(logEa)
        beta = self.heating_rate
        R = 8.314
        alpha = (1/beta) * cumtrapz(HRR, T, initial=0) / Delta_q
        alpha = np.clip(alpha, 0, 1)
        rate = Delta_q * A * ((1 - alpha)**n) * (alpha**m + alpha_zv) * np.exp(-Ea / (R * T))
        return rate
    
    def loss_function(self, params, T, HRR, Delta_q):
        model_predictions = self.reaction_rate_model(params, T, HRR, Delta_q)
        residuals = model_predictions - HRR
        return np.sum(residuals**2)
    
    def processing(self):
        beta = self.heating_rate
        
        self.data['Temperature (K)'] = self.data['Temperature (C)'] + 273.15
        self.Delta_q = np.trapz(self.data['HRR (W/g)'] / beta, self.data['Temperature (K)'])
        self.data['Alpha'] = (1/beta) * cumtrapz(self.data['HRR (W/g)'], self.data['Temperature (K)'], initial=0) / self.Delta_q
        T = self.data['Temperature (K)'].values
        HRR = self.data['HRR (W/g)'].values

        initial_guess = [1e11, np.log(1e4), 1, 1, 0.3]
        bounds = [(1e10, 1e12), (np.log(4*1e3), np.log(4*1e5)), (0, 5), (0, 5), (-1, 1)]

        options = {
            'maxiter': 10000,
            'maxfun': 50000,
            'disp': False
        }

        result = minimize(self.loss_function, initial_guess, args=(T, HRR, self.Delta_q), bounds=bounds, method='TNC', options=options)

        A_fitted, logEa_fitted, n_fitted, m_fitted, alpha_zv_fitted = result.x
        Ea_fitted = np.exp(logEa_fitted)

        self.coefs = [A_fitted, logEa_fitted, n_fitted, m_fitted, alpha_zv_fitted]
        
        return A_fitted, Ea_fitted, n_fitted, m_fitted, alpha_zv_fitted
    
    def draw(self):
        T = self.data['Temperature (K)'].values
        HRR = self.data['HRR (W/g)'].values
        
        predicted_HRR = self.reaction_rate_model(self.coefs, T, HRR,  self.Delta_q)
        # r2 = r2_score(HRR, predicted_HRR)

        plt.figure(figsize=(12, 6))
        plt.scatter(self.data['Temperature (C)'], self.data['HRR (W/g)'], color='blue', label='Actual data')
        plt.plot(self.data['Temperature (C)'], predicted_HRR, color='red', label='Fitted model')
        # plt.text(x=min(experiment_data['Temperature (C)']), y=200, s=f"R2 (чем ближе к 1, тем лучше): {r2:.4f}", fontsize=12)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('HRR (W/g)')
        plt.title('Fit of Reaction Rate Model to Experimental Data')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    from back import FileProcessor

    file = FileProcessor(path="./2023_02_15_02_PET_HR05.txt")

    header = file.get_header()
    data_frame = file.get_data_frame()
    models = Models(data_frame, file.get_heating_rate())
    print(models.processing())