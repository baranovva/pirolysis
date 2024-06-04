import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.integrate import cumtrapz
from scipy.optimize import least_squares, differential_evolution, minimize


class Models:
    """
    A class to model and fit reaction rate data from thermal analysis experiments.

    Attributes:
    -----------
    data : pandas.DataFrame
        Experimental data containing 'Temperature (C)' and 'HRR (W/g)' columns.
    heating_rate : float
        Heating rate in С/s.
    optimized_parameters : list or None
        List of optimized model parameters after fitting.
    Delta_q : float
        The total heat released per gram during the experiment.

    Methods:
    --------
    __init__(data: pandas.DataFrame, heating_rate: float)
        Initializes the Models class with experimental data and heating rate.

    reaction_rate_model(params: list, T: np.array, HRR: np.array, Delta_q: float) -> np.array
        Computes the predicted heat release rate based on the reaction rate model.

    loss_function(params: list, T: np.array, HRR: np.array, Delta_q: float) -> float
        Calculates the loss (sum of squared residuals) between the model predictions and the experimental data.

    residuals(params: list, T: np.array, HRR: np.array, Delta_q: float) -> np.array
        Computes the residuals between the model predictions and the experimental HRR data.

    process(method: str, bounds: dict, initial_guess: list) -> list
        Processes the experimental data, optimizes the model parameters, and fits the model to the data.

    draw() -> matplotlib.figure.Figure
        Plots the experimental data and the fitted model predictions.
    """

    def __init__(self, data: pd.DataFrame, heating_rate: float):
        """
        Initializes the Models class with experimental data and heating rate.

        Parameters:
        -----------
        data : pd.DataFrame
            Experimental data containing 'Temperature (C)' and 'HRR (W/g)' columns.
        heating_rate : float
            Heating rate in К/min.
        """
        self.data = data
        self.heating_rate = heating_rate
        self.optimized_parameters = None
        self.Delta_q = 0

    def reaction_rate_model(self, params: list, T: np.array, HRR: np.array, Delta_q: float) -> np.array:
        """
        Computes the predicted heat release rate based on the reaction rate model.

        Parameters:
        -----------
        params : list
            List of model parameters [A, logEa, n, m, alpha_zv].
        T : np.array
            Array of temperature values (in Kelvin).
        HRR : np.array
            Array of experimental HRR values (in W/g).
        Delta_q : float
            The total heat released per gram during the experiment.

        Returns:
        --------
        np.array
            The predicted heat release rate.
        """
        A, logEa, n, m, alpha_zv = params
        Ea = np.exp(logEa)
        beta = self.heating_rate
        R = 8.314
        alpha = (1 / beta) * cumtrapz(HRR, T, initial=0) / Delta_q
        alpha = np.clip(alpha, 0, 1)
        rate = Delta_q * A * ((1 - alpha) ** n) * (alpha ** m + alpha_zv) * np.exp(-Ea / (R * T))
        return rate

    def loss_function(self, params: list, T: np.array, HRR: np.array, Delta_q: float) -> float:
        """
        Calculates the loss (sum of squared residuals) between the model predictions and the experimental data.

        Parameters:
        -----------
        params : list
            List of model parameters [A, logEa, n, m, alpha_zv].
        T : np.array
            Array of temperature values (in Kelvin).
        HRR : np.array
            Array of experimental HRR values (in W/g).
        Delta_q : float
            The total heat released per gram during the experiment.

        Returns:
        --------
        float
            The loss value.
        """
        model_predictions = self.reaction_rate_model(params, T, HRR, Delta_q)
        residuals = model_predictions - HRR
        return np.sum(residuals ** 2)

    def residuals(self, params: list, T: np.array, HRR: np.array, Delta_q: float) -> float:
        """
        Computes the residuals between the model predictions and the experimental HRR data.

        Parameters:
        -----------
        params : list
            List of model parameters [A, logEa, n, m, alpha_zv].
        T : np.array
            Array of temperature values (in Kelvin).
        HRR : np.array
            Array of experimental HRR values (in W/g).
        Delta_q : float
            The total heat released per gram during the experiment.

        Returns:
        --------
        np.array
            Array of residuals (model predictions - experimental HRR).
        """
        model_predictions = self.reaction_rate_model(params, T, HRR, Delta_q)
        return model_predictions - HRR

    def processing(self, method: str, bounds: dict, initial_guess: list) -> list:
        """
        Processes the experimental data, optimizes the model parameters, and fits the model to the data.

        Parameters:
        -----------
        method : str
            The string for optimization method to choose. Options are "minimize", "least squares", and "differential evolution".
        bounds : dict
            Dictionary containing the bounds for each parameter in the form {'param': (min, max)}.
        initial_guess : list
            Initial guess for the model parameters.

        Returns:
        --------
        list
            Optimized parameters [A, Ea, n, m, alpha_zv].
        """
        beta = self.heating_rate

        self.data['Temperature (K)'] = self.data['Temperature (C)'] + 273.15
        self.Delta_q = np.trapz(self.data['HRR (W/g)'] / beta, self.data['Temperature (K)'])
        self.data['Alpha'] = (1 / beta) * cumtrapz(self.data['HRR (W/g)'], self.data['Temperature (K)'], initial=0
                                                   ) / self.Delta_q
        T = self.data['Temperature (K)'].values
        HRR = self.data['HRR (W/g)'].values

        if method == "minimize":
            bounds_list = [bounds['A'], bounds['logEa'], bounds['n'], bounds['m'], bounds['alpha_zv']]

            options = {
                'maxiter': 10000,
                'maxfun': 50000,
                'disp': False
            }
            result = minimize(self.loss_function, initial_guess, args=(T, HRR, self.Delta_q), bounds=bounds_list,
                              method='TNC',
                              options=options
                              )
        elif method == "least squares":
            lower_bounds = [bounds['A'][0], bounds['logEa'][0], bounds['n'][0], bounds['m'][0], bounds['alpha_zv'][0]]
            upper_bounds = [bounds['A'][1], bounds['logEa'][1], bounds['n'][1], bounds['m'][1], bounds['alpha_zv'][1]]
            bounds_ls = (lower_bounds, upper_bounds)

            result = least_squares(self.residuals, initial_guess, args=(T, HRR, self.Delta_q), bounds=bounds_ls)
        elif method == "differential evolution":
            bounds_list = [bounds['A'], bounds['logEa'], bounds['n'], bounds['m'], bounds['alpha_zv']]

            result = differential_evolution(self.loss_function, bounds_list, args=(T, HRR, self.Delta_q))
        else:
            raise ValueError("Invalid optimization method selected.")
        A_fitted, logEa_fitted, n_fitted, m_fitted, alpha_zv_fitted = result.x
        Ea_fitted = np.exp(logEa_fitted)

        self.optimized_parameters = [A_fitted, logEa_fitted, n_fitted, m_fitted, alpha_zv_fitted]

        return [A_fitted, Ea_fitted, n_fitted, m_fitted, alpha_zv_fitted]

    def draw(self) -> matplotlib.figure.Figure:
        """
        Plots the experimental data and the fitted model predictions.

        Returns:
        --------
        matplotlib.figure.Figure
            Matplotlib figure object.
        """
        T = self.data['Temperature (K)'].values
        HRR = self.data['HRR (W/g)'].values
        predicted_HRR = self.reaction_rate_model(self.optimized_parameters, T, HRR, self.Delta_q)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(self.data['Temperature (C)'], self.data['HRR (W/g)'], color='blue', label='Actual data')
        ax.plot(self.data['Temperature (C)'], predicted_HRR, color='red', label='Fitted model')
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('HRR (W/g)')
        ax.legend()
        ax.grid(True)

        return fig


if __name__ == "__main__":
    from back import FileProcessor

    file = FileProcessor(path="./2023_02_15_02_PET_HR05.txt")

    header = file.get_header()
    data_frame = file.get_data_frame()
    models = Models(data_frame, file.get_heating_rate())
    print(models.processing())
