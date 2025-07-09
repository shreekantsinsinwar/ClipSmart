import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
from datetime import datetime

DATA_FILE = "clip_smart_data.json"

class ClipSmart:
    def __init__(self, root):
        self.root = root
        self.root.title("ClipSmart - Clipboard Manager")
        self.root.geometry("800x600")
        self.clipboard_history = []
        self.pinned_items = []
        self.last_clip = ""
        self.filtered_items = []

        self.load_data()

        self.create_widgets()
        self.poll_clipboard()

    # --------------------- UI SETUP ---------------------
    def create_widgets(self):
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_listbox)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search: ").pack(side=tk.LEFT)
        tk.Entry(search_frame, textvariable=self.search_var, width=50).pack(side=tk.LEFT)

        self.listbox = tk.Listbox(self.root, width=100, height=20, selectmode=tk.SINGLE)
        self.listbox.pack(pady=10)
        self.listbox.bind('<Double-1>', self.copy_selected_item)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # Buttons
        tk.Button(btn_frame, text="Copy", command=self.copy_selected_item, width=12).grid(row=0, column=0, padx=8, pady=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_selected_item, width=12).grid(row=0, column=1, padx=8, pady=5)
        tk.Button(btn_frame, text="Pin", command=self.pin_selected_item, width=12).grid(row=0, column=2, padx=8, pady=5)
        tk.Button(btn_frame, text="Save Snippet", command=self.save_snippet, width=12).grid(row=0, column=3, padx=8, pady=5)
        tk.Button(btn_frame, text="Export .txt", command=self.export_txt, width=12).grid(row=0, column=4, padx=8, pady=5)
        tk.Button(btn_frame, text="Clear All", command=self.clear_all, width=12).grid(row=0, column=5, padx=8, pady=5)

    # --------------------- CLIPBOARD POLLING ---------------------
    def poll_clipboard(self):
        try:
            new_clip = self.root.clipboard_get()
            if new_clip != self.last_clip:
                self.last_clip = new_clip
                self.add_to_history(new_clip)
        except tk.TclError:
            pass
        self.root.after(1000, self.poll_clipboard)

    # --------------------- HISTORY ---------------------
    def add_to_history(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"text": text, "timestamp": timestamp}
        if entry not in self.clipboard_history:
            self.clipboard_history.insert(0, entry)
            self.save_data()
            self.update_listbox()

    def update_listbox(self, *args):
        search_text = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        self.filtered_items = []

        items = self.pinned_items + self.clipboard_history
        for item in items:
            if search_text in item["text"].lower():
                display_text = f"[Pinned] " if item in self.pinned_items else ""
                display_text += item["text"][:100].replace('\n', ' ')
                self.listbox.insert(tk.END, display_text)
                self.filtered_items.append(item)

    # --------------------- ACTIONS ---------------------
    def copy_selected_item(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            text = self.filtered_items[selection[0]]["text"]
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("Copied", "Text copied to clipboard!")

    def delete_selected_item(self):
        selection = self.listbox.curselection()
        if selection:
            item = self.filtered_items[selection[0]]
            if item in self.clipboard_history:
                self.clipboard_history.remove(item)
            if item in self.pinned_items:
                self.pinned_items.remove(item)
            self.save_data()
            self.update_listbox()

    def pin_selected_item(self):
        selection = self.listbox.curselection()
        if selection:
            item = self.filtered_items[selection[0]]
            if item not in self.pinned_items:
                self.pinned_items.insert(0, item)
                self.save_data()
                self.update_listbox()

    def save_snippet(self):
        selection = self.listbox.curselection()
        if selection:
            item = self.filtered_items[selection[0]]
            snippet = item["text"]
            filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text files", "*.txt")])
            if filename:
                with open(filename, "w") as f:
                    f.write(snippet)
                messagebox.showinfo("Saved", f"Snippet saved as {filename}")

    def export_txt(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, "w") as f:
                for item in self.pinned_items + self.clipboard_history:
                    f.write(f"{item['timestamp']} - {item['text']}\n\n")
            messagebox.showinfo("Exported", f"Exported to {filename}")

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all clipboard history?"):
            self.clipboard_history = []
            self.pinned_items = []
            self.save_data()
            self.update_listbox()

    # --------------------- STORAGE ---------------------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.clipboard_history = data.get("history", [])
                self.pinned_items = data.get("pinned", [])

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump({"history": self.clipboard_history, "pinned": self.pinned_items}, f, indent=2)


# --------------------- LAUNCH ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ClipSmart(root)
    root.mainloop()
