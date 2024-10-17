import tkinter as tk
from tkinter import ttk
import itertools

class VideoPlayer:
    def __init__(self, title):
        self.window = tk.Tk()
        self.window.title(title)
        self.window.geometry("600x400")
        
        self.video_panel = tk.Frame(self.window, bg='black')
        self.video_panel.pack(fill=tk.BOTH, expand=True)
        
        self.button_panel = tk.Frame(self.window)
        self.button_panel.pack(side=tk.BOTTOM)
        
        self.play_button = ttk.Button(self.button_panel, text="Play", command=self.play_button_logic)
        self.play_button.pack(side=tk.LEFT)
        
        self.pause_button = ttk.Button(self.button_panel, text="Pause", command=self.pause_button_logic)
        self.pause_button.pack(side=tk.LEFT)
        
        self.stop_button = ttk.Button(self.button_panel, text="Stop", command=self.stop_button_logic)
        self.stop_button.pack(side=tk.LEFT)
        
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)
        
        self.rainbow_effect()
    
    def play_button_logic(self):
        # Play button logic
        print("Play button pressed")

    def pause_button_logic(self):
        # Pause button logic
        print("Pause button pressed")

    def stop_button_logic(self):
        # Stop button logic
        print("Stop button pressed")

    def rainbow_effect(self):
        colors = [
            "#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"
        ]
        
        color_iter = itertools.cycle(colors)
        
        def change_color():
            next_color = next(color_iter)
            self.window.configure(bg=next_color)
            
            self.window.after(100, change_color)  
        
        change_color()
    
    def run(self):
        self.window.mainloop()