# My Todo App
# Started this on a Sunday afternoon because I keep forgetting stuff
# Probably over-engineered it but whatever, it works

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime


class TodoManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Todo List - Don't Forget!")
        self.window.geometry("650x580")
        self.window.configure(bg='#f0f0f0')

        # Data stuff
        self.filename = "my_tasks.json"
        self.task_list = []
        self.next_id = 1

        # Load existing tasks if any
        self.load_from_file()

        # Build the UI
        self.create_interface()
        self.update_display()

    def load_from_file(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.task_list = data.get('tasks', [])
                    self.next_id = data.get('next_id', 1)
        except Exception as e:
            # File might be corrupted, start fresh
            print(f"Error loading file: {e}")
            self.task_list = []
            self.next_id = 1

    def save_to_file(self):
        """Save current state to file"""
        try:
            data = {
                'tasks': self.task_list,
                'next_id': self.next_id,
                'last_saved': datetime.now().isoformat()
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Couldn't save: {e}")

    def create_interface(self):
        """Set up the GUI - this got messy but it works"""

        # Header
        header_frame = tk.Frame(self.window, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title = tk.Label(header_frame, text="📋 My Todo List",
                         font=('Arial', 18, 'bold'),
                         fg='white', bg='#2c3e50')
        title.pack(pady=15)

        # Main container
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Add new task section
        input_frame = tk.LabelFrame(main_frame, text="Add New Task",
                                    font=('Arial', 11, 'bold'),
                                    bg='#f0f0f0', fg='#2c3e50')
        input_frame.pack(fill='x', pady=(0, 15))

        # Task input row
        entry_row = tk.Frame(input_frame, bg='#f0f0f0')
        entry_row.pack(fill='x', padx=10, pady=8)

        self.task_input = tk.Entry(entry_row, font=('Arial', 11), width=40)
        self.task_input.pack(side='left', fill='x', expand=True)
        self.task_input.bind('<Return>', self.add_task_enter)
        self.task_input.focus()

        add_button = tk.Button(entry_row, text="Add", command=self.add_task,
                               bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                               padx=20)
        add_button.pack(side='right', padx=(8, 0))

        # Priority dropdown
        priority_row = tk.Frame(input_frame, bg='#f0f0f0')
        priority_row.pack(fill='x', padx=10, pady=(0, 8))

        tk.Label(priority_row, text="Priority:", bg='#f0f0f0',
                 font=('Arial', 9)).pack(side='left')

        self.priority_choice = ttk.Combobox(priority_row, width=12,
                                            values=['High', 'Medium', 'Low'])
        self.priority_choice.set('Medium')
        self.priority_choice.pack(side='left', padx=(5, 0))

        # Filter section
        filter_frame = tk.Frame(main_frame, bg='#f0f0f0')
        filter_frame.pack(fill='x', pady=(0, 10))

        tk.Label(filter_frame, text="View:", bg='#f0f0f0',
                 font=('Arial', 10, 'bold')).pack(side='left')

        self.view_filter = tk.StringVar(value='all')

        view_options = [('All Tasks', 'all'), ('To Do', 'pending'), ('Done', 'completed')]
        for text, value in view_options:
            rb = tk.Radiobutton(filter_frame, text=text, variable=self.view_filter,
                                value=value, command=self.update_display,
                                bg='#f0f0f0', font=('Arial', 9))
            rb.pack(side='left', padx=(10, 0))

        # Task list area
        list_container = tk.Frame(main_frame, bg='#f0f0f0')
        list_container.pack(fill='both', expand=True)

        # Listbox with scrollbar
        list_frame = tk.Frame(list_container)
        list_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.task_display = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       font=('Consolas', 10), height=16,
                                       selectmode='single')
        self.task_display.pack(side='left', fill='both', expand=True)

        scrollbar.config(command=self.task_display.yview)

        # Action buttons
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(10, 0))

        # Left side buttons
        left_buttons = tk.Frame(button_frame, bg='#f0f0f0')
        left_buttons.pack(side='left')

        done_btn = tk.Button(left_buttons, text="✓ Done", command=self.mark_done,
                             bg='#3498db', fg='white', font=('Arial', 10),
                             padx=15, pady=5)
        done_btn.pack(side='left', padx=(0, 5))

        edit_btn = tk.Button(left_buttons, text="✏ Edit", command=self.edit_task,
                             bg='#f39c12', fg='white', font=('Arial', 10),
                             padx=15, pady=5)
        edit_btn.pack(side='left', padx=5)

        delete_btn = tk.Button(left_buttons, text="🗑 Delete", command=self.delete_task,
                               bg='#e74c3c', fg='white', font=('Arial', 10),
                               padx=15, pady=5)
        delete_btn.pack(side='left', padx=5)

        # Right side - stats
        self.stats_label = tk.Label(button_frame, text="", bg='#f0f0f0',
                                    font=('Arial', 9), fg='#7f8c8d')
        self.stats_label.pack(side='right')

    def add_task_enter(self, event):
        """Handle Enter key in input field"""
        self.add_task()

    def add_task(self):
        """Add new task to the list"""
        text = self.task_input.get().strip()

        if not text:
            messagebox.showwarning("Empty Task", "Enter something to do!")
            return

        # Don't add duplicate tasks
        for task in self.task_list:
            if task['text'].lower() == text.lower() and not task['done']:
                messagebox.showinfo("Duplicate", "You already have this task!")
                return

        new_task = {
            'id': self.next_id,
            'text': text,
            'done': False,
            'priority': self.priority_choice.get(),
            'added': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'completed': None
        }

        self.task_list.append(new_task)
        self.next_id += 1

        self.task_input.delete(0, tk.END)
        self.save_to_file()
        self.update_display()

        # Focus back to input for quick adding
        self.task_input.focus()

    def get_selected_task(self):
        """Get currently selected task"""
        selection = self.task_display.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Pick a task first")
            return None

        # Get task ID from the display line
        line = self.task_display.get(selection[0])
        try:
            # Extract ID from line format: "[ID] text"
            if line.startswith('['):
                task_id = int(line.split(']')[0][1:])
                for task in self.task_list:
                    if task['id'] == task_id:
                        return task
        except:
            pass

        return None

    def mark_done(self):
        """Mark selected task as completed"""
        task = self.get_selected_task()
        if not task:
            return

        if task['done']:
            # Unmark if already done
            task['done'] = False
            task['completed'] = None
        else:
            task['done'] = True
            task['completed'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        self.save_to_file()
        self.update_display()

    def edit_task(self):
        """Edit selected task text"""
        task = self.get_selected_task()
        if not task:
            return

        new_text = simpledialog.askstring("Edit Task", "Update task:",
                                          initialvalue=task['text'])

        if new_text and new_text.strip():
            task['text'] = new_text.strip()
            self.save_to_file()
            self.update_display()

    def delete_task(self):
        """Remove selected task"""
        task = self.get_selected_task()
        if not task:
            return

        # Confirm deletion
        if messagebox.askyesno("Delete Task", f"Delete '{task['text']}'?"):
            self.task_list.remove(task)
            self.save_to_file()
            self.update_display()

    def update_display(self):
        """Refresh the task list display"""
        self.task_display.delete(0, tk.END)

        # Filter tasks based on selection
        filter_choice = self.view_filter.get()

        if filter_choice == 'pending':
            show_tasks = [t for t in self.task_list if not t['done']]
        elif filter_choice == 'completed':
            show_tasks = [t for t in self.task_list if t['done']]
        else:
            show_tasks = self.task_list

        # Sort by priority and completion status
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        show_tasks.sort(key=lambda x: (x['done'], priority_order.get(x['priority'], 1)))

        # Display tasks
        for task in show_tasks:
            status = "✓" if task['done'] else "○"

            priority_symbols = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
            priority_icon = priority_symbols.get(task['priority'], '🟡')

            # Format: [ID] status priority_icon text
            line = f"[{task['id']}] {status} {priority_icon} {task['text']}"

            self.task_display.insert(tk.END, line)

        # Update stats
        total = len(self.task_list)
        done = len([t for t in self.task_list if t['done']])
        pending = total - done

        self.stats_label.config(text=f"Total: {total} | Done: {done} | To Do: {pending}")

    def run(self):
        """Start the app"""
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def on_closing(self):
        """Handle window closing"""
        self.save_to_file()
        self.window.destroy()


# Run the app
if __name__ == '__main__':
    app = TodoManager()
    app.run()