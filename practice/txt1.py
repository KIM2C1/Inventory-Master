def data_check(entries, user_data):
        global quantity_entry, item_type

        item_value = ["센서", "케이블"]
        empty_entries = []

        for entry, value in zip(entries, user_data):
            if not value or value in error_tag:
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

        return empty_entries