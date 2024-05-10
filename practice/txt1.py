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

        # 폼 중앙 정렬 오류 수정해야함 

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    register_window
    change_window
    history_window


    def register_item():
    global form_state, register_window

    if form_state[0]:
        print("is opened!")
        return

    form_state[0] = 1
    
    register_window = tk.Toplevel(root)
    register_window.title("아이템 등록")
    register_window.geometry("360x335")
    register_window.resizable(False, False)
    center_window(register_window)
    register_window.protocol("WM_DELETE_WINDOW", lambda: window_state(0))