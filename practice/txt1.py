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