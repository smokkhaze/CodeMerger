import os
from charset_normalizer import detect
import json
import tkinter as tk
import threading
import fnmatch
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from binaryornot.check import is_binary

# Константы
MAX_FILE_SIZE = None
MAX_CONTENT_LENGTH = None
CONFIG_FILE = 'codemerger_config.json'
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.jpg', '.png', '.zip', '.pdf', '.bin', '.ico',
    '.mp3', '.mp4'
}


class CodeMerger:
    def __init__(self, root):
        self.root = root
        self.root.geometry('900x650')
        self.root.minsize(800, 550)
        self.root.configure(bg='#f0f0f0')
        self.root.title("CodeMerger")
        self.config = self.load_app_config()
        self.max_content_length = self.config.get('max_content_length', MAX_CONTENT_LENGTH)
        self.max_file_size = self.config.get('max_file_size', MAX_FILE_SIZE)
        self.excluded_files = set(self.config.get('excluded_files', []))
        self.ignore_patterns = self.config.get('ignore_patterns', [])
        self.structure = defaultdict(list)
        self.current_filter = tk.StringVar(value='ALL')
        self.lock = threading.Lock()
        self.folder_path = ""
        self.search_file_var = tk.StringVar()
        self.search_content_var = tk.StringVar()
        self.max_content_length_var = tk.StringVar()
        self.excluded_files_var = tk.StringVar(value=', '.join(self.excluded_files))
        self.max_file_size_var = tk.StringVar()
        self.setup_ui()

    def load_app_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        default_config = {
            'max_content_length': None,
            'max_file_size': None,
            'excluded_files': [],
            'ignore_patterns': []
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config

    def save_app_config(self):
        max_length_text = self.max_content_length_var.get()
        if max_length_text and max_length_text != "Max Length":
            try:
                self.max_content_length = int(max_length_text)
            except ValueError:
                pass
        else:
            self.max_content_length = None

        max_size_text = self.max_file_size_var.get()
        if max_size_text and max_size_text != "Max Size":
            try:
                self.max_file_size = int(max_size_text) * 1024
            except ValueError:
                pass
        else:
            self.max_file_size = None

        excluded_files_text = self.excluded_files_var.get()
        if excluded_files_text and excluded_files_text != "Exclude Files":
            self.excluded_files = set(file.strip() for file in excluded_files_text.split(',') if file.strip())

        self.config['max_content_length'] = self.max_content_length
        self.config['max_file_size'] = self.max_file_size
        self.config['excluded_files'] = list(self.excluded_files)
        self.config['ignore_patterns'] = self.ignore_patterns
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        bg_color = '#f0f0f0'

        toolbar = ttk.Frame(self.root, padding=5, borderwidth=0)
        toolbar.pack(fill=tk.X, pady=5)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TButton',
                        font=('Segoe UI', 9, 'bold'),
                        padding=3,
                        borderwidth=0,
                        relief='flat',
                        foreground='#2c3e50',
                        background='#ecf0f1')
        style.map('Modern.TButton',
                  background=[('active', '#3498db'), ('pressed', '#3498db')],
                  foreground=[('active', 'white'), ('pressed', 'white')])

        style.configure('Custom.TMenubutton',
                        font=('Segoe UI', 9),
                        padding=3,
                        borderwidth=0,
                        relief='flat',
                        background='#ecf0f1',
                        foreground='#2c3e50')
        style.map('Custom.TMenubutton',
                  background=[('active', '#3498db')],
                  foreground=[('active', 'white')])

        style.configure('TreeFrame.TFrame', background=bg_color)
        style.configure('IgnoreFrame.TFrame', background=bg_color)
        style.configure('SettingsFrame.TFrame', background=bg_color)
        style.configure('SettingsFrame2.TFrame', background=bg_color)

        btn_frame = ttk.Frame(toolbar)
        btn_frame.pack(side=tk.LEFT, padx=2)

        ttk.Button(btn_frame, text='📂 Select', command=self.select_folder,
                   style='Modern.TButton', width=10, takefocus=0).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text='▶ Start', command=self.start_scan,
                   style='Modern.TButton', width=9, takefocus=0).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text='🗑 Clear', command=self.remove_all_files,
                   style='Modern.TButton', width=9, takefocus=0).pack(side=tk.LEFT, padx=3)

        ttk.Label(btn_frame, text="🔍", font=('Arial', 12)).pack(side=tk.LEFT, padx=(3, 0))
        self.search_file_entry = ttk.Entry(btn_frame, textvariable=self.search_file_var, width=15, font=('Segoe UI', 9))
        self.search_file_entry.pack(side=tk.LEFT, padx=(0, 3))
        self.search_file_entry.insert(0, "Search file")
        self.search_file_entry.config(foreground='grey')
        self.search_file_entry.bind('<FocusIn>', self.clear_placeholder_search_file)
        self.search_file_entry.bind('<FocusOut>', self.restore_placeholder_search_file)
        self.search_file_entry.bind('<Return>', self.search_file)
        self.search_file_entry.bind('<KP_Enter>', self.search_file)

        ttk.Label(btn_frame, text="🔍", font=('Arial', 12)).pack(side=tk.LEFT, padx=(3, 0))
        self.search_content_entry = ttk.Entry(btn_frame, textvariable=self.search_content_var, width=15,
                                              font=('Segoe UI', 9))
        self.search_content_entry.pack(side=tk.LEFT, padx=(0, 3))
        self.search_content_entry.insert(0, "Search content")
        self.search_content_entry.config(foreground='grey')
        self.search_content_entry.bind('<FocusIn>', self.clear_placeholder_search_content)
        self.search_content_entry.bind('<FocusOut>', self.restore_placeholder_search_content)
        self.search_content_entry.bind('<Return>', self.search_content)
        self.search_content_entry.bind('<KP_Enter>', self.search_content)

        self.status_menu = ttk.OptionMenu(
            btn_frame,
            self.current_filter,
            'ALL',
            'ALL', 'OK', 'ERROR', 'BINARY', 'SKIPPED', 'ACCESS_DENIED',
            command=self.apply_filter_from_menu,
            style='Custom.TMenubutton'
        )
        self.status_menu.pack(side=tk.LEFT, padx=10)
        menu = self.status_menu['menu']
        menu.configure(font=('Segoe UI', 9))

        ttk.Button(toolbar, text='Export MD', command=self.export_markdown,
                   style='Modern.TButton', width=10, takefocus=0).pack(side=tk.RIGHT, padx=3)
        ttk.Button(toolbar, text='Export JSON', command=self.export_json,
                   style='Modern.TButton', width=10, takefocus=0).pack(side=tk.RIGHT, padx=3)

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        tree_frame.configure(style='TreeFrame.TFrame')

        self.file_list = ttk.Treeview(tree_frame, columns=('name', 'path', 'status'), show='headings',
                                      selectmode='browse')
        self.file_list.heading('name', text='File Name', anchor=tk.W)
        self.file_list.heading('path', text='Path', anchor=tk.W)
        self.file_list.heading('status', text='Status')
        self.file_list.column('name', width=200, stretch=tk.NO)
        self.file_list.column('path', width=450)
        self.file_list.column('status', width=80, anchor=tk.CENTER)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.configure(yscrollcommand=scrollbar.set)

        self.file_list.bind('<Double-1>', self.show_file_content)

        ignore_frame = ttk.Frame(self.root, borderwidth=0)
        ignore_frame.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(5, 0))
        ignore_frame.configure(style='IgnoreFrame.TFrame')
        self.ignore_combo = ttk.Combobox(ignore_frame, values=self.ignore_patterns, width=35, state='normal')
        self.ignore_combo.pack(side=tk.LEFT)
        self.ignore_combo.insert(0, "Ignore")
        self.ignore_combo.config(foreground='grey')
        self.ignore_combo.bind('<FocusIn>', self.clear_placeholder_ignore)
        self.ignore_combo.bind('<FocusOut>', self.restore_placeholder_ignore)
        self.ignore_combo.bind('<Return>', self.add_ignore_pattern)
        self.ignore_combo.bind('<KP_Enter>', self.add_ignore_pattern)
        self.ignore_combo.bind('<Delete>', self.remove_ignore_pattern)

        settings_frame = ttk.Frame(self.root, borderwidth=0)
        settings_frame.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(5, 0))
        settings_frame.configure(style='SettingsFrame.TFrame')

        self.max_length_entry = ttk.Entry(settings_frame, textvariable=self.max_content_length_var, width=11)
        self.max_length_entry.pack(side=tk.LEFT, padx=(0, 15))
        if not self.max_content_length_var.get():
            self.max_length_entry.insert(0, "Max Length")
            self.max_length_entry.config(foreground='grey')
        self.max_length_entry.bind('<FocusIn>', self.clear_placeholder_max_length)
        self.max_length_entry.bind('<FocusOut>', self.restore_placeholder_max_length)
        self.max_length_entry.bind('<Return>', self.update_max_length_display)
        self.max_length_entry.bind('<KP_Enter>', self.update_max_length_display)

        self.excluded_files_entry = ttk.Entry(settings_frame, textvariable=self.excluded_files_var, width=23)
        self.excluded_files_entry.pack(side=tk.LEFT, padx=(0, 15))
        if not self.excluded_files_var.get():
            self.excluded_files_entry.insert(0, "Exclude Files")
            self.excluded_files_entry.config(foreground='grey')
        self.excluded_files_entry.bind('<FocusIn>', self.clear_placeholder_excluded_files)
        self.excluded_files_entry.bind('<FocusOut>', self.restore_placeholder_excluded_files)

        settings_frame2 = ttk.Frame(self.root, borderwidth=0)
        settings_frame2.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(0, 5))
        settings_frame2.configure(style='SettingsFrame2.TFrame')

        self.max_file_size_entry = ttk.Entry(settings_frame2, textvariable=self.max_file_size_var, width=11)
        self.max_file_size_entry.pack(side=tk.LEFT, padx=(0, 15))
        if not self.max_file_size_var.get():
            self.max_file_size_entry.insert(0, "Max Size")
            self.max_file_size_entry.config(foreground='grey')
        self.max_file_size_entry.bind('<FocusIn>', self.clear_placeholder_max_file_size)
        self.max_file_size_entry.bind('<FocusOut>', self.restore_placeholder_max_file_size)
        self.max_file_size_entry.bind('<Return>', self.update_max_file_size_display)
        self.max_file_size_entry.bind('<KP_Enter>', self.update_max_file_size_display)

        # Новый фрейм для строки статуса снизу
        status_frame = ttk.Frame(self.root, borderwidth=0)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

        self.action_status = ttk.Label(status_frame, anchor=tk.W)
        self.action_status.pack(side=tk.LEFT, padx=10)

        self.stats_status = ttk.Label(status_frame, anchor=tk.E)
        self.stats_status.pack(side=tk.RIGHT, padx=10)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open File", command=self.open_selected_file)
        self.context_menu.add_command(label="Copy Path", command=self.copy_file_path)
        self.context_menu.add_command(label="Show Content", command=self.show_file_content)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Show in Explorer", command=self.reveal_in_explorer)
        self.file_list.bind("<Button-3>", self.show_context_menu)

    def clear_placeholder_search_file(self, event):
        if self.search_file_var.get() == "Search file":
            self.search_file_entry.delete(0, tk.END)
            self.search_file_entry.config(foreground='black')

    def restore_placeholder_search_file(self, event):
        if not self.search_file_var.get():
            self.search_file_entry.insert(0, "Search file")
            self.search_file_entry.config(foreground='grey')

    def clear_placeholder_search_content(self, event):
        if self.search_content_var.get() == "Search content":
            self.search_content_entry.delete(0, tk.END)
            self.search_content_entry.config(foreground='black')

    def restore_placeholder_search_content(self, event):
        if not self.search_content_var.get():
            self.search_content_entry.insert(0, "Search content")
            self.search_content_entry.config(foreground='grey')

    def clear_placeholder_ignore(self, event):
        if self.ignore_combo.get() == "Ignore":
            self.ignore_combo.delete(0, tk.END)
            self.ignore_combo.config(foreground='black')

    def restore_placeholder_ignore(self, event):
        if not self.ignore_combo.get():
            self.ignore_combo.insert(0, "Ignore")
            self.ignore_combo.config(foreground='grey')

    def clear_placeholder_max_length(self, event):
        if self.max_content_length_var.get() == "Max Length":
            self.max_length_entry.delete(0, tk.END)
            self.max_length_entry.config(foreground='black')

    def restore_placeholder_max_length(self, event):
        if not self.max_content_length_var.get():
            self.max_length_entry.insert(0, "Max Length")
            self.max_length_entry.config(foreground='grey')

    def clear_placeholder_excluded_files(self, event):
        if self.excluded_files_var.get() == "Exclude Files":
            self.excluded_files_entry.delete(0, tk.END)
            self.excluded_files_entry.config(foreground='black')

    def restore_placeholder_excluded_files(self, event):
        if not self.excluded_files_var.get():
            self.excluded_files_entry.insert(0, "Exclude Files")
            self.excluded_files_entry.config(foreground='grey')

    def clear_placeholder_max_file_size(self, event):
        if self.max_file_size_var.get() == "Max Size":
            self.max_file_size_entry.delete(0, tk.END)
            self.max_file_size_entry.config(foreground='black')

    def restore_placeholder_max_file_size(self, event):
        if not self.max_file_size_var.get():
            self.max_file_size_entry.insert(0, "Max Size")
            self.max_file_size_entry.config(foreground='grey')

    def update_max_length_display(self, event=None):
        max_length_text = self.max_content_length_var.get()
        if max_length_text and max_length_text != "Max Length":
            try:
                self.max_content_length = int(max_length_text)
                self.save_app_config()
            except ValueError:
                pass
        self.restore_placeholder_max_length(None)

    def update_max_file_size_display(self, event=None):
        max_size_text = self.max_file_size_var.get()
        if max_size_text and max_size_text != "Max Size":
            try:
                size_kb = int(max_size_text)
                self.max_file_size = size_kb * 1024
                if size_kb < 1024:
                    display_text = f"<{size_kb}kb>"
                else:
                    size_mb = size_kb // 1024
                    display_text = f"<{size_mb}mb>"
                self.max_file_size_var.set(display_text)
                self.max_file_size_entry.config(foreground='grey')
                self.save_app_config()
            except ValueError:
                pass
        else:
            self.max_file_size = None
            self.restore_placeholder_max_file_size(None)

    def apply_filter_from_menu(self, value):
        self.update_file_list()

    def show_file_content(self, event=None):
        item = self.file_list.selection()
        if not item:
            return
        selected_values = self.file_list.item(item, 'values')
        file_name = selected_values[0]

        file_data = None
        for folder_files in self.structure.values():
            for f in folder_files:
                if f['name'] == file_name:
                    relative_path = os.path.relpath(f['path'], self.folder_path)
                    if relative_path in selected_values[1]:
                        file_data = f
                        break
            if file_data:
                break

        if not file_data:
            messagebox.showerror("Error", "File data not found in structure.")
            return
        if not file_data['content']:
            messagebox.showinfo("Content", "No readable content available.")
            return

        content_window = tk.Toplevel(self.root)
        content_window.title(f"Content of {file_data['name']}")
        content_window.geometry('600x400')
        text_area = tk.Text(content_window, wrap=tk.WORD)
        text_area.insert(tk.END, file_data['content'])
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.config(state=tk.DISABLED)

    def show_context_menu(self, event):
        item = self.file_list.identify_row(event.y)
        if item:
            self.file_list.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_selected_file(self):
        item = self.file_list.selection()
        if item:
            path = self.get_full_path_from_display_path(self.file_list.item(item, 'values')[1])
            if path:
                try:
                    if os.name == 'nt':
                        os.startfile(path)
                    elif os.name == 'posix':
                        os.system(f'xdg-open "{path}"')
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open file: {str(e)}")

    def copy_file_path(self):
        item = self.file_list.selection()
        if item:
            path = self.get_full_path_from_display_path(self.file_list.item(item, 'values')[1])
            if path:
                self.root.clipboard_clear()
                self.root.clipboard_append(path)

    def reveal_in_explorer(self):
        item = self.file_list.selection()
        if item:
            path = self.get_full_path_from_display_path(self.file_list.item(item, 'values')[1])
            if path:
                folder = os.path.dirname(path)
                try:
                    if os.name == 'nt':
                        os.startfile(folder)
                    elif os.name == 'posix':
                        os.system(f'xdg-open "{folder}"')
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open folder: {str(e)}")

    def get_full_path_from_display_path(self, display_path):
        for folder_files in self.structure.values():
            for f in folder_files:
                relative_path = os.path.relpath(f['path'], self.folder_path)
                root_drive = os.path.splitdrive(self.folder_path)[0] + "/"
                folder_name = os.path.basename(self.folder_path.rstrip('/\\'))
                constructed_display_path = f"{root_drive}.../{folder_name}/{relative_path}"
                if constructed_display_path == display_path:
                    return f['path']
        return None

    def search_file(self, event=None):
        query = self.search_file_var.get().strip().lower()
        if not query or query == "search file":
            return
        children = list(self.file_list.get_children())
        if not children:
            return
        current_selection = self.file_list.selection()
        start_index = children.index(current_selection[0]) + 1 if current_selection else 0
        if start_index >= len(children):
            start_index = 0
        for i in range(start_index, len(children)):
            values = self.file_list.item(children[i], 'values')
            if query in values[0].lower():
                self.file_list.selection_set(children[i])
                self.file_list.focus(children[i])
                self.file_list.see(children[i])
                self.action_status.config(text=f"Found file: {values[0]}")
                self.stats_status.config(text="")
                return
        self.action_status.config(text="No file matches")
        self.stats_status.config(text="")

    def search_content(self, event=None):
        query = self.search_content_var.get().strip().lower()
        if not query or query == "search content":
            return
        children = list(self.file_list.get_children())
        if not children:
            return
        current_selection = self.file_list.selection()
        start_index = children.index(current_selection[0]) + 1 if current_selection else 0
        if start_index >= len(children):
            start_index = 0
        for i in range(start_index, len(children)):
            values = self.file_list.item(children[i], 'values')
            file_data = next((f for folder in self.structure.values() for f in folder if
                              os.path.relpath(f['path'], self.folder_path) in values[1]), None)
            if file_data and file_data['content'] and query in file_data['content'].lower():
                self.file_list.selection_set(children[i])
                self.file_list.focus(children[i])
                self.file_list.see(children[i])
                self.action_status.config(text=f"Found content in: {values[0]}")
                self.stats_status.config(text="")
                return
        self.action_status.config(text="No content matches")
        self.stats_status.config(text="")

    def add_ignore_pattern(self, event=None):
        pattern = self.ignore_combo.get().strip()
        if pattern and pattern != "Ignore" and pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
            self.ignore_combo['values'] = self.ignore_patterns
            self.save_app_config()
            self.action_status.config(text=f"Added ignore pattern: {pattern}")
            self.stats_status.config(text="")
        self.ignore_combo.delete(0, tk.END)
        self.restore_placeholder_ignore(None)

    def remove_ignore_pattern(self, event=None):
        selected = self.ignore_combo.get()
        if selected and selected != "Ignore" and selected in self.ignore_patterns:
            self.ignore_patterns.remove(selected)
            self.ignore_combo['values'] = self.ignore_patterns
            self.ignore_combo.set('')
            self.save_app_config()
            self.action_status.config(text=f"Removed ignore pattern: {selected}")
            self.stats_status.config(text="")
        self.restore_placeholder_ignore(None)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.folder_path = folder_path
            self.action_status.config(text=f"Selected: {folder_path}")
            self.stats_status.config(text="")

    def start_scan(self):
        if not self.folder_path:
            messagebox.showwarning("Error", "Select folder first")
            return
        self.save_app_config()
        self.action_status.config(text="Scanning...")
        self.stats_status.config(text="")
        threading.Thread(target=self.scan_folder, args=(self.folder_path,), daemon=True).start()

    def scan_folder(self, folder_path):
        self.structure.clear()
        processed_files = 0
        errors = 0
        max_workers = min(os.cpu_count() or 4, 8)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    if any(fnmatch.fnmatch(file_path, p) for p in self.ignore_patterns):
                        continue
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_ext in BINARY_EXTENSIONS or is_binary(file_path):
                            self.add_to_structure(file_path, file_ext, status='BINARY', size=file_size)
                            processed_files += 1
                            continue
                        if self.max_file_size and file_size > self.max_file_size:
                            self.add_to_structure(file_path, file_ext, status='SKIPPED', size=file_size)
                            processed_files += 1
                            continue
                        futures.append(executor.submit(self.process_file, file_path, file_ext, root, folder_path))
                    except PermissionError:
                        self.add_to_structure(file_path, file_ext, status='ACCESS_DENIED', size=file_size)
                        processed_files += 1
                        errors += 1
                        continue
            for future in as_completed(futures):
                processed_files += 1
                try:
                    future.result()  # Проверяем, были ли ошибки в обработке
                except Exception:
                    errors += 1

        self.root.after(0, self.update_file_list)
        self.root.after(0, lambda: self.action_status.config(text="Scanned"))
        self.root.after(0, lambda: self.stats_status.config(text=f"Files: {processed_files}, Errors: {errors}"))

    def process_file(self, file_path, file_ext, root, folder_path):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            detected = detect(raw_data)
            encoding = detected['encoding'] if detected['confidence'] > 0.9 else 'utf-8'
            content = raw_data.decode(encoding, errors='replace')
            max_length = self.max_content_length if self.max_content_length is not None else None
            if os.path.basename(file_path) in self.excluded_files:
                max_length = None
            truncated = "\n[TRUNCATED]" if max_length and len(content) >= max_length else ""
            content = content[:max_length] + truncated if max_length else content

            parent_folder = os.path.relpath(root, folder_path)
            with self.lock:
                self.structure[parent_folder].append({
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'extension': file_ext,
                    'content': content,
                    'status': 'OK',
                    'encoding': encoding,
                    'size': os.path.getsize(file_path)
                })
        except Exception as e:
            self.add_to_structure(file_path, file_ext, status='ERROR', error=str(e), size=os.path.getsize(file_path))
            raise  # Поднимаем исключение, чтобы подсчитать ошибки

    def add_to_structure(self, file_path, file_ext, status='OK', error=None, size=None):
        parent_folder = os.path.relpath(os.path.dirname(file_path), self.folder_path)
        content = "" if status == 'OK' else None
        with self.lock:
            self.structure[parent_folder].append({
                'name': os.path.basename(file_path),
                'path': file_path,
                'extension': file_ext,
                'content': content,
                'status': status,
                'encoding': 'unknown' if status != 'OK' else None,
                'error': error if error else None,
                'size': size if size is not None else os.path.getsize(file_path)
            })

    def update_file_list(self):
        self.file_list.delete(*self.file_list.get_children())
        if not self.folder_path:
            return
        root_drive = os.path.splitdrive(self.folder_path)[0] + "/"
        folder_name = os.path.basename(self.folder_path.rstrip('/\\'))
        for folder, files in self.structure.items():
            for file in files:
                if self.current_filter.get() == 'ALL' or file['status'] == self.current_filter.get():
                    relative_path = os.path.relpath(file['path'], self.folder_path)
                    display_path = f"{root_drive}.../{folder_name}/{relative_path}"
                    self.file_list.insert('', 'end', values=(file['name'], display_path, file['status']))

    def export_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.json')
        if not file_path:
            return
        try:
            metadata = {
                'scanned_folder': self.folder_path,
                'timestamp': datetime.now().isoformat(),
                'total_files': sum(len(files) for files in self.structure.values()),
                'successful_files': sum(1 for folder in self.structure.values() for f in folder if f['status'] == 'OK'),
                'error_files': sum(1 for folder in self.structure.values() for f in folder if f['status'] == 'ERROR'),
                'binary_files': sum(1 for folder in self.structure.values() for f in folder if f['status'] == 'BINARY'),
                'skipped_files': sum(
                    1 for folder in self.structure.values() for f in folder if f['status'] == 'SKIPPED'),
                'access_denied_files': sum(
                    1 for folder in self.structure.values() for f in folder if f['status'] == 'ACCESS_DENIED')
            }
            structure = {}
            for folder, files in self.structure.items():
                structure[folder] = [
                    {
                        'name': f['name'],
                        'path': os.path.relpath(f['path'], self.folder_path),
                        'extension': f['extension'],
                        'status': f['status'],
                        'content': f['content'],
                        'encoding': f.get('encoding', 'unknown'),
                        'error': f.get('error', None),
                        'size': f['size'],
                        'last_modified': datetime.fromtimestamp(os.path.getmtime(f['path'])).isoformat()
                    } for f in files
                ]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'metadata': metadata, 'structure': structure}, f, ensure_ascii=False, indent=2)
            messagebox.showinfo('Success', f'Exported to {file_path}')
        except Exception as e:
            messagebox.showerror('Error', f'Export failed: {str(e)}')

    def export_markdown(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.md')
        if not file_path:
            return
        try:
            md_content = f"# CodeMerger: {self.folder_path}\n\n"
            md_content += "## Summary\n"
            total_files = sum(len(files) for files in self.structure.values())
            errors = sum(1 for folder in self.structure.values() for f in folder if f['status'] == 'ERROR')
            binary = sum(1 for folder in self.structure.values() for f in folder if f['status'] == 'BINARY')
            skipped = sum(1 for folder in self.structure.values() for f in folder if f['status'] == 'SKIPPED')
            access_denied = sum(
                1 for folder in self.structure.values() for f in folder if f['status'] == 'ACCESS_DENIED')
            md_content += (
                f"- **Total Files**: {total_files}\n"
                f"- **Successful**: {total_files - errors - binary - skipped - access_denied}\n"
                f"- **Errors**: {errors}\n"
                f"- **Binary**: {binary}\n"
                f"- **Skipped**: {skipped}\n"
                f"- **Access Denied**: {access_denied}\n"
                f"- **Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            )
            md_content += "## Structure\n"
            for folder, files in sorted(self.structure.items()):
                md_content += f"### {folder if folder else 'Root'}\n"
                for file in sorted(files, key=lambda x: x['name']):
                    status_icon = f" `[{file['status']}]`" if file['status'] != 'OK' else ''
                    error_note = f" (error: {file['error']})" if file.get('error') else ''
                    size_note = f" (size: {file['size'] // 1024}kb)" if file.get('size') else ''
                    md_content += f"- `{file['extension']}` **{file['name']}**{status_icon}{error_note}{size_note} (encoding: {file.get('encoding', 'unknown')})\n"
                    if file['content']:
                        md_content += f"```{(file['extension'][1:] if file['extension'] else 'text')}\n{file['content']}\n```\n"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            messagebox.showinfo('Success', f'Exported to {file_path}')
        except Exception as e:
            messagebox.showerror('Error', f'Export failed: {str(e)}')

    def remove_all_files(self):
        self.file_list.delete(*self.file_list.get_children())
        self.structure.clear()
        self.action_status.config(text="List cleared")
        self.stats_status.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CodeMerger")
    root.protocol("WM_DELETE_WINDOW", root.quit)
    app = CodeMerger(root)
    root.mainloop()