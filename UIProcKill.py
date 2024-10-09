import tkinter as tk
from tkinter import Listbox, messagebox, Scrollbar
import psutil
import ctypes


class ProcessKillerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Process Killer")

        # Get the active window's position and spawn the window there
        # Fallback if active window isn't detected
        self.master.geometry("400x500+500+200")

        # Set the window size, transparency, and remove window frame
        self.master.overrideredirect(True)  # Remove default window frame
        self.master.attributes("-alpha", 1.0)  # Fully opaque at start

        # Make window resizable
        self.master.resizable(False, False)  # Fixed size to show 20 items only

        # Call Windows API to make corners rounded (Windows only)
        if ctypes.windll.shell32.IsUserAnAdmin():
            hwnd = ctypes.windll.user32.GetParent(self.master.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 2, ctypes.byref(ctypes.c_int(1)), 4)

        self.master.config(bg="#1e1e1e")  # Dark background color
        # Detect click outside window
        self.master.bind("<FocusOut>", lambda event: master.destroy())
        self.master.bind("<Escape>", lambda event: master.destroy())

        # Bind events for moving the window
        self.master.bind('<Button-1>', self.start_move)
        self.master.bind('<B1-Motion>', self.do_move)

        # Styling
        self.bg_color = "#1e1e1e"
        self.text_color = "#ffffff"
        self.accent_color = "#3c3f41"
        self.font = ("Segoe UI", 10)

        # Title Label
        self.title_label = tk.Label(
            master, text="Process Killer", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 14))
        self.title_label.pack(pady=(20, 10))  # Add padding for title

        # Create the search bar (Entry widget)
        self.process_name_var = tk.StringVar()
        self.entry = tk.Entry(master, textvariable=self.process_name_var, bg=self.accent_color, fg=self.text_color,
                              insertbackground=self.text_color, font=self.font, relief=tk.FLAT)
        self.entry.pack(pady=10, padx=10, fill=tk.X)

        # Bind the return key in the entry to kill the process
        self.entry.bind("<Return>", self.kill_process)

        # Label for "Process List"
        self.label = tk.Label(master, text="Process List",
                              bg=self.bg_color, fg=self.text_color, font=self.font)
        self.label.pack(anchor='w', padx=10)

        # Create a Frame to hold the Listbox and Scrollbar
        self.frame = tk.Frame(master, bg=self.bg_color)
        self.frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Scrollbar for process list
        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create listbox to display processes with a maximum of 20 items shown
        self.process_listbox = Listbox(self.frame, width=50, height=20, bg=self.accent_color, fg=self.text_color, font=self.font,
                                       relief=tk.FLAT, selectbackground="#5a5e63", highlightthickness=0, bd=0,
                                       yscrollcommand=self.scrollbar.set)
        self.process_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.process_listbox.yview)

        # Bind key events for navigation and process selection
        self.process_name_var.trace_add("write", self.update_process_list)
        self.process_listbox.bind("<Up>", self.navigate_list)
        self.process_listbox.bind("<Down>", self.navigate_list)

        # Populate the process list
        self.update_process_list()
        self.entry.focus_set()  # Set focus on the search bar

        # Variables to hold window drag
        self.start_x = None
        self.start_y = None

    def start_move(self, event):
        """Initiate the move process."""
        self.start_x = event.x
        self.start_y = event.y

    def do_move(self, event):
        """Move the window by dragging."""
        deltax = event.x - self.start_x
        deltay = event.y - self.start_y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    def update_process_list(self, *args):
        """Update the listbox with matching processes and adjust window size."""
        self.process_listbox.delete(0, tk.END)
        process_name = self.process_name_var.get().lower()

        for proc in psutil.process_iter(['name']):
            if process_name in proc.info['name'].lower():
                self.process_listbox.insert(tk.END, proc.info['name'])

        # Automatically select the first matching process
        if self.process_listbox.size() > 0:
            self.process_listbox.selection_set(0)
            self.process_listbox.activate(0)

    def navigate_list(self, event):
        """Navigate through the listbox items."""
        current_selection = self.process_listbox.curselection()
        if event.keysym == "Up":
            if current_selection:
                new_selection = max(0, current_selection[0] - 1)
                self.process_listbox.selection_clear(0, tk.END)
                self.process_listbox.selection_set(new_selection)
                self.process_listbox.activate(new_selection)
        elif event.keysym == "Down":
            if current_selection:
                new_selection = min(self.process_listbox.size() - 1, current_selection[0] + 1)
                self.process_listbox.selection_clear(0, tk.END)
                self.process_listbox.selection_set(new_selection)
                self.process_listbox.activate(new_selection)


    def kill_process(self, event=None):
        """Kill the selected process."""
        selected_process = self.process_listbox.curselection()
        if selected_process:
            process_name = self.process_listbox.get(selected_process).strip()
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    try:
                        proc.kill()
                        messagebox.showinfo(
                            "Success", f"Killed process: {process_name}")
                        self.master.quit()  # Close the program after successful kill
                    except Exception as e:
                        messagebox.showerror(
                            "Error", f"Failed to kill process: {e}")
                    break
        else:
            messagebox.showwarning(
                "No Selection", "Please select a process to kill.")

    def on_focus_out(self):
        """ quit when clicked outside."""
        self.master.quit()  # Quit the program


if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessKillerApp(root)
    root.mainloop()
