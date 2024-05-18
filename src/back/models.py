import pandas as pd


class Models:
    def __init__(self, data: pd.DataFrame, heating_rate: float):
        self.data = data
        self.heating_rate = heating_rate

    def processing(self):
        return 10
