import tkinter as tk

from back import FileProcessor
from front import App

if __name__ == "__main__":
    root = tk.Tk()
    file_processor = FileProcessor()
    app = App(root, file_processor)
    root.mainloop()
