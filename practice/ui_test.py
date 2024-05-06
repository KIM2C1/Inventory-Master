import tkinter as tk
from tkinter import ttk

def darkstyle(root):
    style = ttk.Style(root)
    root.tk.call("source", 'azure.tcl')
    root.tk.call("set_theme", 'dark')
    
    #style.theme_use('azure.tcl')
    style.configure("Accentbutton", foreground='white')
    style.configure("Togglebutton", foreground='white')
    return style

win = tk.Tk()
style = darkstyle(win)
win.update()

# 버튼 생성
button = ttk.Button(win, text="Click Me")
button.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")
button.pack()

win.mainloop()