import tkinter as tk #GUI
import json                                                                                                                                     
import os
import re
from datetime import datetime

class StickyNote:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() #not show in taskbar 
        self.window = tk.Toplevel(self.root) #create a subwindow as app
        self.window.overrideredirect(True) #not show caption bar
        self.window.lower() #only show on desktop 

        # UI color
        self.bg_color = "#FFF9C4"       
        self.sub_bg_color = "#FFF59D"   
        self.drag_color = "#FFE082"     
        self.text_color = "#333333"     
        self.icon_color = "#757575"     
        self.font = ("Segoe UI", 11)            
        self.window.configure(bg=self.bg_color)
        
        #initial setup
        self.is_locked = False
        self.save_file = "appdata.json" 
        self.dragged_row = None 

        #control tool
        self.title_bar = tk.Frame(self.window, bg=self.bg_color, relief="flat", bd=0)
        self.title_bar.pack(fill=tk.X, pady=(2, 0))

        self.close_btn = self.create_btn(self.title_bar, "✖", self.root.destroy)
        self.close_btn.pack(side=tk.RIGHT, padx=5)

        self.lock_btn = self.create_btn(self.title_bar, "🔓", self.toggle_lock)
        self.lock_btn.pack(side=tk.RIGHT, padx=2)

        self.clear_btn = self.create_btn(self.title_bar, "🗑", self.clear_all)
        self.clear_btn.config(font=("Segoe UI Symbol", 13, "bold"), fg="#555555")
        self.clear_btn.pack(side=tk.RIGHT, padx=2)

        self.list_frame = tk.Frame(self.window, bg=self.bg_color)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.grip = tk.Label(self.window, text="⇲", bg=self.bg_color, fg=self.icon_color, cursor="size_nw_se")
        self.grip.place(relx=1.0, rely=1.0, anchor="se")

        # detect mouse
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_bar.bind("<ButtonRelease-1>", lambda e: self.save_data())
        
        self.grip.bind("<Button-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.do_resize)
        self.grip.bind("<ButtonRelease-1>", lambda e: self.save_data())

        self.load_data()

    def create_btn(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg=self.bg_color, fg=self.icon_color, 
                        borderwidth=0, activebackground=self.sub_bg_color, 
                        font=("Segoe UI Symbol", 10), command=command, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=self.sub_bg_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.bg_color))
        return btn

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        self.close_btn.pack_forget()
        self.lock_btn.pack_forget()
        self.clear_btn.pack_forget()

        if self.is_locked:  #if lock not show close button
            self.lock_btn.config(text="🔒", fg="#d9534f")
            self.grip.place_forget() 
            self.lock_btn.pack(side=tk.RIGHT, padx=2)
            self.clear_btn.pack(side=tk.RIGHT, padx=2)
        else: #show all the button
            self.lock_btn.config(text="🔓", fg=self.icon_color)
            self.grip.place(relx=1.0, rely=1.0, anchor="se")
            self.close_btn.pack(side=tk.RIGHT, padx=5)
            self.lock_btn.pack(side=tk.RIGHT, padx=2)
            self.clear_btn.pack(side=tk.RIGHT, padx=2)
            
        self.save_data()

    def clear_all(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.add_row()
        self.save_data()

    def start_drag_row(self, event, container):
        self.dragged_row = container
        self.set_row_highlight(container, True)

    def do_drag_row(self, event):
        if self.dragged_row is None: return
        
        current_y = self.window.winfo_pointery()
        
        for child in self.list_frame.winfo_children():
            if child != self.dragged_row:
                child_y = child.winfo_rooty()
                child_h = child.winfo_height()
                
                if child_y <= current_y <= child_y + child_h:
                    if current_y < child_y + child_h / 2:
                        self.dragged_row.pack(before=child)
                    else:
                        self.dragged_row.pack(after=child)
                    break 

    def stop_drag_row(self, event):
        if self.dragged_row is None: return
        self.set_row_highlight(self.dragged_row, False)
        self.dragged_row = None 
        self.save_data()        

    def set_row_highlight(self, container, is_highlight):
        color = self.drag_color if is_highlight else self.bg_color
        container.row_frame.config(bg=color)
        container.drag_handle.config(bg=color)
        container.right_frame.config(bg=color)
        container.entry.config(bg=color)
        container.date_entry.config(bg=color)
        container.del_btn.config(bg=color)
        container.add_btn.config(bg=color)
        container.date_btn.config(bg=color)

    def start_move(self, event):
        if self.is_locked: return
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        if self.is_locked: return
        x = self.window.winfo_x() + (event.x - self.x)
        y = self.window.winfo_y() + (event.y - self.y)
        self.window.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        if self.is_locked: return
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.start_width = self.window.winfo_width()
        self.start_height = self.window.winfo_height()

    def do_resize(self, event):
        if self.is_locked: return
        new_width = max(250, self.start_width + (event.x_root - self.resize_start_x))
        new_height = max(150, self.start_height + (event.y_root - self.resize_start_y))
        self.window.geometry(f"{new_width}x{new_height}")

    def add_row(self, main_text="", sub_text="", is_sub_open=False, date_text="", insert_after=None):
        item_container = tk.Frame(self.list_frame, bg=self.bg_color)
        
        if insert_after:
            item_container.pack(after=insert_after, fill=tk.X, pady=2)
        else:
            item_container.pack(fill=tk.X, pady=2)

        row_frame = tk.Frame(item_container, bg=self.bg_color)
        row_frame.pack(fill=tk.X)

        drag_handle = tk.Label(row_frame, text="☰ ", bg=self.bg_color, fg="#BDBDBD", font=self.font, cursor="sb_v_double_arrow")
        drag_handle.pack(side=tk.LEFT)
        drag_handle.bind("<Button-1>", lambda e: self.start_drag_row(e, item_container))
        drag_handle.bind("<B1-Motion>", self.do_drag_row) 
        drag_handle.bind("<ButtonRelease-1>", self.stop_drag_row)

        right_frame = tk.Frame(row_frame, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT)

        del_btn = self.create_btn(right_frame, "囗", lambda: self.delete_row(item_container))
        del_btn.pack(side=tk.RIGHT)

        add_btn = self.create_btn(right_frame, "✚", lambda: self.toggle_subnote(item_container))
        add_btn.pack(side=tk.RIGHT)

        date_btn = self.create_btn(right_frame, "📅", lambda: self.toggle_date(item_container))
        date_btn.pack(side=tk.RIGHT)

        date_entry = tk.Entry(right_frame, bg=self.bg_color, fg="#d9534f", bd=0, font=("Segoe UI", 9, "bold"), width=15, justify="right")
        if date_text:
            date_entry.insert(0, date_text)
            date_entry.pack(side=tk.RIGHT, padx=2)

        entry = tk.Entry(row_frame, bg=self.bg_color, fg=self.text_color, bd=0, font=self.font, highlightthickness=0)
        entry.insert(0, main_text)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        sub_frame = tk.Frame(item_container, bg=self.bg_color)
        sub_text_widget = tk.Text(sub_frame, bg=self.sub_bg_color, fg=self.text_color, bd=0, 
                                  font=("Segoe UI", 10), height=3, padx=5, pady=5)
        sub_text_widget.insert("1.0", sub_text)
        sub_text_widget.pack(fill=tk.BOTH, padx=(25, 0), pady=(2, 0))

        item_container.row_frame = row_frame
        item_container.right_frame = right_frame
        item_container.drag_handle = drag_handle
        item_container.entry = entry
        item_container.sub_frame = sub_frame
        item_container.sub_text = sub_text_widget
        item_container.del_btn = del_btn
        item_container.add_btn = add_btn
        item_container.date_btn = date_btn
        item_container.is_sub_open = is_sub_open
        item_container.date_entry = date_entry 

        if is_sub_open:
            sub_frame.pack(fill=tk.X)
            add_btn.config(text="━")

        entry.bind("<Return>", lambda e: self.on_enter_pressed(item_container))
        entry.bind("<KeyRelease>", lambda e: self.save_data())
        sub_text_widget.bind("<KeyRelease>", lambda e: self.save_data())
        date_entry.bind("<KeyRelease>", lambda e, widget=date_entry: self.on_date_edited(widget))
        
        entry.focus_set()
        return item_container

    def toggle_date(self, item_container):
        if item_container.date_entry.winfo_ismapped():
            item_container.date_entry.pack_forget() 
            item_container.date_entry.delete(0, tk.END) 
        else:
            now = datetime.now()
            date_str = f"{now.year}/{now.month}/{now.day}({now.strftime('%a')})"
            item_container.date_entry.insert(0, date_str)
            item_container.date_entry.pack(side=tk.RIGHT, padx=2)
        self.save_data()

    def on_enter_pressed(self, current_container):
        self.add_row(insert_after=current_container)
        self.save_data()

    def delete_row(self, item_container):
        item_container.destroy()
        if len(self.list_frame.winfo_children()) == 0:
            self.add_row()
        self.save_data()

    def toggle_subnote(self, item_container):
        if item_container.is_sub_open:
            item_container.sub_frame.pack_forget()
            item_container.add_btn.config(text="+")
            item_container.is_sub_open = False
        else:
            item_container.sub_frame.pack(fill=tk.X)
            item_container.add_btn.config(text="-")
            item_container.is_sub_open = True
        self.save_data()
    
    def on_date_edited(self, date_entry):
        current_text = date_entry.get()

        match = re.match(r"^(\d{4}/\d{1,2}/\d{1,2})", current_text)
        
        if match:
            date_part = match.group(1)
            try:
                dt = datetime.strptime(date_part, "%Y/%m/%d")
                new_text = f"{date_part}({dt.strftime('%a')})"
                
                if current_text != new_text:
                    cursor_pos = date_entry.index(tk.INSERT)
                    
                    date_entry.delete(0, tk.END)
                    date_entry.insert(0, new_text)
                    
                    date_entry.icursor(cursor_pos)
            except ValueError:
                pass 

        self.save_data() 

    def save_data(self):
        items_data = []
        for child in self.list_frame.winfo_children():
            if hasattr(child, 'entry'): 
                items_data.append({
                    "main": child.entry.get(),
                    "sub": child.sub_text.get("1.0", tk.END).strip(),
                    "sub_open": child.is_sub_open,
                    "date": child.date_entry.get() if child.date_entry.winfo_ismapped() else ""
                })

        data = {
            "x": self.window.winfo_x(),
            "y": self.window.winfo_y(),
            "width": self.window.winfo_width(),
            "height": self.window.winfo_height(),
            "is_locked": self.is_locked,
            "items": items_data
        }
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                w = data.get('width', 350) 
                h = data.get('height', 300)
                x = data.get('x', 200)
                y = data.get('y', 200)
                self.window.geometry(f"{w}x{h}+{x}+{y}")
                
                self.is_locked = data.get('is_locked', False)
                if self.is_locked:
                    self.lock_btn.config(text="🔒", fg="#d9534f")
                    self.grip.place_forget() 
                    self.close_btn.pack_forget() 
                
                items = data.get('items', [])
                if items:
                    for item in items:
                        self.add_row(item.get("main", ""), item.get("sub", ""), item.get("sub_open", False), item.get("date", ""))
                else:
                    self.add_row()
        else:
            self.window.geometry("350x300+200+200")
            self.add_row()

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNote(root)
    root.mainloop()
