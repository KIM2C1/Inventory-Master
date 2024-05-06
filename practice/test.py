import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def on_double_click(event):
    item = tree.selection()[0]
    values = tree.item(item, "values")
    print("선택한 행열의 데이터:", values)

def on_select(event):
    item = tree.selection()[0]
    values = tree.item(item, "values")
    image_path = values[1]  # 이미지 경로는 두 번째 열에 있음
    show_image(image_path)

def show_image(image_path):
    image = Image.open(image_path)
    image.thumbnail((300, 300))  # 이미지 크기 조정
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)
    label.image = photo

# Tkinter 창 생성
root = tk.Tk()
root.title("테이블 예제")

# 표 생성
columns = ("이름", "이미지 경로", "주소")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=0, column=0, padx=10, pady=10)  # 그리드 형태로 배치

# 표에 데이터 추가
data = [("이름1", "images/image1.jpg", "주소1"), 
        ("이름2", "images/image2.jpg", "주소2"),
        ("이름3", "images/image3.png", "주소3")]
for item in data:
    tree.insert('', 'end', values=item)

# 더블클릭 이벤트 처리
tree.bind("<Double-1>", on_double_click)
# 선택 이벤트 처리
tree.bind("<<TreeviewSelect>>", on_select)

# 이미지 표시를 위한 라벨
label = tk.Label(root)
label.grid(row=0, column=1, padx=10, pady=10)  # 그리드 형태로 배치

root.mainloop()