import tkinter as tk
from tkinter import ttk

def update_count():
    global count
    new_count = count_entry.get()
    try:
        count = int(new_count)
        count_label.config(text=f"Count: {count}")
        #count_entry.delete(0, 'end')  # 입력 필드 비우기
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def update_count_entry():
    count_entry.insert(0, str(count))

# Tkinter 애플리케이션 생성
root = tk.Tk()
root.title("Count Update")

# 변수 초기화
count = 1

# 레이블과 입력 필드 생성
count_label = ttk.Label(root, text=f"Count: {count}")
count_label.pack(pady=10)

count_entry = ttk.Entry(root)
count_entry.pack(pady=5)

update_button = ttk.Button(root, text="Update Count", command=update_count)
update_button.pack(pady=5)

# 초기 count 값을 입력 필드에 표시
update_count_entry()

root.mainloop()