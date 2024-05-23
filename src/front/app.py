import tkinter as tk
from tkinter import filedialog, scrolledtext, Toplevel, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Union
from tkinter import ttk

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

    def __init__(self, root: tk.Tk, file_processor: Union[str, FileProcessor]):
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

        self.header_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=9)
        self.header_text.pack(pady=10)

        self.method_combobox = ttk.Combobox(root, values=["min", "ls", "dif"])
        self.method_combobox.set("min")
        self.method_combobox.pack(pady=5)

        self.processing_button = tk.Button(root, text="Обработать данные", command=self.processing, state=tk.DISABLED)
        self.processing_button.pack(pady=10)
        

        self.result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=5)
        self.result_text.pack(pady=10)

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

            # Activate the processing button once data is loaded
            self.processing_button.config(state=tk.NORMAL)

    def processing(self) -> None:
        """
        Processes the loaded data using the Models class and displays the result in the result_text widget.
        """
        try:
            method = self.method_combobox.get()
            self.models = Models(self.data_frame, self.heating_rate)
            result = self.models.processing(method)
            if result:
                result_str = f"A = {result[0]}\nEa = {result[1]}\nn = {result[2]}\nm = {result[3]}\nalpha = {result[4]}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.INSERT, result_str)
                self.plot_button.config(state=tk.NORMAL)
            else:
                tk.messagebox.showinfo("Данные не обработаны!")
        except ValueError as e:
            tk.messagebox.showinfo("Ошибка", str(e))

    def plot_data(self):
        """
        Plots the processed data if available.
        """
        if hasattr(self, 'models') and self.models.coefs is not None:
            plot_window = tk.Toplevel(self.root)
            plot_window.title("График")
            plot_window.geometry("800x600+200+200")

            fig = self.models.draw()

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
