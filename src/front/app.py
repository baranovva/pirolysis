import tkinter as tk
from tkinter import filedialog, scrolledtext, Toplevel, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Union
from tkinter import ttk
import numpy as np
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
    __init__(self, root: tk.Tk, file_processor: Union[str, FileProcessor])
        Initializes the App with the window and sets up the GUI components.

    toggle_custom_params(self)
        Toggles the visibility of the custom parameters frame.

    open_file(self) -> None
        Opens a file dialog to select a file, reads the header and data, and displays the header.

    get_custom_bounds_and_initials(self) -> tuple
        Retrieves custom bounds and initial conditions from the GUI inputs.

    processing(self) -> None
        Processes the loaded data using the Models class and displays the result in the result_text widget.

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
        self.models = None
        self.data_frame = None
        self.heating_rate = None

        self.root = root
        self.file_processor = file_processor

        self.root.title("Пиролиз")

        self.open_button = tk.Button(root, text="Открыть файл", command=self.open_file)
        self.open_button.pack(pady=10)

        self.header_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=9)
        self.header_text.pack(pady=10)

        self.method_combobox = ttk.Combobox(root, values=["minimize", "least squares", "differential evolution"])
        self.method_combobox.set("minimize")
        self.method_combobox.pack(pady=5)

        self.custom_params_frame_visible = False
        self.toggle_button = tk.Button(root, text="Показать дополнительные параметры",
                                       command=self.toggle_custom_params
                                       )
        self.toggle_button.pack(pady=5)

        self.custom_params_frame = tk.Frame(root)
        self.custom_params_frame.pack(pady=5)

        self.bounds_entries = {}
        self.initial_entries = {}
        param_labels = ['A', 'Ea', 'n', 'm', 'alpha_zv']
        default_bounds = [(1e10, 1e12), (4 * 1e3, 4 * 1e5), (0, 5), (0, 5), (-1, 1)]
        default_initials = [1e11, 1e4, 1, 1, 0.3]

        for i, label in enumerate(param_labels):
            tk.Label(self.custom_params_frame, text=f"{label} min:").grid(row=i, column=0, padx=5, pady=2)
            min_entry = tk.Entry(self.custom_params_frame)
            min_entry.grid(row=i, column=1, padx=5, pady=2)
            min_entry.insert(0, default_bounds[i][0])

            tk.Label(self.custom_params_frame, text=f"{label} max:").grid(row=i, column=2, padx=5, pady=2)
            max_entry = tk.Entry(self.custom_params_frame)
            max_entry.grid(row=i, column=3, padx=5, pady=2)
            max_entry.insert(0, default_bounds[i][1])

            self.bounds_entries[label] = (min_entry, max_entry)

            tk.Label(self.custom_params_frame, text=f"{label} initial:").grid(row=i, column=4, padx=5, pady=2)
            initial_entry = tk.Entry(self.custom_params_frame)
            initial_entry.grid(row=i, column=5, padx=5, pady=2)
            initial_entry.insert(0, default_initials[i])

            self.initial_entries[label] = initial_entry

        self.custom_params_frame.pack_forget()
        self.processing_button = tk.Button(root, text="Обработать данные", command=self.processing, state=tk.DISABLED)
        self.processing_button.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=30, height=5)
        self.result_text.pack(pady=10)

        self.plot_button = tk.Button(root, text="Показать график", command=self.plot_data)
        self.plot_button.pack(pady=10)
        self.plot_button.config(state=tk.DISABLED)

    def toggle_custom_params(self) -> None:
        """
        Toggles the visibility of the custom_params_frame.

        Returns: None
        """
        if self.custom_params_frame_visible:
            self.custom_params_frame.pack_forget()
            self.toggle_button.config(text="Показать дополнительные параметры")
        else:
            self.custom_params_frame.pack(pady=5, before=self.processing_button)
            self.toggle_button.config(text="Скрыть дополнительные параметры")
        self.custom_params_frame_visible = not self.custom_params_frame_visible
        
    def open_file(self) -> None:
        """
        Opens a file dialog to select a file, reads the header and data, and displays the header.

        Returns: None
        """
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.file_processor.file_path = file_path
            header = self.file_processor.get_header()
            self.header_text.delete(1.0, tk.END)
            self.header_text.insert(tk.INSERT, '\n'.join(header))

            self.data_frame = self.file_processor.get_data_frame()
            self.heating_rate = self.file_processor.get_heating_rate()
            self.processing_button.config(state=tk.NORMAL)

    def get_custom_bounds_and_initials(self) -> tuple:
        """
        Retrieves custom bounds and initial conditions from the GUI inputs.

        Returns:
        --------
        tuple
            Dictionary containing custom bounds and list of initial conditions.
        """
        custom_bounds = {}
        custom_initials = []
        for param, (min_entry, max_entry) in self.bounds_entries.items():
            custom_bounds[param] = (float(min_entry.get()), float(max_entry.get()))

        for param, initial_entry in self.initial_entries.items():
            custom_initials.append(float(initial_entry.get()))

        custom_initials[1] = np.log(custom_initials[1])
        custom_bounds['logEa'] = (np.log(custom_bounds['Ea'][0]), np.log(custom_bounds['Ea'][1]))
        custom_bounds['A'] = (custom_bounds['A'][0], custom_bounds['A'][1])

        return custom_bounds, custom_initials

    def processing(self) -> None:
        """
        Processes the loaded data using the Models class and displays the result in the result_text widget.

        Returns: None
        """
        try:
            method = self.method_combobox.get()
            custom_bounds, custom_initials = self.get_custom_bounds_and_initials()

            self.models = Models(self.data_frame, self.heating_rate)
            result = self.models.processing(method, custom_bounds, custom_initials)
            if result:
                result_str = f"A = {result[0]:.3e}\nEa = {result[1]:.3e}\nn = {result[2]:.5f}\nm = {result[3]:.5f}\nalpha = {result[4]:.5f}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.INSERT, result_str)
                self.plot_button.config(state=tk.NORMAL)
            else:
                tk.messagebox.showinfo("Данные не обработаны!")
        except ValueError as e:
            tk.messagebox.showinfo("Ошибка", str(e))

    def plot_data(self) -> None:
        """
        Plots the processed data if available.

        Returns: None
        """
        if hasattr(self, 'models') and self.models.coefs is not None:
            plot_window = tk.Toplevel(self.root)
            plot_window.title("График")
            plot_window.geometry("800x600+200+200")

            fig = self.models.draw()

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
