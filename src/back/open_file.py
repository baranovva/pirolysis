from typing import Optional

import pandas
import pandas as pd


class FileProcessor:
    """
   A class to process files and extract relevant data.

   Attributes:
   -----------
   file_path : str
       The path to the file to be processed.
   header : list
       A list to store the header lines from the file.
   data_frame : pandas.DataFrame or None
       A DataFrame to store the file data after processing.
   heating_rate : float or None
       The heating rate value extracted from the file header.

   Methods:
   --------
   __init__(path: str = "")
       Initializes the FileProcessor with an optional file path.

   open_file()
       Opens the file, reads the header, and extracts the heating rate.

   get_header() -> list
       Returns the header lines from the file.

   get_data_frame() -> pandas.DataFrame
       Returns the data frame created from the file contents.

   get_heating_rate() -> float or None
       Returns the heating rate extracted from the file header.
    """

    def __init__(self, path: str = ""):
        """
       Initializes the FileProcessor with an optional file path.

       Parameters:
       -----------
       path : str, optional
           The path to the file to be processed (default is an empty string).
        """
        self.file_path = path
        self.header = []
        self.data_frame = None
        self.heating_rate = None

    def open_file(self) -> None:
        """
        Opens the file, reads the header lines, and extracts the heating rate.

        This method reads the first 11 lines of the file. Lines starting with a '#'
        are considered as header lines. The heating rate is extracted from the
        header if it is present. The header is trimmed to exclude the last two lines.
        """
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

    def get_header(self) -> list:
        """
        Returns the header lines from the file.

        Returns:
        --------
        list
            A list of header lines from the file.
        """
        self.open_file()
        return self.header

    def get_data_frame(self) -> pandas.DataFrame:
        """
        Returns the data frame created from the file contents.

        The data frame is created by reading the file with pandas read_csv method,
        starting from the 11th line.

        Returns:
        --------
        pandas.DataFrame
            The data frame containing the file contents.
        """
        self.data_frame = pd.read_csv(self.file_path, sep='	', header=10, index_col=None)
        return self.data_frame

    def get_heating_rate(self) -> Optional[float]:
        """
        Returns the heating rate extracted from the file header.

        Returns:
        --------
        float or None
            The heating rate value if it was found in the file header, otherwise None.
        """
        return self.heating_rate


if __name__ == "__main__":
    file = FileProcessor(path="../../2023_02_15_02_PET_HR05.txt")

    header = file.get_header()
    data_frame = file.get_data_frame()

    for line in header:
        print(line)
    print(data_frame)
    print(file.get_heating_rate())
