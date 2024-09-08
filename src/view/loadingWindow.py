import time
from tkinter import ttk
import tkinter as tk

class LoadingWindow(tk.Tk):
    def __init__(self, operation):
        super().__init__()
        self.title(operation)
        self.label = ttk.Label(text="Progress\n: 0%", font=("Arial", 15))
        self.info = ttk.Label(
            text="Teste",
            font=("Arial", 15),
        )
        self.progressbar = ttk.Progressbar(
            orient=tk.HORIZONTAL, length=250, mode="determinate"
        )
        self.button_close = ttk.Button(text="X", command=self.close_window, width=5)
        self.label.place(x=25, y=4)
        self.progressbar.place(x=25, y=30)
        self.button_close.place(x=230, y=4)
        self.info.place(x=25, y=50)
        self.progress = 0
        self.geometry("300x200")

    def update_progress(self, value):
        try:
            self.progress = value
            self.progressbar["value"] = self.progress
            self.label.config(text=f"Progress: {self.progress}%")
            if value == 100:
                time.sleep(2)
                self.destroy()
        except Exception as e:
            print(value, "**")

    def close_window(self):
        self.destroy()

    def update_info(self, value):
        self.label.config(text=value)