import tkinter as tk
from tkinter import ttk
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import json
import tkinter.messagebox
import time
import os

#global var
history_table = ""
item_tag = ["이름", "총 갯수", "사용중", "태그", "링크", "이미지주소", "카테고리"]
history_tag = ["아이템", "사용자", "갯수", "사용 날짜", "카테고리"]
history_find_tag = ["아이템", "카테고리"]
filename_tag = ["sensor.json", "cable.json"]
filename_name = ["센서", "케이블"]
is_select = False

def show_error_message(message):
    """Display an error message box with a custom message."""
    root = tk.Tk()  # This is required to initialize Tkinter and should be part of your main application logic
    root.withdraw()  # This hides the root window which we don't need to see
    tkinter.messagebox.showerror("Error", message)
    root.destroy()  # Clean up the root window after closing messagebox

def create_table(tab, columns):
    # 표를 만들고 형식 포맷하는 함수
    tree = ttk.Treeview(tab, columns=columns, show="headings") 
    for col in columns:
        tree.heading(col, text=col)
        if not col == "태그":
            tree.column(col, anchor='center', width=100)  # 중앙 정렬
    tree.pack(side="left", fill="both", expand=True)

    return tree

def read_file(filename, tree=None, tag=None):
    global history_taghistory_tag

    Check = False
    for name_tag in filename:
        try:
            if os.path.getsize(name_tag) > 0:
                with open(name_tag, "r", encoding="utf-8") as file:
                    loaded_data = json.load(file)
            else:
                loaded_data = []
        except FileNotFoundError:
            loaded_data = []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file '{name_tag}': {e}")

        if tree == history_table and tag:
            tree.delete(*tree.get_children())
            for index, item in enumerate(loaded_data):
                if tag[0] == item["아이템"]:
                    values = [item[name] for name in history_tag]
                    tree.insert('', 'end', values=values)
           
        elif tree and tag:
            
            for index, item in enumerate(loaded_data):
                if all (name in item for name in tag):
                    if not Check:
                        tree.delete(*tree.get_children())
                        Check = True
                    values = [item[name] for name in tag] 
                    values.insert(3, int(item["총 갯수"]) - int(item["사용중"]))
                    tree.insert('', 'end', values=values)
                else:
                    print(f"Invalid data format in file '{item}': Missing tag.")
        else:
            pass

    Check = False
    return loaded_data
    
def write_file(filename, data, tag):
    try:
        if os.path.getsize(filename) > 0:
            with open(filename, "r", encoding="utf-8") as file:
                loaded_data = json.load(file)
        else:
            loaded_data = []
    except FileNotFoundError:
        loaded_data = []

    loaded_data.append(dict(zip(tag, data)))

    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(loaded_data, file, ensure_ascii=False, indent=len(tag))
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error writing to JSON file '{filename}': {e}")

def tab_index():
    global filename_tag, tree_tag

    current_tab_index = tab_control.index(tab_control.select())
    current_tab_text = tab_control.tab(current_tab_index, "text")
    filename = []

    if current_tab_index == 0:
        filename = filename_tag[:]
    else:
        filename.append(filename_tag[current_tab_index - 1])

    #info_tab[] = [filename, tree_var_name, tree_dp_name]
    info_tab = [filename, tree_tag[current_tab_index], current_tab_text]

    return info_tab

def change_form():
    info_select = tab_select()

    change_window = tk.Toplevel(root)
    change_window.title("데이터 변경")
    change_window.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    form_frame = ttk.Frame(change_window)
    form_frame.pack(padx=10, pady=10)

    # 이름 입력
    ttk.Label(form_frame, text="이름:").grid(row=0, column=0, sticky="w")
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=0, column=1)
    name_entry.insert(0, info_select[0])

    # 갯수 입력
    ttk.Label(form_frame, text="총 갯수:").grid(row=1, column=0, sticky="w")
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=1, column=1)
    quantity_entry.insert(0, info_select[1])

    # 링크 입력
    ttk.Label(form_frame, text="태그:").grid(row=2, column=0, sticky="w")
    link_entry = ttk.Entry(form_frame)
    link_entry.grid(row=2, column=1)
    link_entry.insert(0, info_select[4])

    # 태그 입력
    ttk.Label(form_frame, text="링크:").grid(row=3, column=0, sticky="w")
    tag_entry = ttk.Entry(form_frame)
    tag_entry.grid(row=3, column=1)
    tag_entry.insert(0, info_select[5])

    # 이미지 주소 입력
    ttk.Label(form_frame, text="이미지 주소:").grid(row=4, column=0, sticky="w")
    imagePath_entry = ttk.Entry(form_frame)
    imagePath_entry.grid(row=4, column=1)
    imagePath_entry.insert(0, info_select[6])

    # 아이템 타입 선택
    ttk.Label(form_frame, text="아이템 타입:").grid(row=5, column=0, sticky="w")
    item_type = ttk.Combobox(form_frame, values=["센서", "케이블"])
    item_type.grid(row=5, column=1)
    item_type.set(info_select[7])

    buttom_frame = ttk.Frame(form_frame)
    buttom_frame.grid(row=6, column=1, pady=10, padx=(0, 20))

    def change_data():
        info_select = tab_select() 

        name = name_entry.get()
        quantity = quantity_entry.get()
        tag = tag_entry.get()
        link = link_entry.get()
        imagePath = imagePath_entry.get()
        item = item_type.get()

        try:
            if os.path.getsize(info_select[8]) > 0:
                with open(info_select[8], "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = []
        except FileNotFoundError:
            data = []

        for i in range(len(data)):
            if data[i]['이름'] == info_select[0]:
                if data[i]['카테고리'] != item:
                    new_data = [entry for entry in data if not (entry['이름'] == info_select[0])]

                    with open(info_select[8], "w", encoding="utf-8") as file:
                        json.dump(new_data, file, ensure_ascii=False, indent=6)
   
                    try:
                        if os.path.getsize(info_select[8]) > 0:
                            with open(info_select[8], "r", encoding="utf-8") as file:
                                data = json.load(file)
                        else:
                            data = []
                    except FileNotFoundError:
                        data = []

                    data.append({
                        "이름": name,
                        "총 갯수": quantity,
                        "사용중": 0,
                        "태그": tag,
                        "링크": link,
                        "이미지주소": imagePath,
                        "카테고리": item
                    })
                else:
                    data[i]['이름'] = name
                    data[i]['총 갯수'] = quantity
                    data[i]['사용중'] = 0
                    data[i]['태그'] = tag
                    data[i]['링크'] = link
                    data[i]['이미지주소'] = imagePath
                    data[i]['카테고리'] = item

                with open(info_select[8], "w", encoding="utf-8") as file:
                        json.dump(data, file, ensure_ascii=False, indent=6)

    def del_data():
        info_select = tab_select()

        try:
            if os.path.getsize(info_select[8]) > 0:
                with open(info_select[8], "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = []
        except FileNotFoundError:
            data = []

        for i in range(len(data)):
            if data[i]['이름'] == info_select[0]:

                new_data = [entry for entry in data if not (entry['이름'] == info_select[0])]

                with open(info_select[8], "w", encoding="utf-8") as file:
                    json.dump(new_data, file, ensure_ascii=False, indent=6)
            else:
                pass

    change_button = ttk.Button(buttom_frame, width=5, text="변경", command=change_data)
    change_button.pack(side="left", padx=(0, 5))

    delete_button = ttk.Button(buttom_frame, width=5, text="삭제", command=del_data)
    delete_button.pack(side="left")

def save_history_date(tree):
    info_select = tab_select()

    try:
        if os.path.getsize("history.json") > 0:
            with open("history.json", "r", encoding="utf-8") as file:
                history_data = json.load(file)
                #print(history_data)
        else:
            history_data = []
    except FileNotFoundError:
        history_data = []

    history_data.append({
            "아이템": tree[0],
            "사용자": tree[1],
            "갯수": tree[2],
            "사용 날짜": tree[3],
            "카테고리": tree[4]
        })

    with open("history.json", "w", encoding="utf-8") as file:
        json.dump(history_data, file, ensure_ascii=False, indent=4)

    try:
        if os.path.getsize(info_select[8]) > 0:
            with open(info_select[8], "r", encoding="utf-8") as file:
                tree_data = json.load(file) #트리 데이터중 현재 수정중인 데이터만 찾아야 함
        else:
            tree_data = []
    except FileNotFoundError:
        tree_data = []

    for i in range(len(tree_data)):
        if tree_data[i]['이름'] == tree[0]:
            
            tree_data[i]['사용중'] = int(tree_data[i]['사용중']) + int(tree[2])
            #print(int(tree_data[i]['갯수']))

    with open(info_select[8], "w", encoding="utf-8") as file:
        json.dump(tree_data, file, ensure_ascii=False, indent=6)

def del_history_date():
    info_select = tab_select()
    global info_history_select

    print(info_history_select)

    try:
        if os.path.getsize(info_select[8]) > 0:
            with open(info_select[8], "r", encoding="utf-8") as file:
                tree_data = json.load(file) #트리 데이터중 현재 수정중인 데이터만 찾아야 함
        else:
            tree_data = []
    except FileNotFoundError:
        tree_data = []

    for i in range(len(tree_data)):
        if tree_data[i]['이름'] == info_select[0]:
            tree_data[i]['사용중'] = int(tree_data[i]['사용중']) - int(info_history_select[1])

    with open(info_select[8], "w", encoding="utf-8") as file:
        json.dump(tree_data, file, ensure_ascii=False, indent=6)

    with open("history.json", "r", encoding="utf-8") as json_file:
        try:
            data = json.load(json_file)
            new_data = [entry for entry in data if not (entry['사용자'] == info_history_select[0] and entry['갯수'] == info_history_select[1] and entry['사용 날짜'] == info_history_select[2])]
            
            with open("history.json", "w", encoding="utf-8") as file:
                json.dump(new_data, file, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file 'history.json': {e}")

    info_history_select = ()

scrollbars = {}

def switch_tab(event=None):
    #info_tab[] = [filename, tree_var_name, tree_dp_name]
    info_tab = tab_index()
    
    read_file(info_tab[0], info_tab[1], item_tag)
    update_scrollbar(info_tab[1], info_tab[2])

def update_scrollbar(treeview, tab_name):
    # Remove the previous scrollbar if it exists
    if tab_name in scrollbars and scrollbars[tab_name]:
        scrollbars[tab_name].destroy()

    # Create a new scrollbar for the given treeview
    scrollbar = ttk.Scrollbar(treeview.master, orient='vertical', command=treeview.yview)
    scrollbar.pack(side='right', fill='y')
    treeview.configure(yscrollcommand=scrollbar.set)
    scrollbars[tab_name] = scrollbar

    # Fix column widths for the treeview to avoid resizing
    for column in treeview["columns"]:
        treeview.column(column, width=100)  # Adjust the width as needed

def register_item():
    # 아이템 등록 함수
    register_window = tk.Toplevel(root)
    register_window.title("아이템 등록")
    register_window.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    # 폼 생성
    form_frame = ttk.Frame(register_window)
    form_frame.pack(padx=10, pady=10)

    # 이름 입력
    ttk.Label(form_frame, text="이름:").grid(row=0, column=0, sticky="w")
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=0, column=1)

    # 갯수 입력
    ttk.Label(form_frame, text="갯수:").grid(row=1, column=0, sticky="w")
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=1, column=1)

    # 링크 입력
    ttk.Label(form_frame, text="태그:").grid(row=2, column=0, sticky="w")
    link_entry = ttk.Entry(form_frame)
    link_entry.grid(row=2, column=1)

    # 태그 입력
    ttk.Label(form_frame, text="링크:").grid(row=3, column=0, sticky="w")
    tag_entry = ttk.Entry(form_frame)
    tag_entry.grid(row=3, column=1)

    # 이미지 주소 입력
    ttk.Label(form_frame, text="이미지 주소:").grid(row=4, column=0, sticky="w")
    imagePath_entry = ttk.Entry(form_frame)
    imagePath_entry.grid(row=4, column=1)

    # 아이템 타입 선택
    ttk.Label(form_frame, text="아이템 타입:").grid(row=5, column=0, sticky="w")
    item_type = ttk.Combobox(form_frame, values=["센서", "케이블"])
    item_type.grid(row=5, column=1)

    # 등록 버튼이 눌리면 폼의 내용을 가져와서 처리
    def on_focus_in(event):
        if event.widget.get() == "필수항목" or event.widget.get() == "잘못된 데이터" or event.widget.get() == "양수를 입력하시오":
            event.widget.delete(0, 'end')  # Clear the existing text
            event.widget.config(foreground="white")  # Change the text color back to black

    def handle_register():
        global item_tag, filename_name, tree_tag, filename_tag

        # 각 항목의 값을 가져옴
        name = name_entry.get()
        quantity = quantity_entry.get()
        tag = tag_entry.get()
        link = link_entry.get()
        imagePath = imagePath_entry.get()
        item = item_type.get()
    
        # 빈 항목을 찾기 위한 리스트 생성
        entries = [name_entry, quantity_entry, tag_entry, link_entry, imagePath_entry, item_type]
        values = [name, quantity, tag, link, imagePath, item]
        item_value = ["센서", "케이블"]

        # 빈 항목의 이름을 저장할 리스트
        empty_entries = []
        for entry, value in zip(entries, values):
            if not value or value == "필수항목" or value == "잘못된 데이터":
                empty_entries.append(entry)
                entry.delete(0, 'end')
                entry.insert(0, "필수항목")
                entry.config(foreground="red")

            if entry == quantity_entry:
                try:
                    if int(value) < 0:
                        raise ValueError
                except ValueError:
                    empty_entries.append(entry)
                    quantity_entry.delete(0, 'end')
                    quantity_entry.insert(0, "양수를 입력하시오")
                    quantity_entry.config(foreground="red")

            if entry == item_type and value not in item_value:
                    empty_entries.append(entry)
                    item_type.delete(0, 'end')
                    item_type.insert(0, "잘못된 데이터")
                    item_type.config(foreground="red")
        # 빈 항목이 있는지 확인하고 있으면 함수 종료
        if empty_entries:
            return
        else:
            # 각 항목을 처리하는 코드를 여기에 추가
            data = (name, quantity, 0, tag, link, imagePath, item)

            for index, name in enumerate(filename_name):
                if item == name:
                    tree_tag[index + 1].insert('', 'end', values=data)
                    write_file(filename_tag[index], values, item_tag)
                else:
                    pass

        register_window.destroy()
    
    # Applying focus binding to each entry
    for entry in [name_entry, quantity_entry, tag_entry, link_entry, imagePath_entry, item_type]:
        entry.bind("<FocusIn>", on_focus_in)

    # 등록 버튼 생성
    register_button = ttk.Button(form_frame, text="등록", command=handle_register)
    register_button.grid(row=6, columnspan=2)

    # 창을 화면 중앙에 배치
    register_window.update()
    register_window.minsize(register_window.winfo_width(), register_window.winfo_height())
    x_cordinate1 = int((register_window.winfo_screenwidth() / 2) - (register_window.winfo_width() / 2))
    y_cordinate1 = int((register_window.winfo_screenheight() / 2) - (register_window.winfo_height() / 2))
    register_window.geometry("+{}+{}".format(x_cordinate1, y_cordinate1))

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    

history_window_open = False
history_window = None 

def history_item():
    global history_window_open
    global history_window
    global is_select

    info_select = tab_select()

    if history_window_open or not is_select:
        show_error_message("이미 열려있습니다!")
        return
    
    history_window_open = True

    history_window = tk.Toplevel(root)
    history_window.title("히스토리 추가")
    history_window.protocol("WM_DELETE_WINDOW", on_history_window_close)  # 윈도우가 닫힐 때 호출될 함수 지정
    history_window.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    form_frame = ttk.Frame(history_window)
    form_frame.pack(padx=10, pady=10)

    ttk.Label(form_frame, text="아이템:").grid(row=0, column=0, sticky="w")
    item_label = ttk.Label(form_frame, text=str(info_select[0]))
    item_label.grid(row=0, column=1)

    ttk.Label(form_frame, text="사용자:").grid(row=1, column=0, sticky="w")
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=1, column=1)

    ttk.Label(form_frame, text="갯수:").grid(row=2, column=0, sticky="w")
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=2, column=1)

    ttk.Label(form_frame, text="아이템 타입:").grid(row=3, column=0, sticky="w")
    item_type = ttk.Label(form_frame, text=str(info_select[7]))
    item_type.grid(row=3, column=1)

    ttk.Label(form_frame, text="사용 날짜:").grid(row=4, column=0, sticky="w")
    date_entry = ttk.Entry(form_frame)
    date_entry.grid(row=4, column=1)

    current_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d", current_time)

    date_entry.insert(0, str(formatted_time))

    def handle_history():
        item = str(info_select[0])
        name = name_entry.get()
        quantity = quantity_entry.get()
        date = date_entry.get()
        category = str(info_select[7])

        entries = [item_label, name_entry, quantity_entry, date_entry, item_type]
        values = [item, name, quantity, date, category]

        empty_entries = []
        for entry, value in zip(entries, values):
            if not value or value == "필수항목":
                empty_entries.append(entry)
                entry.delete(0, 'end')
                entry.insert(0, "필수항목")
                entry.config(foreground="red")

        if empty_entries:
            return
        else:
            data = (name, quantity, date)
            history_table.insert('', 'end', values=data)
            save_history_date(values)

    register_button = ttk.Button(form_frame, text="등록", command=handle_history)
    register_button.grid(row=5, columnspan=2)

    history_window.update()
    history_window.minsize(history_window.winfo_width(), history_window.winfo_height())
    x_cordinate1 = int((history_window.winfo_screenwidth() / 2) - (history_window.winfo_width() / 2))
    y_cordinate1 = int((history_window.winfo_screenheight() / 2) - (history_window.winfo_height() / 2))
    history_window.geometry("+{}+{}".format(x_cordinate1, y_cordinate1))

def on_history_window_close():
    global history_window_open
    history_window_open = False  # 폼이 닫힐 때 history_window_open 값을 False로 설정
    history_window.destroy()  # 윈도우를 파괴하여 메모리 누수를 방지

def search_event(event=None):
    info_tab = tab_index()
    keyword = search_entry.get().strip()  

    def search_data(keyword):
        global item_tag

        try:
            Check = False
            for i in range(len(info_tab[0])):
                loaded_data = read_file([info_tab[0][i]])
                for index, item in enumerate(loaded_data):
                    if keyword in item["이름"] or keyword in item["태그"]:
                        if not Check:
                            info_tab[1].delete(*info_tab[1].get_children())
                            Check = True
                        values = [item[name] for name in item_tag] 
                        values.insert(3, int(item["총 갯수"]) - int(item["사용중"]))
                        info_tab[1].insert('', 'end', values=values)
            
            
        except FileNotFoundError:
            pass
        Check = False

    if keyword:
        search_data(keyword)
    else:
        read_file(info_tab[0], info_tab[1], item_tag)

def open_link(event):
    # 링크를 클릭할 때 웹 브라우저에서 해당 링크 열기
    item = event.widget.selection()[0]
    link = event.widget.item(item, "values")[5]  # 링크는 세 번째 열에 있음
    if link:  # 링크가 비어있지 않으면 열기
        webbrowser.open(link)

def configure_styles():
    style.configure("Treeview", font=("나눔고딕", 12))
    style.configure("Treeview.Heading", font=("나눔고딕", 12))
    style.configure("Accentbutton", foreground='white')
    style.configure("Togglebutton", foreground='white')
    style.configure("TNotebook.Tab", font=("나눔고딕", 12))
    style.configure("TButton", font=("나눔고딕", 12))

def load_and_display_image(url):
    global history_table

    if not url:
        url = "https://as1.ftcdn.net/v2/jpg/02/14/73/42/1000_F_214734237_YnPf35kd8stUEpmiKwUsr22z11V1YQox.jpg"
    try:
        # Get the image from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise exception if there is an error
        # Create a PIL image from the image data
        image_data = BytesIO(response.content)
        pil_image = Image.open(image_data)
        # 이미지의 크기를 조절합니다.
        pil_image.thumbnail((250, 250))
        # Convert the PIL image to a format that Tkinter can use
        tk_image = ImageTk.PhotoImage(pil_image)
        # If the image label already exists, update its image
        if hasattr(load_and_display_image, 'image_label'):
            load_and_display_image.image_label.config(image=tk_image)
            load_and_display_image.image_label.image = tk_image
        else:
            # Create a bordered frame for the image
            border_frame = ttk.Frame(image_frame, borderwidth=2, relief="groove")
            #border_frame = ttk.Frame(image_frame, borderwidth=2, relief="groove", style='White.TFrame')
            
            border_frame.pack(fill='both', padx=10, pady=(10, 0))
            # Create a Tkinter label widget inside the border frame and set the image
            image_label = ttk.Label(border_frame, image=tk_image)
            image_label.image = tk_image  # Keep a reference to prevent garbage collection
            image_label.pack(pady=(10, 10))
            load_and_display_image.image_label = image_label  # Store the label for reuse
        image_frame.update_idletasks()  # Update the container's information
        # Get the width of the grid
        width = image_frame.grid_size()[0]
        # If the text label already exists, update its width
        if hasattr(load_and_display_image, 'text_label'):
            load_and_display_image.text_label.config(width=width) 
        else:
            
            # Create a label widget for the text below the image
            history_table = ttk.Treeview(log_frame, columns=("사용자", "갯수", "사용 날짜"), show="headings")
            history_table.heading("사용자", text="사용자")
            history_table.heading("갯수", text="갯수")
            history_table.heading("사용 날짜", text="사용 날짜")
            history_table.column("사용자", width=100, anchor="center")
            history_table.column("갯수", width=70, anchor="center")
            history_table.column("사용 날짜", width=100, anchor="center")
            history_table.pack(side='left',fill='x')

            scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=history_table.yview)
            scrollbar.pack(side='right', fill='y')
            history_table.configure(yscroll=scrollbar.set)
            history_table.bind("<<TreeviewSelect>>", his_select)
            #text_label = ttk.Label(log_frame, text="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", width=width)
            #text_label.pack(fill='x')
            load_and_display_image.history_table = history_table  # Store the label for reuse
    except requests.RequestException as e:
        print(f"Error loading image: {e}")

def tab_select(event=None):
    global is_select
    global filename_tag, filename_name


    info_tab = tab_index()

    if info_tab[1].selection():
        is_select = True
        item = info_tab[1].selection()[0]

        #info_select[] = [name, total_cnt, use_cnt, invente_cnt, tag, link, image_path, category, filename]
        info_select = info_tab[1].item(item, "values")

        for name, tag in zip(filename_name, filename_tag):
            if name == info_select[7]:
                info_select += (tag,)
                break

        load_and_display_image(info_select[6])

        history_tag = [info_select[0], info_select[7]]
        read_file(["history.json"], history_table, history_tag)

    else:
        info_select = ()
        is_select = False

    return info_select

info_history_select = ()

def his_select(event):
    global info_history_select
    if history_table.selection():
        item = history_table.selection()[0]
        info_history_select = history_table.item(item, "values")
    else:
        info_history_select = ()




# GUI 생성
root = tk.Tk()
root.geometry('1050x600')
root.resizable(False, False)

root.title("620-1 장비 수불 대장")
root.wm_iconbitmap('title.ico')

style = ttk.Style(root)


root.tk.call("source", 'azure.tcl')
root.tk.call("set_theme", 'dark')
root.option_add("*Font", ("나눔고딕", 12))

configure_styles()

# 왼쪽 프레임 생성
left_frame = ttk.Frame(root)
left_frame.pack(side="left", fill="y")

# 탭 생성
tab_control = ttk.Notebook(left_frame)
tab_control.pack(side="top", fill="y", expand="True", padx=10, pady=10)

# 전체 탭 생성
total_tab = ttk.Frame(tab_control)
tab_control.add(total_tab, text="전체")

# 센서 탭 생성
sensor_tab = ttk.Frame(tab_control)
tab_control.add(sensor_tab, text="센서")

# 케이블 탭 생성
cable_tab = ttk.Frame(tab_control)
tab_control.add(cable_tab, text="케이블")

# 표 생성
columns_tag = ("이름", "총 갯수", "사용중", "보관중", "태그")
tree_total = create_table(total_tab, columns_tag)
tree_sensor = create_table(sensor_tab, columns_tag)
tree_cable = create_table(cable_tab, columns_tag)

tree_tag = [tree_total, tree_sensor, tree_cable]

# 검색 엔트리와 검색 버튼 생성
search_frame = ttk.Frame(left_frame)
search_frame.pack(side="bottom", fill="x", padx=10)

search_entry = ttk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

confirm_frame = ttk.Frame(search_frame)
confirm_frame.pack(side="bottom", fill="x", padx=10, pady=10)

search_button = ttk.Button(confirm_frame, text="검색", width=5, command=search_event)
search_button.grid(row=0, column=0, padx=5)

# 등록 버튼 생성
register_button = ttk.Button(confirm_frame, text="등록", width=5, command=register_item)
register_button.grid(row=0, column=1, padx=5)

modify_button = ttk.Button(confirm_frame, text="데이터 수정", command=change_form)
modify_button.grid(row=0, column=2, padx=5)


# 오른쪽 프레임 생성
right_frame = ttk.Frame(root)
right_frame.pack(side="right", fill="x", expand=True)

#style.configure('White.TFrame', background='white')
image_frame = ttk.Frame(right_frame)
image_frame.pack(side="top", fill="both", expand=True)

edit_frame = ttk.Frame(right_frame)
edit_frame.pack(fill="x", padx=10, pady=10)

historyDel_button = ttk.Button(edit_frame, text="기록 삭제", command=del_history_date)
historyDel_button.pack(side="right", padx=10)

historyAdd_button = ttk.Button(edit_frame, text="기록 추가", command=history_item)
historyAdd_button.pack(side="right", padx=10)

log_frame = ttk.Frame(right_frame, borderwidth=2, relief="groove")
log_frame.pack(side="bottom", fill="both", padx=10, pady=0)

# Enter 키를 눌렀을 때도 검색 수행하도록 바인딩
search_entry.bind("<Return>", search_event)

# 탭 변경 이벤트 바인딩
tab_control.bind("<<NotebookTabChanged>>", switch_tab)

# 링크를 더블 클릭하여 해당 링크 열기
tree_total.bind("<Double-1>", open_link)
tree_sensor.bind("<Double-1>", open_link)
tree_cable.bind("<Double-1>", open_link)

# 선택 이벤트 처리
tree_total.bind("<<TreeviewSelect>>", tab_select)
tree_sensor.bind("<<TreeviewSelect>>", tab_select)
tree_cable.bind("<<TreeviewSelect>>", tab_select)

# 초기 데이터 로드
switch_tab()
load_and_display_image("")

test = []
test.append("history.json")

# Set a minsize for the window, and place it in the middle
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

root.mainloop()