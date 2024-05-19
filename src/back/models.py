import pandas as pd
from scipy.integrate import cumtrapz
import numpy as np
from scipy.optimize import minimize


class Models:
    def __init__(self, data: pd.DataFrame, heating_rate: float):
        self.data = data
        self.heating_rate = heating_rate

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
        Delta_q = np.trapz(self.data['HRR (W/g)'] / beta, self.data['Temperature (K)'])
        self.data['Alpha'] = (1/beta) * cumtrapz(self.data['HRR (W/g)'], self.data['Temperature (K)'], initial=0) / Delta_q
        T = self.data['Temperature (K)'].values
        HRR = self.data['HRR (W/g)'].values

        initial_guess = [1, np.log(1e4), 1, 1, 0.3]
        bounds = [(0.01, 10), (np.log(1000), np.log(20000)), (0, 5), (0, 5), (-1, 1)]

        options = {
            'maxiter': 10000,
            'maxfun': 50000,
            'disp': False
        }

        result = minimize(self.loss_function, initial_guess, args=(T, HRR, Delta_q), bounds=bounds, method='TNC', options=options)

        A_fitted, logEa_fitted, n_fitted, m_fitted, alpha_zv_fitted = result.x
        Ea_fitted = np.exp(logEa_fitted)

        return A_fitted, Ea_fitted, n_fitted, m_fitted, alpha_zv_fitted


if __name__ == "__main__":
    from back import FileProcessor

    file = FileProcessor(path="./2023_02_15_02_PET_HR05.txt")

    header = file.get_header()
    data_frame = file.get_data_frame()
    models = Models(data_frame, file.get_heating_rate())
    print(models.processing())