import tkinter as tk
import tkinter.messagebox
import webbrowser
import requests
import json
import time
import os
import datetime

from tkinter import ttk
from PIL import Image, ImageTk, ImageFont
from io import BytesIO

#공통 태그 선언
item_tag = ["이름", "총 갯수", "사용중", "태그", "링크", "이미지주소", "카테고리"]
history_tag = ["아이템", "사용자", "갯수", "사용 날짜", "아이디", "카테고리"]
treeview_name = ["센서", "케이블", "모터", "컨버터"]

filename_tag = ["data\sensor.json", "data\cable.json", "data\motor.json", "data\converter.json"]

#아이템을 선택 했는지 체크하는 변수
is_select = [False, False]

#폼 전역 변수 선언
history_window, register_window, change_window = None, None, None 

# 공통 entry 선언
name_entry, quantity_entry, item_type, date_entry = None, None, None, None

def configure_styles():
    #스타일 지정
    style.configure("Treeview", font=("나눔고딕", 12))
    style.configure("Treeview.Heading", font=("나눔고딕", 12))
    style.configure("Accentbutton", foreground='white')
    style.configure("Togglebutton", foreground='white')
    style.configure("TNotebook.Tab", font=("나눔고딕", 12))
    style.configure("TButton", font=("나눔고딕", 12))

def create_table(tab, columns):
    # 표를 만들고 형식 포맷 함수
    tree = ttk.Treeview(tab, columns=columns, show="headings") 
    for col in columns:
        tree.heading(col, text=col)
        if not col == "태그" and not col == "이름":
            tree.column(col, anchor='center', width=50, stretch=False)  # 중앙 정렬
        if col == '이름':
            tree.column(col, width=250, stretch=True)
        else:
            tree.column(col, stretch=False)
    tree.pack(side="left", fill="both", expand=True)

    return tree

"""JSON 데이터 관리 함수"""
def read_file(filename, tree=None, tag=None):
    #JSON 파일로 부터 데이터를 불러와 tree에 저장 또는 데이터 리턴 함수
    Check = False 
    #totla_tree인 경우 tree.delete를 한 번만 진행하기 위해서

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
    #JSON 파일에 데이터 추가 함수
    #1. 데이터 불러와 변수에 dic로 저장 2. 추가 데이터 변수에 추가 3. 변수를 기존 파일에 덮음 
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
    #데이터를 <추가>가 아닌 통째로 변경하는 함수 (받은 데이터가 dic인 경우)
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=len(tag))
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error writing to JSON file '{filename}': {e}")

def save_history_date(tree):
    #history JSON과 tree에 데이터 추가 함수
    info_select = item_select()

    write_file("history.json", tree, history_tag)

    original_data = read_file([info_select[8]])

    for index in range(len(original_data)):
        if original_data[index]['이름'] == tree[0]:
            original_data[index]['사용중'] = int(original_data[index]['사용중']) + int(tree[2])

    dump_data(info_select[8], original_data, item_tag)
"""JSON 데이터 관리 함수"""

"""서비스 함수"""
def show_error_message(message):
    #에러 메시지를 함수
    root = tk.Tk() 
    root.withdraw()
    tkinter.messagebox.showwarning("Warring!", message)
    root.destroy()  

error_tag = ["필수항목", "잘못된 데이터", "양수를 입력하시오", "양수가 아니거나 재고 부족", "YYYY-MM-DD", "중복된 이름"]
def data_check(entries, user_data, filename = None, discount=None):
    #데이터 무결성 검사 함수

    global quantity_entry, item_type, date_entry, treeview_name

    info_select = item_select()
    empty_entries = []

    def check_name(data, value, entry):
        #기존 데이터에서 중복된 데이터 검사 함수
        for item in data:
            if item["이름"] == value:
                empty_entries.append(entry)
                entry.delete(0, 'end')
                entry.insert(0, "중복된 이름")
                entry.config(foreground="red")
        return False
    
    for entry, value in zip(entries, user_data):
        #데이터가 없는 경우
        if (not value or value in error_tag) and entry not in [quantity_entry, item_type, date_entry]:
            empty_entries.append(entry)
            entry.delete(0, 'end')
            entry.insert(0, "필수항목")
            entry.config(foreground="red")

        elif entry == name_entry:
            #이름이 잘못된 경우
            try:
                load_data = read_file([filename])
                #데이터 수정인 경우
                if info_select:
                    if info_select[0] != value:
                        #이름이 변경된 경우
                        check_name(load_data, value, entry)

                #데이터 등록인 경우
                else:
                    check_name(load_data, value, entry)
            except:
                pass

        elif entry == quantity_entry:
            #갯수가 잘못된 경우
            try:
                is_negative = (discount and ((int(discount) - int(value) < 0) or (int(value) <= 0))) or (not discount and int(value) < 0)
                if is_negative:
                    raise ValueError
                
            except ValueError:
                entry.delete(0, 'end')
                entry.insert(0, "양수가 아니거나 재고 부족")
                entry.config(foreground="red")
                empty_entries.append(entry)

        elif entry == item_type and value not in treeview_name:
            #카테고리에 없는 경우
            empty_entries.append(entry)
            item_type.delete(0, 'end')
            item_type.insert(0, "잘못된 데이터")
            item_type.config(foreground="red")

        elif entry == date_entry or value not in value:
            #날짜 형식이 잘못된 경우
            try:
                datetime.datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                empty_entries.append(entry)
                date_entry.delete(0, 'end')
                date_entry.insert(0, "YYYY-MM-DD")
                date_entry.config(foreground="red")

        else:
            pass
    return empty_entries

def search_event(event=None):
    #검색 함수

    info_tab = tab_index()
    keyword = search_entry.get().strip()  

    def search_data(keyword):
        global item_tag

        try:
            Check = False
            data_found = False
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
                        data_found = True

            if not data_found:
                show_error_message("아이템이 없습니다!")
                read_file(info_tab[0], info_tab[1], item_tag)

        except FileNotFoundError:
            pass
        Check = False

    if keyword:
        search_data(keyword)
    else:
        read_file(info_tab[0], info_tab[1], item_tag)

def open_link(event):
    # 링크를 클릭할 때 웹 브라우저에서 해당 링크 여는 함수

    item = event.widget.selection()[0]
    link = event.widget.item(item, "values")[5]
    if link:
        webbrowser.open(link)

def load_and_display_image(url):
    #이미지 URL 검사 함수

    try:
        load_image_from_url(url)
    except requests.RequestException as e:
        load_image_from_url("https://i.ibb.co/whFbRQJ/empty-item.png")

def load_image_from_url(url):
    #이미지 로드 함수

    response = requests.get(url)
    response.raise_for_status()

    image_data = BytesIO(response.content)
    pil_image = Image.open(image_data)

    # 이미지의 크기를 조절합니다.
    pil_image.thumbnail((250, 250))
    tk_image = ImageTk.PhotoImage(pil_image)

    if hasattr(load_and_display_image, 'image_label'):
        load_and_display_image.image_label.config(image=tk_image)
        load_and_display_image.image_label.image = tk_image
    else:
        border_frame = ttk.Frame(image_frame, borderwidth=2, relief="groove")
        border_frame.pack(fill='both', padx=10, pady=(10, 0))

        image_label = ttk.Label(border_frame, image=tk_image)
        image_label.image = tk_image 
        image_label.pack(pady=(10, 10))
        load_and_display_image.image_label = image_label

    image_frame.update_idletasks()
"""서비스 함수"""

"""Bind 함수"""
def tab_index():
    #탭을 선택할 때 탭 관련 데이터 추출 함수
    #info_tab[] = 0. 파일이름 1. tree 변수 이름 2. tree 표시 이름(ex)전체, 센서....)
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

def switch_tab(event=None):
    #탭 변경 감지하는 함수
    #탭 변경시 탬 관련 데이터 추출후 tree에 데이터 리로드 및 스크롤바 업데이트
    info_tab = tab_index()
    
    read_file(info_tab[0], info_tab[1], item_tag)
    update_scrollbar(info_tab[1], info_tab[2])

last_selected_id = None
def item_select(event=None):
    #아이템 선택시 관련 데이터 추출
    #info_select[] = 0. 이름 1. 총 갯수 2. 사용중 3. 보관중 4. 태그 5. 링크 6. 이미지링크 7. 카테고리 8. 파일 이름

    global is_select, last_selected_id
    global filename_tag, treeview_name, history_table

    info_tab = tab_index()

    if info_tab[1].selection():
        is_select[0] = True
        item = info_tab[1].selection()[0]
        last_selected_id = info_tab[1].item(item, "values")[0]

        #info_select[] = [name, total_cnt, use_cnt, invente_cnt, tag, link, image_path, category, filename]
        info_select = info_tab[1].item(item, "values")
            
        for name, tag in zip(treeview_name, filename_tag):
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
    #사용기록 선택시 관련 데이터 추출 함수

    global info_history_select, is_select

    if history_table.selection():
        is_select[1] = True
        item = history_table.selection()[0]
        info_history_select = history_table.item(item, "values")
    else:
        info_history_select = ()
        is_select[1] = False

def on_focus_in(event):
    #entry에서 내용을 클릭했을때 처리하는 함수

    global error_tag

    if event.widget.get() in error_tag:
        event.widget.delete(0, 'end')
        event.widget.config(foreground="white")
"""Bind 함수"""

"""Tree 관리 함수"""
def center_window(window):
    #폼을 화면 중앙에 맞추는 함수

    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

#폼 상태 = [등록 폼, 데이터 수정 폼, 기록 추가 폼]
form_state = [False, False, False]
def window_state(index, window):
    #폼이 열려있는지 검사하는 함수

    global form_state
    #form_index = {register_window, change_window, history_window}
    if form_state[index] == True:
        form_state[index] = False
        window.destroy()
    else:
        pass

scrollbars = {}
def update_scrollbar(treeview, tab_name):
    #기존의 스크롤바를 지우고 다시 생성하는 함수

    global scrollbars

    if tab_name in scrollbars and scrollbars[tab_name]:
        scrollbars[tab_name].destroy()

    scrollbar = ttk.Scrollbar(treeview.master, orient='vertical', command=treeview.yview)
    scrollbar.pack(side='right', fill='y')
    treeview.configure(yscrollcommand=scrollbar.set)
    scrollbars[tab_name] = scrollbar

    for column in treeview["columns"]:
        treeview.column(column, width=100)
"""Tree 관리 함수"""

"""폼 함수"""
def relaod_data(filename, tree):
    #데이터 리로드 및 마지막 선택 항목 복구 함수
    global last_selected_id

    read_file(filename, tree, item_tag)

    for child in tree.get_children():
        if tree.item(child, "values")[0] == last_selected_id:
            tree.selection_set(child)
            break

def register_item():
    #아이템 등록 폼
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
    item_type = ttk.Combobox(form_frame, values=treeview_name)
    item_type.grid(row=5, column=1)

    entries = [name_entry, quantity_entry, tag_entry, link_entry, imagePath_entry, item_type]
    
    def handle_register():
        #등록 버튼
        global item_tag, treeview_name, tree_tag, filename_tag

        name = name_entry.get()
        quantity = quantity_entry.get()
        tag = tag_entry.get()
        link = link_entry.get()
        imagePath = imagePath_entry.get()
        item = item_type.get()
    
        values = [name, quantity, tag, link, imagePath, item]
        
        filename = None

        for index, value in enumerate(treeview_name):
            if value == item:
                filename = filename_tag[index]

        #데이터 무결성 검사
        if data_check(entries, values, filename):
            return
        else:
            for index, value in enumerate(treeview_name):
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

def change_form():
    #데이터 수정 폼

    global filename_tag, treeview_name, change_window
    global name_entry, quantity_entry, item_type
    
    if not is_select[0]:
        show_error_message("아이템을 선택 해주세요!")
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
    tag_entry = ttk.Entry(form_frame)
    tag_entry.grid(row=2, column=1)
    tag_entry.insert(0, info_select[4])
    
    # 태그 입력
    ttk.Label(form_frame, text="링크:").grid(row=3, column=0, sticky="w", pady=10)
    link_entry = ttk.Entry(form_frame)
    link_entry.grid(row=3, column=1)
    link_entry.insert(0, info_select[5])

    # 이미지 주소 입력
    ttk.Label(form_frame, text="이미지 주소:").grid(row=4, column=0, sticky="w", pady=10)
    imagePath_entry = ttk.Entry(form_frame)
    imagePath_entry.grid(row=4, column=1)
    imagePath_entry.insert(0, info_select[6])

    # 아이템 타입 선택
    ttk.Label(form_frame, text="아이템 타입:").grid(row=5, column=0, sticky="w", pady=10)
    item_type = ttk.Combobox(form_frame, values=treeview_name)
    item_type.grid(row=5, column=1)
    item_type.set(info_select[7])

    buttom_frame = ttk.Frame(form_frame)
    buttom_frame.grid(row=6, column=1, pady=10, padx=(0, 20))

    entries = [name_entry, quantity_entry, tag_entry, link_entry, imagePath_entry, item_type]

    def change_data():
        #변경 버튼

        name = name_entry.get()
        quantity = quantity_entry.get()
        tag = tag_entry.get()
        link = link_entry.get()
        imagePath = imagePath_entry.get()
        item = item_type.get()

        values = [name, quantity, tag, link, imagePath, item]

        filename = None

        for index, value in enumerate(treeview_name):
            if value == item:
                filename = filename_tag[index]

        #데이터 무결성 검사
        if data_check(entries, values, filename):
            return
        else:
            values = [name, quantity, info_select[2], tag, link, imagePath, item]
            original_data = read_file([info_select[8]])

            for i in range(len(original_data)):
                if original_data[i]['이름'] == info_select[0]:
                    #카테고리가 변경된 경우
                    if original_data[i]['카테고리'] != item:
                        remove_data = [entry for entry in original_data if not (entry['이름'] == info_select[0])]
                        dump_data(info_select[8], remove_data, item_tag)

                        #변경된 카테고리로 부터 파일의 이름 추출
                        filename = filename_tag[treeview_name.index(item)] if item in treeview_name else None

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
        #삭제 버튼

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

def history_item():
    #사용기록 추가 폼

    global form_state, is_select, history_window, history_table
    global quantity_entry, date_entry

    info_select = item_select()
    info_tab = tab_index()

    if not is_select[0]:
        show_error_message("아이템을 선택 해주세요!")
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
        #등록 버튼

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

def del_history_data():
    #사용 기록 삭제 함수
    global info_history_select, item_tag, history_tag

    info_tab = tab_index()
    info_select = item_select()

    if not is_select[1]:
        show_error_message("아이템을 선택 해주세요!")
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
"""폼 함수"""
            
#Main 함수 및 GUI 생성
root = tk.Tk()
root.geometry('1050x600')
root.resizable(False, False)

root.title("620-1 장비 수불 대장")
root.wm_iconbitmap('title.ico')

style = ttk.Style(root)

root.tk.call("source", "assets/azure.tcl")
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

# 모터 탭 생성
motor_tab = ttk.Frame(tab_control)
tab_control.add(motor_tab, text="모터")

# 컨버터 탭 생성
converter_tab = ttk.Frame(tab_control)
tab_control.add(converter_tab, text="컨버터")

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

# 표 생성
columns_tag = ("이름", "총 갯수", "사용중", "보관중", "태그")
tree_total = create_table(total_tab, columns_tag)
tree_sensor = create_table(sensor_tab, columns_tag)
tree_cable = create_table(cable_tab, columns_tag)
tree_motor = create_table(motor_tab, columns_tag)
tree_converter = create_table(converter_tab, columns_tag)

#tree 추가
tree_tag = [tree_total, tree_sensor, tree_cable, tree_motor, tree_converter]

#history_tree 선언
history_table = None

#history_table 추가
history_table = ttk.Treeview(log_frame, columns=("사용자", "갯수", "사용 날짜", "아이디"), show="headings")
history_table.heading("사용자", text="사용자")
history_table.heading("갯수", text="갯수")
history_table.heading("사용 날짜", text="사용 날짜")
history_table.heading("아이디", text="아이디")
history_table.column("사용자", width=100, anchor="center")
history_table.column("갯수", width=70, anchor="center")
history_table.column("사용 날짜", width=100, anchor="center")
history_table.column("아이디", width=0, anchor="center", stretch=False)
history_table.pack(side='left', fill='x')
scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=history_table.yview)
scrollbar.pack(side='right', fill='y')
history_table.configure(yscroll=scrollbar.set)

history_table.bind("<<TreeviewSelect>>", history_select)

# 바인드 설정
for tree in tree_tag:
    tree.bind("<Double-1>", open_link)
    tree.bind("<<TreeviewSelect>>", item_select)

# 초기 데이터 로드
load_and_display_image("")
switch_tab()

root.update()
root.minsize(root.winfo_width(), root.winfo_height()) 
center_window(root)
root.mainloop()