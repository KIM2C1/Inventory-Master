import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def on_click(event):
    global prev_selected_item
    global prev_selected_col
    # 현재 선택된 항목과 열 가져오기
    selected_item = tree.selection()
    col = tree.identify_column(event.x)
    # 이전에 선택된 항목과 열이 없거나 현재 선택된 항목 또는 열이 변경되었을 때만 실행
    if not prev_selected_item or prev_selected_item != selected_item or prev_selected_col != col:
        # 선택된 항목과 열 업데이트
        prev_selected_item = selected_item
        prev_selected_col = col
        # 클릭된 열이 있는 경우에만 실행
        if col:
            # 클릭된 열의 인덱스 가져오기
            col_index = int(col.replace("#", "")) - 1
            # 선택된 항목이 있는지 확인
            if selected_item:
                # 선택된 행 가져오기
                item = selected_item[0]
                # 선택된 행의 데이터 가져오기
                values = tree.item(item, "values")
                # 클릭된 열에 따라 처리
                if col_index == 0:  # 이름 열
                    print(values[col_index])
                elif col_index == 1:  # 이미지 경로 열
                    show_image_popup(values[col_index])
                elif col_index == 2:
                    print(values[col_index])

def show_image_popup(image_path):
    # 이미지 경로를 받아서 이미지를 팝업으로 열기
    image = Image.open(image_path)
    image.show()

# Tkinter 창 생성
root = tk.Tk()
root.title("테이블 예제")

# 표 생성
columns = ("이름", "이미지 경로", "주소")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack()

# 표에 데이터 추가
data = [("T1", "images.jpg", "1-2"), ("T2", "1-2.jpg", "2-2"), ("T3", "1-3.jpg", "3-2"), ("T4", "1-4.jpg", "4-2"), ("T5", "1-5.jpg", "5-2")]
for item in data:
    tree.insert('', 'end', values=item)

# 클릭 이벤트 처리
prev_selected_item = None  # 이전에 선택된 항목을 저장할 변수 초기화
prev_selected_col = None  # 이전에 선택된 열을 저장할 변수 초기화
tree.bind("<Button-1>", on_click)

root.mainloop()