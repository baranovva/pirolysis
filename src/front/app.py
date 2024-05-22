import tkinter as tk
from tkinter import filedialog, scrolledtext, Toplevel, messagebox
from typing import Optional

from back import Models, FileProcessor


class App:
    """
    A class to create a GUI application.

    Attributes:
    -----------
    root : tk.Tk
        The root window of the Tkinter application.
    file_processor : FileProcessor
        An instance of the FileProcessor class for handling file operations.

    Methods:
    --------
    __init__(self, root, file_processor)
        Initializes the App with the window.

    open_file(self)
        Opens a file dialog to select a file, reads the header and data, and displays the header.

    processing(self)
        Processes the loaded data using the Models class and displays the result in a new window.

    plot_data(self)
        Plots the processed data if available.
    """

    def __init__(self, root: tk.Tk, file_processor: Optional[str, FileProcessor]):
        """
       Initializes the App with the window.

       Parameters:
       -----------
       root : tk.Tk
           The root window of the Tkinter application.
       file_processor : FileProcessor or str
           An instance of the FileProcessor class for handling file operations.
       """
        self.data_frame = None
        self.heating_rate = None

        self.root = root
        self.file_processor = file_processor

        self.root.title("Пиролиз")

        self.open_button = tk.Button(root, text="Открыть файл", command=self.open_file)
        self.open_button.pack(pady=10)

        self.header_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10)
        self.header_text.pack(pady=10)

        self.processing_button = tk.Button(root, text="Обработать данные", command=self.processing)
        self.processing_button.pack(pady=10)

        self.plot_button = tk.Button(root, text="Показать график", command=self.plot_data)
        self.plot_button.pack(pady=10)
        self.plot_button.config(state=tk.DISABLED)

    def open_file(self) -> None:
        """
        Opens a file dialog to select a file, reads the header and data, and displays the header.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.file_processor.file_path = file_path
            header = self.file_processor.get_header()
            self.header_text.delete(1.0, tk.END)
            self.header_text.insert(tk.INSERT, '\n'.join(header))

            self.data_frame = self.file_processor.get_data_frame()
            self.heating_rate = self.file_processor.get_heating_rate()

    def processing(self) -> None:
        """
        Processes the loaded data using the Models class and displays the result in a new window.
        """
        try:
            if self.data_frame is not None:
                self.models = Models(self.data_frame, self.heating_rate)
                result = self.models.processing()
                if result:
                    result_window = Toplevel(self.root)
                    result_window.title("Результат обработки")

                    result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=60, height=20)
                    result_text.pack(pady=10)
                    result_text.insert(tk.INSERT, result)
                    self.plot_button.config(state=tk.NORMAL)
                else:
                    raise ValueError("Данные не обработаны!")
            else:
                raise ValueError("Сначала загрузите данные!")
        except ValueError as e:
            tk.messagebox.showinfo("Ошибка", str(e))

    def plot_data(self) -> None:
        """
        Plots the processed data if available.
        """
        if hasattr(self, 'models') and self.models.coefs is not None:
            self.models.draw()
