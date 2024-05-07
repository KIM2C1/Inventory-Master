def read_file1(filename, tree=None, tag=None):
    global history_taghistory_tag

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
            for index, item in enumerate(loaded_data):
                if tag[0] == item["아이템"]:
                    values = [item[name] for name in history_tag]
                    tree.insert('', 'end', values=values)

        elif tree and tag:
            for index, item in enumerate(loaded_data):
                if all (name in item for name in tag):
                    values = [item[name] for name in tag] 
                    values.insert(3, int(item["총 갯수"]) - int(item["사용중"]))
                    tree.insert('', 'end', values=values)
                else:
                    print(f"Invalid data format in file '{item}': Missing tag.")
        else:
            print()

item_tag = ["이름", "총 갯수", "사용중", "태그", "링크", "이미지주소", "카테고리"]

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