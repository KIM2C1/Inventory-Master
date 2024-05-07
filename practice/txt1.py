def tab_index():
    global filename_tag, tree_tag

    current_tab_index = tab_control.index(tab_control.select())
    current_tab_text = tab_control.tab(current_tab_index, "text")
    filename = []

    if current_tab_index == 0:
        filename = filename_tag[:]
    else:
        filename.append(filename_tag[current_tab_index - 1])

    #info[] = [filename, tree_var_name, tree_dp_name]
    info = [filename, tree_tag[current_tab_index], current_tab_text]

    return info


#select_date[] = [name, total_cnt, use_cnt, invente_cnt, tag, link, image_path, category]
select_data = info_tab[1].item(item, "values")

filename_tag = ["sensor.json", "cable.json"]
filename_name = ["센서", "케이블"]

#info_select[] = [name, total_cnt, use_cnt, invente_cnt, tag, link, image_path, category, filename]
info_select = on_select()
info_select[8]

#info_history_select = [User, cnt, date]
info_history_select = his_select()

history_table = ""
item_tag = ["이름", "총 갯수", "사용중", "태그", "링크", "이미지주소", "카테고리"]
history_tag = ["아이템", "사용자", "갯수", "사용 날짜", "카테고리"]
history_find_tag = ["아이템", "카테고리"]
filename_tag = ["sensor.json", "cable.json"]
filename_name = ["센서", "케이블"]
is_select = False