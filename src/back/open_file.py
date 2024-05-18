import pandas as pd


class FileProcessor:
    def __init__(self, path: str = ""):
        self.file_path = path
        self.header = []
        self.data_frame = None
        self.heating_rate = None

    def open_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.header = []

            for _ in range(11):
                line = file.readline().strip()
                if line.startswith("#"):
                    line = line[1:]
                    self.header.append(line)
                    if line.startswith("Heating Rate"):
                        _, value = line.split(":")
                        self.heating_rate = float(value.strip())

            if len(self.header) > 2:
                self.header = self.header[:-2]

    def get_header(self):
        self.open_file()
        return self.header

    def get_data_frame(self):
        self.data_frame = pd.read_csv(self.file_path, sep='	', header=10, index_col=None)
        return self.data_frame

    def get_heating_rate(self):
        return self.heating_rate


if __name__ == "__main__":
    file = FileProcessor(path="../../2023_02_15_02_PET_HR05.txt")

    header = file.get_header()
    data_frame = file.get_data_frame()

    for line in header:
        print(line)
    print(data_frame)
    print(file.get_heating_rate())
