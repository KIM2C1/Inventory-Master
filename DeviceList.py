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
import datetime

#global var
history_table = ""
item_tag = ["이름", "총 갯수", "사용중", "태그", "링크", "이미지주소", "카테고리"]
history_tag = ["아이템", "사용자", "갯수", "사용 날짜", "아이디", "카테고리"]
history_find_tag = ["아이템", "카테고리"]
filename_tag = ["sensor.json", "cable.json"]
filename_name = ["센서", "케이블"]
is_select = [False, False]

history_window = None 
register_window = None
change_window = None

# 폼 별로 이름 불리 해야함!!!!!!!!!!
name_entry, quantity_entry, item_type, date_entry = None, None, None, None

def show_error_message():
    root = tk.Tk() 
    root.withdraw()
    tkinter.messagebox.showwarning("Warring!", "아이템을 선택 해주세요!")
    root.destroy()  

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


    def tree_insert(tree, data):
        for index, item in enumerate(data):
            if all (name in item for name in tag):
                values = [item[name] for name in tag] 
                values.insert(3, int(item["총 갯수"]) - int(item["사용중"]))
                tree.insert('', 'end', values=values)
            else:
                print(f"Invalid data format in file '{item}': Missing tag.")
    
    for name_tag in filename:
        try:
            with open(name_tag, "r", encoding="utf-8") as file:
                loaded_data = json.load(file)
            if not loaded_data:
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
                    tree.insert('', 'end', values=values[1:])

        elif tree and tag:
            if not Check:
                tree.delete(*tree.get_children())
                Check = True

            if tree == tree_total:
                for name_tag in filename:
                    with open(name_tag, "r", encoding="utf-8") as file:
                        buff = json.load(file)
                    if buff:
                        tree_insert(tree, loaded_data)
                        break
            else:
                if loaded_data:    
                    tree_insert(tree, loaded_data)
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

def dump_data(filename, data, tag):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=len(tag))
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

def relaod_data(filename, tree):
    global last_selected_id

    read_file(filename, tree, item_tag)

    for child in tree.get_children():
        if tree.item(child, "values")[0] == last_selected_id:
            tree.selection_set(child)
            break

def save_history_date(tree):
    info_select = item_select()

    write_file("history.json", tree, history_tag)

    original_data = read_file([info_select[8]])

    for index in range(len(original_data)):
        if original_data[index]['이름'] == tree[0]:
            original_data[index]['사용중'] = int(original_data[index]['사용중']) + int(tree[2])

    dump_data(info_select[8], original_data, item_tag)

def del_history_data():
    global info_history_select, item_tag, history_tag

    info_tab = tab_index()
    info_select = item_select()

    if not is_select[1]:
        show_error_message()
        return

    original_tab_data = read_file([info_select[8]])

    for index in range(len(original_tab_data)):
        if original_tab_data[index]['이름'] == info_select[0]:
            original_tab_data[index]['사용중'] = int(original_tab_data[index]['사용중']) - int(info_history_select[1])

    dump_data(info_select[8], original_tab_data, item_tag)

    original_his_data = read_file(["history.json"])

    new_data = [entry for entry in original_his_data if not (entry['사용자'] == info_history_select[0] and entry['갯수'] == info_history_select[1] and entry['사용 날짜'] == info_history_select[2] and entry['아이디'] == info_history_select[3])]

    dump_data("history.json", new_data, history_tag)

    relaod_data(info_tab[0], info_tab[1])

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

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def on_focus_in(event):
    if event.widget.get() in error_tag:
        event.widget.delete(0, 'end')
        event.widget.config(foreground="white")

error_tag = ["필수항목", "잘못된 데이터", "양수를 입력하시오", "양수가 아니거나 재고 부족", "YYYY-MM-DD", "중복된 이름"]
def data_check(entries, user_data, filename = None, discount=None):
        global quantity_entry, item_type, date_entry

        info_select = item_select()
        print(info_select)
        if info_select:
            print("TRUE")
        else:
            print("ELSE")

        item_value = ["센서", "케이블"]
        empty_entries = []

        def check_name(data, value, entry):
            for item in data:
                if item["이름"] == value:
                    #print("중복된 이름!!!!!")
                    empty_entries.append(entry)
                    entry.delete(0, 'end')
                    entry.insert(0, "중복된 이름")
                    entry.config(foreground="red")
            return False

        for entry, value in zip(entries, user_data):
            if (not value or value in error_tag) and entry not in [quantity_entry, item_type, date_entry]:
                empty_entries.append(entry)
                entry.delete(0, 'end')
                entry.insert(0, "필수항목")
                entry.config(foreground="red")

            if entry == name_entry:
                try:
                    load_data = read_file([filename])
                    #데이터 수정인 경우
                    if info_select:
                        if info_select[0] != value:
                            print()
                            check_name(load_data, value, entry)
                    #데이터 등록인 경우
                    else:
                        print()
                        check_name(load_data, value, entry)
                except:
                    pass

            if entry == quantity_entry:
                try:
                    is_negative = (discount and ((int(discount) - int(value) < 0) or (int(value) <= 0))) or (not discount and int(value) < 0)
                    if is_negative:
                        raise ValueError
                    
                except ValueError:
                    entry.delete(0, 'end')
                    entry.insert(0, "양수가 아니거나 재고 부족")
                    entry.config(foreground="red")
                    empty_entries.append(entry)

            if entry == item_type and value not in item_value:
                empty_entries.append(entry)
                item_type.delete(0, 'end')
                item_type.insert(0, "잘못된 데이터")
                item_type.config(foreground="red")

            if entry == date_entry or value not in value:
                try:
                    datetime.datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    empty_entries.append(entry)
                    date_entry.delete(0, 'end')
                    date_entry.insert(0, "YYYY-MM-DD")
                    date_entry.config(foreground="red")

        return empty_entries

#등록 폼
def register_item():
    global form_state, register_window
    global name_entry, quantity_entry, item_type

    if form_state[0]:
        register_window.lift()
        return

    form_state[0] = True
    
    info_tab = tab_index()

    for item in info_tab[1].selection():
        info_tab[1].selection_remove(item)

    register_window = tk.Toplevel(root)
    register_window.title("아이템 등록")
    register_window.geometry("360x335")
    register_window.resizable(False, False)
    center_window(register_window)
    register_window.protocol("WM_DELETE_WINDOW", lambda: window_state(0, register_window))

    # 폼 생성
    form_frame = ttk.Frame(register_window)
    form_frame.pack(padx=10, pady=10)
    
    # 이름 입력
    ttk.Label(form_frame, text="이름:").grid(row=0, column=0, sticky="w", pady=10)
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=10)

    # 갯수 입력
    ttk.Label(form_frame, text="갯수:").grid(row=1, column=0, sticky="w", pady=10)
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=1, column=1)

    # 태그 입력
    ttk.Label(form_frame, text="태그:").grid(row=2, column=0, sticky="w", pady=10)
    tag_entry = ttk.Entry(form_frame)
    tag_entry.grid(row=2, column=1)

    # 링크 입력
    ttk.Label(form_frame, text="링크:").grid(row=3, column=0, sticky="w", pady=10)
    link_entry = ttk.Entry(form_frame)
    link_entry.grid(row=3, column=1)

    # 이미지 주소 입력
    ttk.Label(form_frame, text="이미지 주소:").grid(row=4, column=0, sticky="w", pady=10)
    imagePath_entry = ttk.Entry(form_frame)
    imagePath_entry.grid(row=4, column=1)

    # 아이템 타입 선택
    ttk.Label(form_frame, text="아이템 타입:").grid(row=5, column=0, sticky="w", pady=10)
    item_type = ttk.Combobox(form_frame, values=["센서", "케이블"])
    item_type.grid(row=5, column=1)

    entries = [name_entry, quantity_entry, tag_entry, link_entry, imagePath_entry, item_type]
    
    def handle_register():
        global item_tag, filename_name, tree_tag, filename_tag

        # 각 항목의 값을 가져옴
        name = name_entry.get()
        quantity = quantity_entry.get()
        tag = tag_entry.get()
        link = link_entry.get()
        imagePath = imagePath_entry.get()
        item = item_type.get()
    
        values = [name, quantity, tag, link, imagePath, item]
        
        filename = None

        for index, value in enumerate(filename_name):
            if value == item:
                filename = filename_tag[index]

        #데이터 무결성 검사
        if data_check(entries, values, filename):
            return
        else:
            for index, value in enumerate(filename_name):
                if item == value:
                    new_data = (name, quantity, 0, tag, link, imagePath, item)
                    tree_tag[index].insert('', 'end', values=new_data)
                    write_file(filename_tag[index], new_data, item_tag)
                    read_file([filename_tag[index]], tree_tag[index], item_tag)
              

            window_state(0, register_window)
            read_file(info_tab[0], info_tab[1], item_tag)

    for entry in entries:
        entry.bind("<FocusIn>", on_focus_in)

    # 등록 버튼 생성
    register_button = ttk.Button(form_frame, text="등록", command=handle_register)
    register_button.grid(row=6, columnspan=2, padx=(40,0), pady=20)

#데이터 수정 폼
def change_form():
    global filename_tag, filename_name, change_window
    global name_entry, quantity_entry, item_type
    
    if not is_select[0]:
        show_error_message()
        return
    elif form_state[1]:
        change_window.lift()
        return
    
    form_state[1] = True

    info_select = item_select()
    info_tab = tab_index()

    change_window = tk.Toplevel(root)
    change_window.title("데이터 수정")
    change_window.geometry("340x325")
    change_window.resizable(False, False)
    center_window(change_window)
    change_window.protocol("WM_DELETE_WINDOW", lambda: window_state(1, change_window))

    form_frame = ttk.Frame(change_window)
    form_frame.pack(padx=10, pady=10)

    # 이름 입력
    ttk.Label(form_frame, text="이름:").grid(row=0, column=0, sticky="w", pady=10)
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=10)
    name_entry.insert(0, info_select[0])

    # 갯수 입력
    ttk.Label(form_frame, text="총 갯수:").grid(row=1, column=0, sticky="w", pady=10)
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=1, column=1)
    quantity_entry.insert(0, info_select[1])

    # 링크 입력
    ttk.Label(form_frame, text="태그:").grid(row=2, column=0, sticky="w", pady=10)
    link_entry = ttk.Entry(form_frame)
    link_entry.grid(row=2, column=1)
    link_entry.insert(0, info_select[4])

    # 태그 입력
    ttk.Label(form_frame, text="링크:").grid(row=3, column=0, sticky="w", pady=10)
    tag_entry = ttk.Entry(form_frame)
    tag_entry.grid(row=3, column=1)
    tag_entry.insert(0, info_select[5])

    # 이미지 주소 입력
    ttk.Label(form_frame, text="이미지 주소:").grid(row=4, column=0, sticky="w", pady=10)
    imagePath_entry = ttk.Entry(form_frame)
    imagePath_entry.grid(row=4, column=1)
    imagePath_entry.insert(0, info_select[6])

    # 아이템 타입 선택
    ttk.Label(form_frame, text="아이템 타입:").grid(row=5, column=0, sticky="w", pady=10)
    item_type = ttk.Combobox(form_frame, values=["센서", "케이블"])
    item_type.grid(row=5, column=1)
    item_type.set(info_select[7])

    buttom_frame = ttk.Frame(form_frame)
    buttom_frame.grid(row=6, column=1, pady=10, padx=(0, 20))

    entries = [name_entry, quantity_entry, tag_entry, link_entry, imagePath_entry, item_type]

    def change_data():
        name = name_entry.get()
        quantity = quantity_entry.get()
        tag = tag_entry.get()
        link = link_entry.get()
        imagePath = imagePath_entry.get()
        item = item_type.get()

        values = [name, quantity, tag, link, imagePath, item]

        filename = None

        for index, value in enumerate(filename_name):
            if value == item:
                filename = filename_tag[index]

        #데이터 무결성 검사
        if data_check(entries, values, filename):
            return
        else:

            original_data = read_file([info_select[8]])

            for i in range(len(original_data)):
                if original_data[i]['이름'] == info_select[0]:
                    #카테고리가 변경된 경우
                    if original_data[i]['카테고리'] != item:
                        remove_data = [entry for entry in original_data if not (entry['이름'] == info_select[0])]
                        dump_data(info_select[8], remove_data, item_tag)

                        #변경된 카테고리로 부터 파일의 이름 추출
                        filename = filename_tag[filename_name.index(item)] if item in filename_name else None

                        change_data = read_file([filename])

                        change_data.append({
                            "이름": name,
                            "총 갯수": quantity,
                            "사용중": info_select[2],
                            "태그": tag,
                            "링크": link,
                            "이미지주소": imagePath,
                            "카테고리": item
                        })

                        dump_data(filename, change_data, item_tag)

                    else:
                        original_data[i]['이름'] = name
                        original_data[i]['총 갯수'] = quantity
                        original_data[i]['사용중'] = info_select[2]
                        original_data[i]['태그'] = tag
                        original_data[i]['링크'] = link
                        original_data[i]['이미지주소'] = imagePath
                        original_data[i]['카테고리'] = item

                        dump_data(info_select[8], original_data, item_tag)

            window_state(1, change_window)
            history_table.delete(*history_table.get_children())
            read_file(info_tab[0], info_tab[1], item_tag)

    def delete_data():
        original_data = read_file([info_select[8]])
        
        for i in range(len(original_data)):
            if original_data[i]['이름'] == info_select[0]:
                new_data = [entry for entry in original_data if not (entry['이름'] == info_select[0])]
                dump_data(info_select[8], new_data, item_tag)

        read_file(info_tab[0], info_tab[1], item_tag)
        window_state(1, change_window)

    for entry in entries:
        entry.bind("<FocusIn>", on_focus_in)

    #변경 버튼
    change_button = ttk.Button(buttom_frame, width=5, text="변경", command=change_data)
    change_button.pack(side="left", padx=(0, 5))

    #삭제 버튼
    delete_button = ttk.Button(buttom_frame, width=5, text="삭제", command=delete_data)
    delete_button.pack(side="left")

#기록 추가 폼
def history_item():
    global form_state, is_select, history_window, history_table, quantity_entry, date_entry, history_window

    info_select = item_select()
    info_tab = tab_index()

    if not is_select[0]:
        show_error_message()
        return
    elif form_state[2]:
        history_window.lift()
        return

    form_state[2] = True

    history_window = tk.Toplevel(root)
    history_window.title("히스토리 추가")
    history_window.geometry("360x300")
    history_window.resizable(False, False)
    center_window(history_window)
    history_window.protocol("WM_DELETE_WINDOW", lambda: window_state(2, history_window))

    form_frame = ttk.Frame(history_window)
    form_frame.pack(padx=10, pady=10)

    ttk.Label(form_frame, text="아이템:").grid(row=0, column=0, sticky="w", pady=10)
    item_label = ttk.Label(form_frame, text=str(info_select[0]))
    item_label.grid(row=0, column=1, padx=10)

    ttk.Label(form_frame, text="사용자:").grid(row=1, column=0, sticky="w", pady=10)
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=1, column=1)

    ttk.Label(form_frame, text="갯수:").grid(row=2, column=0, sticky="w", pady=10)
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=2, column=1)

    ttk.Label(form_frame, text="아이템 타입:").grid(row=3, column=0, sticky="w", pady=10)
    item_type = ttk.Label(form_frame, text=str(info_select[7]))
    item_type.grid(row=3, column=1)

    ttk.Label(form_frame, text="사용 날짜:").grid(row=4, column=0, sticky="w", pady=10)
    date_entry = ttk.Entry(form_frame)
    date_entry.grid(row=4, column=1)

    current_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d", current_time)

    date_entry.insert(0, str(formatted_time))

    entries = [name_entry, quantity_entry, date_entry]

    def handle_history():
        item = str(info_select[0])
        name = name_entry.get()
        quantity = quantity_entry.get()
        date = date_entry.get()
        category = str(info_select[7])

        values = [name, quantity, date]

        #데이터 무결성 검사
        if data_check(entries, values, None, info_select[3]):
            return
        else:
            uuid = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            new_data = (item, name, quantity, date, uuid, category)
            tree_data = new_data[1:]
            history_table.insert('', 'end', values=tree_data)
            save_history_date(new_data)
            window_state(2, history_window)
            relaod_data(info_tab[0], info_tab[1])


    for entry in entries:
        entry.bind("<FocusIn>", on_focus_in)

    register_button = ttk.Button(form_frame, text="등록", command=handle_history)
    register_button.grid(row=5, columnspan=2, padx=(40, 0), pady=20)

#폼 상태 = [등록 폼, 데이터 수정 폼, 기록 추가 폼]
form_state = [False, False, False]

def window_state(index, window):
    global form_state
    #form_index = {register_window, change_window, history_window}
    if form_state[index] == True:
        form_state[index] = False
        window.destroy()
    else:
        pass
            
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
            history_table = ttk.Treeview(log_frame, columns=("사용자", "갯수", "사용 날짜", "아이디"), show="headings")
            history_table.heading("사용자", text="사용자")
            history_table.heading("갯수", text="갯수")
            history_table.heading("사용 날짜", text="사용 날짜")
            history_table.heading("아이디", text="아이디")
            history_table.column("사용자", width=100, anchor="center")
            history_table.column("갯수", width=70, anchor="center")
            history_table.column("사용 날짜", width=100, anchor="center")
            history_table.column("아이디", width=0, anchor="center", stretch=False)
            history_table.pack(side='left',fill='x')

            scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=history_table.yview)
            scrollbar.pack(side='right', fill='y')
            history_table.configure(yscroll=scrollbar.set)
            history_table.bind("<<TreeviewSelect>>", history_select)
            #text_label = ttk.Label(log_frame, text="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", width=width)
            #text_label.pack(fill='x')
            load_and_display_image.history_table = history_table  # Store the label for reuse
    except requests.RequestException as e:
        print(f"Error loading image: {e}")

last_selected_id = None

def item_select(event=None):
    global is_select, last_selected_id
    global filename_tag, filename_name, history_table


    info_tab = tab_index()

    if info_tab[1].selection():
        is_select[0] = True
        item = info_tab[1].selection()[0]
        last_selected_id = info_tab[1].item(item, "values")[0]

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
        is_select[0] = False
        last_selected_id = None

    return info_select

info_history_select = ()

def history_select(event):
    global info_history_select, is_select

    if history_table.selection():
        is_select[1] = True
        item = history_table.selection()[0]
        info_history_select = history_table.item(item, "values")
        print(info_history_select)
    else:
        info_history_select = ()
        is_select[1] = False

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

historyDel_button = ttk.Button(edit_frame, text="기록 삭제", command=del_history_data)
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
tree_total.bind("<<TreeviewSelect>>", item_select)
tree_sensor.bind("<<TreeviewSelect>>", item_select)
tree_cable.bind("<<TreeviewSelect>>", item_select)

# 초기 데이터 로드
switch_tab()
load_and_display_image("")

test = []
test.append("history.json")

# Set a minsize for the window, and place it in the middle
root.update()
root.minsize(root.winfo_width(), root.winfo_height()) #최소 크기 지정
center_window(root)

root.mainloop()