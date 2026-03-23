import tkinter as tk #GUI
import json                                                                                                                                     
import os
import re
import sys
import winreg
from tkinter import simpledialog
from datetime import datetime

class StickyNote:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() #not show in taskbar 
        self.window = tk.Toplevel(self.root) #create a subwindow as app
        self.window.overrideredirect(True) #not show caption bar
        self.window.lower() #only show on desktop 

        # UI color
        self.themes = [
            {"bg": "#FFF9C4", "sub": "#FFF59D", "drag": "#FFE082"}, 
            {"bg": "#E1F5FE", "sub": "#B3E5FC", "drag": "#81D4FA"}, 
            {"bg": "#FCE4EC", "sub": "#F8BBD0", "drag": "#F48FB1"}, 
            {"bg": "#E8F5E9", "sub": "#C8E6C9", "drag": "#A5D6A7"} 
        ]
        self.bg_color = self.themes[0]["bg"]
        self.sub_bg_color = self.themes[0]["sub"]
        self.drag_color = self.themes[0]["drag"]
        self.text_color = "#333333"     
        self.icon_color = "#757575"     
        self.font = ("Segoe UI", 11)            
        self.window.configure(bg=self.bg_color)
        
        #initial setup
        self.is_locked = False
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.save_file = os.path.join(base_dir, "appdata.json")
        self.dragged_row = None 

        self.current_group = "General"
        self.groups = {"General": {"theme_idx": 0, "items": []}}

        #control tool
        self.title_bar = tk.Frame(self.window, bg=self.bg_color, relief="flat", bd=0)
        self.title_bar.pack(fill=tk.X, pady=(2, 0))

        self.tab_frame = tk.Frame(self.title_bar, bg=self.bg_color)
        self.tab_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.control_frame = tk.Frame(self.title_bar, bg=self.bg_color)
        self.control_frame.pack(side=tk.RIGHT)

        self.close_btn = self.create_btn(self.control_frame, "✖", self.root.destroy)
        self.close_btn.pack(side=tk.RIGHT, padx=5)

        self.lock_btn = self.create_btn(self.control_frame, "🔓", self.toggle_lock)
        self.lock_btn.pack(side=tk.RIGHT, padx=2)

        self.clear_btn = self.create_btn(self.control_frame, "🗑", self.clear_all)
        self.clear_btn.config(font=("Segoe UI Symbol", 13, "bold"), fg="#555555")
        self.clear_btn.pack(side=tk.RIGHT, padx=2)

        self.list_container = tk.Frame(self.window, bg=self.bg_color)
        self.list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(self.list_container, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width - 20))
        
        self.window.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

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

        self.privacy_frame = None
        self.idle_timer = None
        
        self.window.bind("<Any-KeyPress>", self.reset_timer)
        self.window.bind("<Any-ButtonPress>", self.reset_timer)
        self.window.bind("<Motion>", self.reset_timer)
        self.reset_timer()
        self.window.bind("<Enter>", self.show_scrollbar)
        self.window.bind("<Leave>", self.hide_scrollbar)

    def show_scrollbar(self, event=None):
        self.scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")

    def hide_scrollbar(self, event=None):
        x, y = self.window.winfo_pointerxy()
        x0 = self.window.winfo_rootx()
        y0 = self.window.winfo_rooty()
        x1 = x0 + self.window.winfo_width()
        y1 = y0 + self.window.winfo_height()
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            self.scrollbar.place_forget() 

    def create_btn(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg=self.bg_color, fg=self.icon_color, 
                        borderwidth=0, activebackground=self.sub_bg_color, 
                        font=("Segoe UI Symbol", 10), command=command, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=self.sub_bg_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.bg_color))
        return btn
    
    def apply_autostart(self):
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(__file__) 
            
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            exists = False
            try:
                winreg.QueryValueEx(key, "MyStickyNote")
                exists = True
            except FileNotFoundError:
                pass

            if self.autostart and not exists:
                run_cmd = f'"{app_path}"' if getattr(sys, 'frozen', False) else f'pythonw "{app_path}"'
                winreg.SetValueEx(key, "MyStickyNote", 0, winreg.REG_SZ, run_cmd)
            elif not self.autostart and exists:
                winreg.DeleteValue(key, "MyStickyNote")
                
            winreg.CloseKey(key)
        except Exception as e:
            pass
    
    def update_app_colors(self):
        theme = self.themes[self.groups[self.current_group]["theme_idx"]]
        self.bg_color = theme["bg"]
        self.sub_bg_color = theme["sub"]
        self.drag_color = theme["drag"]

        self.window.configure(bg=self.bg_color)
        self.title_bar.configure(bg=self.bg_color)
        self.tab_frame.configure(bg=self.bg_color)
        self.control_frame.configure(bg=self.bg_color)
        self.list_container.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        self.list_frame.configure(bg=self.bg_color)
        self.grip.configure(bg=self.bg_color)
        self.close_btn.configure(bg=self.bg_color)
        self.lock_btn.configure(bg=self.bg_color)
        self.clear_btn.configure(bg=self.bg_color)

    def render_tabs(self):
        for widget in self.tab_frame.winfo_children():
            widget.destroy()

        add_tab_btn = tk.Button(self.tab_frame, text="💬", bg=self.bg_color, fg=self.icon_color, 
                                bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", command=self.add_group)
        add_tab_btn.pack(side=tk.LEFT, padx=5)

        for group_name in self.groups.keys():
            is_current = (group_name == self.current_group)
            btn_bg = self.sub_bg_color if is_current else self.bg_color
            font_weight = "bold" if is_current else "normal"
            
            tab_btn = tk.Button(self.tab_frame, text=group_name, bg=btn_bg, fg=self.text_color, 
                                bd=0, font=("Segoe UI", 10, font_weight), cursor="hand2",
                                command=lambda g=group_name: self.switch_group(g))
            tab_btn.pack(side=tk.LEFT, padx=2)
            tab_btn.bind("<Button-3>", lambda e, g=group_name: self.show_tab_menu(e, g))

    def show_tab_menu(self, event, group_name):
        menu = tk.Menu(self.window, tearoff=0, bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 10), bd=0)      
        menu.add_command(label="Rename", command=lambda: self.rename_group(group_name))
        menu.add_command(label="Delete", command=lambda: self.delete_group(group_name))     
        menu.tk_popup(event.x_root, event.y_root)

    def delete_group(self, group_name):
        if len(self.groups) == 1:
            self.groups = {"General": {"theme_idx": 0, "items": []}}
            self.current_group = "General"
            self.update_app_colors()
            for child in self.list_frame.winfo_children():
                child.destroy()
            self.add_row()
            
        else:
            if self.current_group == group_name:
                del self.groups[group_name]
                
                self.current_group = list(self.groups.keys())[0]
                self.update_app_colors()
                
                for child in self.list_frame.winfo_children():
                    child.destroy()
                    
                items = self.groups[self.current_group].get("items", [])
                if items:
                    for item in items:
                        self.add_row(item.get("main", ""), item.get("sub", ""), item.get("sub_open", False), item.get("date", ""))
                else:
                    self.add_row()
            
            else:
                del self.groups[group_name]
                
        self.render_tabs() 
        self.save_data()   

    def save_current_items_to_memory(self):
        items_data = []
        for child in self.list_frame.winfo_children():
            if hasattr(child, 'entry'): 
                items_data.append({
                    "main": child.entry.get(),
                    "sub": child.sub_text.get("1.0", tk.END).strip(),
                    "sub_open": child.is_sub_open,
                    "date": child.date_entry.get() if child.date_entry.winfo_manager() == "pack" else ""
                })
        self.groups[self.current_group]["items"] = items_data

    def switch_group(self, group_name):
        if group_name == self.current_group: return
        self.save_current_items_to_memory()
        
        self.current_group = group_name
        self.update_app_colors()
        
        for child in self.list_frame.winfo_children():
            child.destroy()
            
        items = self.groups[self.current_group].get("items", [])
        if items:
            for item in items:
                self.add_row(item.get("main", ""), item.get("sub", ""), item.get("sub_open", False), item.get("date", ""))
        else:
            self.add_row()
            
        self.render_tabs()
        self.save_data()

    def add_group(self):
        new_name = simpledialog.askstring("New Group", "Enter group name:", parent=self.window)
        if new_name and new_name not in self.groups:
            theme_idx = len(self.groups) % len(self.themes)
            self.groups[new_name] = {"theme_idx": theme_idx, "items": []}
            self.switch_group(new_name)

    def rename_group(self, old_name):
        new_name = simpledialog.askstring("Rename Group", f"Rename '{old_name}' to:", parent=self.window)
        if new_name and new_name != old_name and new_name not in self.groups:
            self.groups[new_name] = self.groups.pop(old_name)
            if self.current_group == old_name:
                self.current_group = new_name
            self.render_tabs()
            self.save_data()

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
        
        # 取得滑鼠放開時的座標，找出下方的元件
        x, y = self.window.winfo_pointerxy()
        target_widget = self.window.winfo_containing(x, y)
        
        target_group = None
        if target_widget and target_widget.master == self.tab_frame:
            btn_text = target_widget.cget("text")
            if btn_text in self.groups and btn_text != self.current_group:
                target_group = btn_text
                
        if target_group:
            item_data = {
                "main": self.dragged_row.entry.get(),
                "sub": self.dragged_row.sub_text.get("1.0", tk.END).strip(),
                "sub_open": self.dragged_row.is_sub_open,
                "date": self.dragged_row.date_entry.get() if self.dragged_row.date_entry.winfo_manager() == "pack" else ""
            }
            
            if "items" not in self.groups[target_group]:
                self.groups[target_group]["items"] = []
            self.groups[target_group]["items"].append(item_data)
            
            self.dragged_row.destroy()
            if len(self.list_frame.winfo_children()) == 0:
                self.add_row()
                
            self.dragged_row = None
            self.save_data()
            return 
        
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
    
    def reset_timer(self, event=None):
        if self.privacy_frame and self.privacy_frame.winfo_exists():
            return

        if self.idle_timer:
            self.window.after_cancel(self.idle_timer)

        self.idle_timer = self.window.after(30000, self.hide_content)

    def hide_content(self):
        self.title_bar.pack_forget()
        self.list_container.pack_forget()
        self.grip.place_forget()

        self.privacy_frame = tk.Frame(self.window, bg=self.bg_color)
        self.privacy_frame.pack(expand=True, fill=tk.BOTH)

        unlock_btn = tk.Button(self.privacy_frame, text="to do list", font=("Segoe UI", 12, "bold"),
                               bg=self.sub_bg_color, fg=self.text_color, relief="flat", cursor="hand2",
                               command=self.verify_and_show)
        unlock_btn.pack(pady=(60, 10) if self.password else 60)

        if self.password:
            self.pwd_entry = tk.Entry(self.privacy_frame, show="*", font=self.font, justify="center", bd=0)
            self.pwd_entry.pack(pady=(10, 5))
            self.pwd_entry.bind("<Return>", lambda e: self.verify_and_show())

            hint_label = tk.Label(self.privacy_frame, text="Press ENTER to login", 
                                  bg=self.bg_color, fg=self.icon_color, font=("Segoe UI", 9))
            hint_label.pack()
            self.pwd_entry.focus_set()
        else:
            self.pwd_entry = None

    def verify_and_show(self):
        if self.password and self.pwd_entry:
            if self.pwd_entry.get() != self.password:
                self.pwd_entry.delete(0, tk.END)
                return

        self.privacy_frame.destroy()

        self.title_bar.pack(fill=tk.X, pady=(2, 0))
        self.list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        if not self.is_locked:
            self.grip.place(relx=1.0, rely=1.0, anchor="se")

        self.reset_timer()

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
        self.save_current_items_to_memory() 

        data = {
            "password": getattr(self, 'password', ""),
            "autostart": getattr(self, 'autostart', True),
            "x": self.window.winfo_x(),
            "y": self.window.winfo_y(),
            "width": self.window.winfo_width(),
            "height": self.window.winfo_height(),
            "is_locked": self.is_locked,
            "current_group": self.current_group,
            "groups": self.groups     
        }
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                self.autostart = data.get('autostart', True)
                self.password = data.get('password', "")
                
                w = data.get('width', 350) 
                h = data.get('height', 300)
                x = data.get('x', 200)
                y = data.get('y', 200)
                self.window.geometry(f"{w}x{h}+{x}+{y}")

                self.groups = data.get("groups", {"General": {"theme_idx": 0, "items": data.get("items", [])}})
                self.current_group = data.get("current_group", "General")
                self.update_app_colors()
                
                self.is_locked = data.get('is_locked', False)
                if self.is_locked:
                    self.lock_btn.config(text="🔒", fg="#d9534f")
                    self.grip.place_forget() 
                    self.close_btn.pack_forget() 
                
                items = self.groups[self.current_group].get("items", [])
                if items:
                    for item in items:
                        self.add_row(item.get("main", ""), item.get("sub", ""), item.get("sub_open", False), item.get("date", ""))
                else:
                    self.add_row()
        else:
            self.autostart = True
            self.password = ""
            self.window.geometry("350x300+200+200")
            self.add_row()
            
        self.render_tabs()
        self.apply_autostart()

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNote(root)
    root.mainloop()
