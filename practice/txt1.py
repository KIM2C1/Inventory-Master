def save_history_date(tree):
    global history_index

    filename_buff = ["sensor.json", "cable.json"]

    if history_index == "센서":
        filename = filename_buff[0]
    elif history_index == "케이블":
        filename = filename_buff[1]
    else:
        pass

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
            "사용 날짜": tree[3]
        })

    with open("history.json", "w", encoding="utf-8") as file:
        json.dump(history_data, file, ensure_ascii=False, indent=4)

    try:
        if os.path.getsize(filename) > 0:
            with open(filename, "r", encoding="utf-8") as file:
                tree_data = json.load(file) #트리 데이터중 현재 수정중인 데이터만 찾아야 함
        else:
            tree_data = []
    except FileNotFoundError:
        tree_data = []

    for i in range(len(tree_data)):
        if tree_data[i]['이름'] == tree[0]:
            
            tree_data[i]['사용중'] = int(tree_data[i]['사용중']) + int(tree[2])
            #print(int(tree_data[i]['갯수']))

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(tree_data, file, ensure_ascii=False, indent=6)

his_select_data = []