import tkinter as tk
from tkinter import filedialog, scrolledtext, Toplevel
from back import Models


class App:
    def __init__(self, root, file_processor):
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

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.file_processor.file_path = file_path
            header = self.file_processor.get_header()
            self.header_text.delete(1.0, tk.END)
            self.header_text.insert(tk.INSERT, '\n'.join(header))

            self.data_frame = self.file_processor.get_data_frame()
            self.heating_rate = self.file_processor.get_heating_rate()

    def processing(self):
        try:
            if self.data_frame is not None:
                models = Models(self.data_frame, self.heating_rate)
                result = models.processing()
                if result:
                    result_window = Toplevel(self.root)
                    result_window.title("Результат обработки")

                    result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=60, height=20)
                    result_text.pack(pady=10)
                    result_text.insert(tk.INSERT, result)
                else:
                    raise ValueError("Данные не обработаны!")
            else:
                raise ValueError("Сначала загрузите данные!")
        except ValueError as e:
            tk.messagebox.showinfo("Ошибка", str(e))
