# Simple Calculator
# Made this because the Windows calculator is somehow always missing when I need it
# Started as a basic calc, ended up adding more stuff because why not

import tkinter as tk
from tkinter import messagebox
import math


class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Calculator - Because Math is Hard")
        self.window.geometry("350x500")
        self.window.configure(bg='#2c3e50')
        self.window.resizable(False, False)

        # State
        self.current = ""
        self.total = 0
        self.input_value = True
        self.result = False
        self.operation_pending = None

        # History for fun
        self.history = []

        self.create_widgets()

    def create_widgets(self):
        """Build the calculator interface - tried to make it look decent"""

        # Display area
        display_frame = tk.Frame(self.window, bg='#2c3e50')
        display_frame.pack(pady=20, padx=20, fill='x')

        # Main display
        self.display_var = tk.StringVar(value="0")
        self.display = tk.Entry(display_frame, textvariable=self.display_var,
                                font=('Consolas', 24, 'bold'),  # Digital-7 swapped for safety
                                justify='right', state='readonly',
                                bg='#1a252f', fg='#00ff00',
                                bd=0, highlightthickness=2,
                                highlightcolor='#3498db')
        self.display.pack(fill='x', ipady=10)

        # Small history display
        self.history_var = tk.StringVar(value="")
        history_label = tk.Label(display_frame, textvariable=self.history_var,
                                 font=('Arial', 10), bg='#2c3e50', fg='#95a5a6',
                                 anchor='e')
        history_label.pack(fill='x', pady=(5, 0))

        # Button frame
        button_frame = tk.Frame(self.window, bg='#2c3e50')
        button_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Button styles
        num_style = {'font': ('Arial', 16, 'bold'), 'bg': '#34495e', 'fg': 'white',
                     'activebackground': '#4a6a7a', 'bd': 1, 'relief': 'raised'}

        op_style = {'font': ('Arial', 16, 'bold'), 'bg': '#e67e22', 'fg': 'white',
                    'activebackground': '#d35400', 'bd': 1, 'relief': 'raised'}

        special_style = {'font': ('Arial', 14, 'bold'), 'bg': '#27ae60', 'fg': 'white',
                         'activebackground': '#229954', 'bd': 1, 'relief': 'raised'}

        clear_style = {'font': ('Arial', 14, 'bold'), 'bg': '#e74c3c', 'fg': 'white',
                       'activebackground': '#c0392b', 'bd': 1, 'relief': 'raised'}

        # --- Buttons ---
        # Row 1
        row1 = tk.Frame(button_frame, bg='#2c3e50'); row1.pack(fill='x', pady=2)
        tk.Button(row1, text="C", command=self.clear_all, **clear_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row1, text="±", command=self.sign_change, **special_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row1, text="√", command=self.sqrt, **special_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row1, text="÷", command=lambda: self.operation("/"), **op_style).pack(side='left', fill='both', expand=True, padx=2)

        # Row 2
        row2 = tk.Frame(button_frame, bg='#2c3e50'); row2.pack(fill='x', pady=2)
        for num in ["7", "8", "9"]:
            tk.Button(row2, text=num, command=lambda n=num: self.number_input(n), **num_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row2, text="×", command=lambda: self.operation("*"), **op_style).pack(side='left', fill='both', expand=True, padx=2)

        # Row 3
        row3 = tk.Frame(button_frame, bg='#2c3e50'); row3.pack(fill='x', pady=2)
        for num in ["4", "5", "6"]:
            tk.Button(row3, text=num, command=lambda n=num: self.number_input(n), **num_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row3, text="−", command=lambda: self.operation("-"), **op_style).pack(side='left', fill='both', expand=True, padx=2)

        # Row 4
        row4 = tk.Frame(button_frame, bg='#2c3e50'); row4.pack(fill='x', pady=2)
        for num in ["1", "2", "3"]:
            tk.Button(row4, text=num, command=lambda n=num: self.number_input(n), **num_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row4, text="+", command=lambda: self.operation("+"), **op_style).pack(side='left', fill='both', expand=True, padx=2)

        # Row 5
        row5 = tk.Frame(button_frame, bg='#2c3e50'); row5.pack(fill='x', pady=2)
        tk.Button(row5, text="0", command=lambda: self.number_input("0"), **num_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row5, text=".", command=lambda: self.number_input("."), **num_style).pack(side='left', fill='both', expand=True, padx=2)
        tk.Button(row5, text="=", command=self.calculate_result, **op_style).pack(side='left', fill='both', expand=True, padx=2, pady=2, ipadx=20)

        # Bind keyboard events
        self.window.bind('<Key>', self.key_press)
        self.window.bind('<BackSpace>', self.backspace)
        self.window.bind('<Escape>', lambda e: self.clear_all())
        self.window.focus_set()

    # --- Core logic ---
    def number_input(self, num):
        if self.result:
            self.current = ""
            self.result = False

        if self.input_value:
            self.current = ""
            self.input_value = False

        if num == "." and "." in self.current:
            return

        self.current += str(num)
        self.display_var.set(self.current)

    def clear_all(self):
        self.current = ""
        self.total = 0
        self.input_value = True
        self.result = False
        self.operation_pending = None
        self.display_var.set("0")
        self.history_var.set("")

    def operation(self, op):
        if self.current:
            if self.operation_pending and not self.input_value:
                self.calculate_result()
            else:
                self.total = float(self.current)

        self.operation_pending = op
        self.input_value = True
        self.result = False
        self.history_var.set(f"{self.format_number(self.total)} {op}")

    def calculate_result(self):
        if self.operation_pending and self.current:
            try:
                left = self.total
                current_num = float(self.current)

                if self.operation_pending == "+":
                    self.total = left + current_num
                elif self.operation_pending == "-":
                    self.total = left - current_num
                elif self.operation_pending == "*":
                    self.total = left * current_num
                elif self.operation_pending == "/":
                    if current_num == 0:
                        messagebox.showerror("Error", "Can't divide by zero! That's like, math 101.")
                        return
                    self.total = left / current_num

                calculation = f"{self.format_number(left)} {self.operation_pending} {self.format_number(current_num)} = {self.format_number(self.total)}"
                self.history.append(calculation)

                self.current = str(self.total)
                self.display_var.set(self.format_number(self.total))
                self.history_var.set(f"= {self.format_number(self.total)}")

                self.result = True
                self.input_value = True
                self.operation_pending = None  # reset after result

            except Exception as e:
                messagebox.showerror("Error", f"Something went wrong: {e}")
                self.clear_all()

    def sqrt(self):
        target = self.current or str(self.total)
        if target:
            try:
                num = float(target)
                if num < 0:
                    messagebox.showerror("Error", "Can't take square root of negative number!")
                    return

                result = math.sqrt(num)
                self.current = str(result)
                self.display_var.set(self.format_number(result))
                self.history_var.set(f"√{self.format_number(num)} = {self.format_number(result)}")
                self.result = True

            except Exception as e:
                messagebox.showerror("Error", f"Error calculating square root: {e}")

    def sign_change(self):
        if self.current and self.current != "0":
            if self.current.startswith("-"):
                self.current = self.current[1:]
            else:
                self.current = "-" + self.current
            self.display_var.set(self.current)

    def backspace(self, event=None):
        if not self.input_value and self.current:
            self.current = self.current[:-1] or "0"
            self.display_var.set(self.current)

    def format_number(self, num):
        if isinstance(num, float):
            if num.is_integer():
                return str(int(num))
            else:
                return f"{num:.8g}"
        return str(num)

    def key_press(self, event):
        key = event.char
        if key.isdigit():
            self.number_input(key)
        elif key == ".":
            self.number_input(".")
        elif key == "+":
            self.operation("+")
        elif key == "-":
            self.operation("-")
        elif key in ["*", "x", "X"]:
            self.operation("*")
        elif key == "/":
            self.operation("/")
        elif key in ["\r", "="]:
            self.calculate_result()
        elif key in ["c", "C"]:
            self.clear_all()

    def run(self):
        self.window.mainloop()


def main():
    calc = Calculator()
    calc.run()


if __name__ == "__main__":
    main()
