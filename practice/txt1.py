import tkinter as tk
from tkinter import ttk

def bring_second_to_top():
    second_window.lift()  # 두 번째 창을 최상위로 올림

# 메인 윈도우 생성
root = tk.Tk()
root.title("Main Window")
root.geometry("300x200")

# 첫 번째 Toplevel 창 생성
first_window = tk.Toplevel(root)
first_window.title("First Toplevel Window")
first_window.geometry("300x200")

# 두 번째 Toplevel 창 생성
second_window = tk.Toplevel(root)
second_window.title("Second Toplevel Window")
second_window.geometry("300x200")

# 첫 번째 창에 버튼 배치
btn_bring_second = ttk.Button(first_window, text="Bring Second to Top", command=bring_second_to_top)
btn_bring_second.pack(pady=20)

# 메인 루프
root.mainloop()