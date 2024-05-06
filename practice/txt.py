import tkinter as tk
from tkinter import ttk

def create_scrolled_table(root):
    # Create a frame for the table and scrollbar
    frame = ttk.Frame(root)
    frame.pack(fill='both', expand=True)

    # Define the columns for the Treeview
    columns = ('name', 'age', 'job')
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    
    # Define headings
    tree.heading('name', text='Name')
    tree.heading('age', text='Age')
    tree.heading('job', text='Job')

    # Inserting some sample data
    tree.insert('', 'end', values=('Alice', 30, 'Engineer'))
    tree.insert('', 'end', values=('Bob', 25, 'Designer'))
    tree.insert('', 'end', values=('Cathy', 35, 'Manager'))

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    # Layout
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

root = tk.Tk()
create_scrolled_table(root)
root.mainloop()
