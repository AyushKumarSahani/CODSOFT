# made this because my phone contacts app annoys me :)

import tkinter as tk
from tkinter import messagebox
import json
from json import JSONDecodeError
import re
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import uuid


class ContactManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("My Contact Manager - Never Lose A Number Again")
        self.root.geometry("850x600")
        self.root.configure(bg="#f8fafc")

        # keep data next to this script
        self.data_dir = Path(__file__).resolve().parent
        self.contacts_file = self.data_dir / "contacts.json"

        # in-memory contacts
        self.contacts = self.load_contacts()

        # the contact currently selected in the list
        self.selected_contact = None

        # search box state
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_contacts)

        self.setup_ui()
        self.refresh_contact_list()

    # ---------- data stuff ----------

    def load_contacts(self):
        """read contacts from disk (if file exists); handle corrupt/empty gracefully"""
        if not self.contacts_file.exists():
            return []
        try:
            with self.contacts_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("contacts", [])
        except (JSONDecodeError, OSError) as e:
            messagebox.showwarning(
                "Load warning",
                f"Contacts file unreadable.\nStarting fresh.\n\n{e}"
            )
            return []

    def save_contacts(self):
        """atomic write so we don't lose data mid-save"""
        try:
            payload = {
                "contacts": self.contacts,
                "last_saved": datetime.now().isoformat(timespec="seconds"),
                "count": len(self.contacts),
            }
            # write to a temp file, then move into place
            tmp = tempfile.NamedTemporaryFile(
                "w", delete=False, dir=self.data_dir, encoding="utf-8"
            )
            with tmp as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            shutil.move(tmp.name, self.contacts_file)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save contacts:\n{e}")
            return False

    # ---------- small helpers ----------

    def _clean_phone(self, s):
        """keep digits and common symbols, nothing wild"""
        return re.sub(r"[^\d+\-\(\)\s]", "", s or "").strip()

    def _digits(self, s):
        return re.sub(r"\D", "", s or "")

    def _valid_email(self, s):
        if not s:
            return True  # email is optional
        return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$", s) is not None

    def _filtered_contacts(self):
        """what the list is currently showing (based on search)"""
        term = (self.search_var.get() or "").lower()
        result = []
        for c in self.contacts:
            name = (c.get("name") or "").lower()
            phone = (c.get("phone") or "").lower()
            email = (c.get("email") or "").lower()
            if term in name or term in phone or term in email:
                result.append(c)
        # sort alphabetically by name (case-insensitive)
        result.sort(key=lambda x: (x.get("name") or "").lower())
        return result

    # ---------- ui ----------

    def setup_ui(self):
        # header
        header = tk.Frame(self.root, bg="#2563eb", height=68)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="📞 Contact Manager", font=("Segoe UI", 20, "bold"), fg="white", bg="#2563eb"
        ).pack(pady=16)

        # main area
        main = tk.Frame(self.root, bg="#f8fafc")
        main.pack(fill="both", expand=True, padx=14, pady=14)

        # left pane (search + list)
        left = tk.Frame(main, bg="white", relief="solid", bd=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        search_box = tk.Frame(left, bg="white")
        search_box.pack(fill="x", padx=14, pady=10)
        tk.Label(search_box, text="🔍 Search", font=("Segoe UI", 11, "bold"), bg="white").pack(anchor="w")

        self.search_entry = tk.Entry(
            search_box, textvariable=self.search_var, font=("Segoe UI", 10), bd=1, relief="solid"
        )
        self.search_entry.pack(fill="x", pady=(5, 0))

        list_wrap = tk.Frame(left, bg="white")
        list_wrap.pack(fill="both", expand=True, padx=14, pady=(10, 14))
        tk.Label(list_wrap, text="📋 Contacts", font=("Segoe UI", 11, "bold"), bg="white").pack(anchor="w")

        list_container = tk.Frame(list_wrap, bg="white")
        list_container.pack(fill="both", expand=True, pady=(5, 0))

        scroll = tk.Scrollbar(list_container)
        scroll.pack(side="right", fill="y")

        self.contact_listbox = tk.Listbox(
            list_container, yscrollcommand=scroll.set, font=("Segoe UI", 10), selectmode="single", bd=1, relief="solid"
        )
        self.contact_listbox.pack(side="left", fill="both", expand=True)
        self.contact_listbox.bind("<<ListboxSelect>>", self.on_contact_select)

        scroll.config(command=self.contact_listbox.yview)

        # right pane (form + buttons)
        right = tk.Frame(main, bg="white", relief="solid", bd=1)
        right.pack(side="right", fill="both", expand=True)

        form = tk.LabelFrame(right, text="Contact Details", font=("Segoe UI", 11, "bold"), bg="white", fg="#1f2937")
        form.pack(fill="both", expand=True, padx=14, pady=14)

        # form fields
        self.form_vars = {}
        fields = [("Name:", "name"), ("Phone:", "phone"), ("Email:", "email"), ("Address:", "address")]

        for label_text, key in fields:
            row = tk.Frame(form, bg="white")
            row.pack(fill="x", padx=10, pady=8)

            tk.Label(row, text=label_text, font=("Segoe UI", 10, "bold"), bg="white", width=8, anchor="w").pack(side="left")

            if key == "address":
                entry = tk.Text(row, height=3, font=("Segoe UI", 10), bd=1, relief="solid", wrap="word")
                entry.pack(side="right", fill="x", expand=True)
            else:
                entry = tk.Entry(row, font=("Segoe UI", 10), bd=1, relief="solid")
                entry.pack(side="right", fill="x", expand=True)

            self.form_vars[key] = entry

        # buttons (add/update/delete etc)
        btns = tk.Frame(right, bg="white")
        btns.pack(fill="x", padx=14, pady=(0, 14))

        row1 = tk.Frame(btns, bg="white")
        row1.pack(fill="x", pady=5)

        tk.Button(row1, text="➕ Add", command=self.add_contact, bg="#10b981", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left")

        tk.Button(row1, text="✏️ Update", command=self.update_contact, bg="#f59e0b", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)

        tk.Button(row1, text="🗑️ Delete", command=self.delete_contact, bg="#ef4444", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)

        row2 = tk.Frame(btns, bg="white")
        row2.pack(fill="x", pady=5)

        tk.Button(row2, text="🔄 Clear", command=self.clear_form, bg="#6b7280", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left")

        tk.Button(row2, text="💾 Export", command=self.export_contacts, bg="#8b5cf6", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left", padx=6)

        # status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w",
                 font=("Segoe UI", 9), bg="#e5e7eb").pack(side="bottom", fill="x")

        self.update_status(f"Loaded {len(self.contacts)} contacts")

    # ---------- list + selection ----------

    def refresh_contact_list(self):
        """redraw listbox items based on search"""
        self.contact_listbox.delete(0, tk.END)
        for c in self._filtered_contacts():
            name = c.get("name") or "No Name"
            phone = c.get("phone") or "No Phone"
            self.contact_listbox.insert(tk.END, f"{name} - {phone}")

        self.update_status(f"Showing {self.contact_listbox.size()} of {len(self.contacts)} contacts")

    def filter_contacts(self, *_):
        self.refresh_contact_list()

    def on_contact_select(self, _event):
        """when user clicks an item, load it into the form"""
        sel = self.contact_listbox.curselection()
        if not sel:
            return

        filtered = self._filtered_contacts()
        idx = sel[0]
        if idx >= len(filtered):
            return

        self.selected_contact = filtered[idx]  # remember which dict we picked
        self.load_contact_to_form(self.selected_contact)

    # ---------- form handling ----------

    def load_contact_to_form(self, contact):
        """put the contact values into the boxes"""
        # IMPORTANT: don't lose selection when clearing
        self.clear_form(reset_selection=False)

        self.form_vars["name"].insert(0, contact.get("name", ""))
        self.form_vars["phone"].insert(0, contact.get("phone", ""))
        self.form_vars["email"].insert(0, contact.get("email", ""))
        self.form_vars["address"].insert("1.0", contact.get("address", ""))

    def clear_form(self, reset_selection=True):
        """wipe inputs (optionally keep which contact is selected) + clear listbox selection"""
        self.form_vars["name"].delete(0, tk.END)
        self.form_vars["phone"].delete(0, tk.END)
        self.form_vars["email"].delete(0, tk.END)
        self.form_vars["address"].delete("1.0", tk.END)
        self.contact_listbox.selection_clear(0, tk.END)
        if reset_selection:
            self.selected_contact = None
        # UX: focus name box for fast typing
        self.form_vars["name"].focus_set()

    def get_form_data(self):
        """grab current form values and make a contact dict"""
        name = self.form_vars["name"].get().strip()
        phone = self._clean_phone(self.form_vars["phone"].get())
        email = self.form_vars["email"].get().strip()
        address = self.form_vars["address"].get("1.0", tk.END).strip()

        return {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            # stable unique id (won't collide after deletions)
            "id": str(uuid.uuid4()),
            "created": datetime.now().isoformat(timespec="seconds"),
        }

    def validate_contact(self, c):
        """make sure name + phone make sense"""
        problems = []
        if not c["name"]:
            problems.append("Name is required")
        if not c["phone"]:
            problems.append("Phone is required")
        elif len(self._digits(c["phone"])) < 7:
            problems.append("Phone number seems too short")
        if not self._valid_email(c["email"]):
            problems.append("Email format looks wrong")
        return problems

    # ---------- actions ----------

    def add_contact(self):
        newc = self.get_form_data()
        errs = self.validate_contact(newc)
        if errs:
            messagebox.showerror("Validation", "\n".join(errs))
            return

        # duplicate check: by name OR digits-only phone
        dupe = next(
            (
                c for c in self.contacts
                if (c.get("name", "").strip().lower() == newc["name"].lower())
                or (self._digits(c.get("phone")) == self._digits(newc["phone"]))
            ),
            None
        )
        if dupe and not messagebox.askyesno(
            "Possible duplicate", "Found a similar contact.\nAdd anyway?"
        ):
            return

        self.contacts.append(newc)
        if self.save_contacts():
            self.refresh_contact_list()
            self.clear_form()
            self.update_status(f"Added: {newc['name']}")
            messagebox.showinfo("Added", f"Contact '{newc['name']}' added.")

    def update_contact(self):
        if not self.selected_contact:
            messagebox.showwarning("No Selection", "Select a contact first.")
            return

        updated = self.get_form_data()
        errs = self.validate_contact(updated)
        if errs:
            messagebox.showerror("Validation", "\n".join(errs))
            return

        # keep original id/created if present
        updated["id"] = self.selected_contact.get("id", updated["id"])
        updated["created"] = self.selected_contact.get("created", updated["created"])
        updated["modified"] = datetime.now().isoformat(timespec="seconds")

        # replace the dict in the list
        for i, c in enumerate(self.contacts):
            if c is self.selected_contact:
                self.contacts[i] = updated
                self.selected_contact = updated  # point to the new dict
                break

        if self.save_contacts():
            self.refresh_contact_list()
            self.clear_form()
            self.update_status(f"Updated: {updated['name']}")
            messagebox.showinfo("Updated", f"Contact '{updated['name']}' updated.")
        # UX: focus back to name for quick edits
        self.form_vars["name"].focus_set()

    def delete_contact(self):
        """remove the selected contact from the list"""
        if not self.selected_contact:
            messagebox.showwarning("No Selection", "Select a contact to delete.")
            return

        name = self.selected_contact.get("name", "Unknown")
        if not messagebox.askyesno("Confirm Delete", f"Delete '{name}'?\nThis cannot be undone."):
            return

        try:
            self.contacts.remove(self.selected_contact)
            self.selected_contact = None
        except ValueError:
            pass

        if self.save_contacts():
            self.refresh_contact_list()
            self.clear_form()
            self.update_status(f"Deleted: {name}")
            messagebox.showinfo("Deleted", f"Contact '{name}' deleted.")

    def export_contacts(self):
        """dump a simple text file for backup / reading"""
        if not self.contacts:
            messagebox.showinfo("Export", "No contacts to export.")
            return

        filename = self.data_dir / f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with filename.open("w", encoding="utf-8") as f:
                f.write("CONTACT MANAGER EXPORT\n")
                f.write("=" * 40 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total: {len(self.contacts)}\n\n")
                for i, c in enumerate(self.contacts, start=1):
                    f.write(f"Contact #{i}\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Name: {c.get('name','')}\n")
                    f.write(f"Phone: {c.get('phone','')}\n")
                    f.write(f"Email: {c.get('email','')}\n")
                    f.write(f"Address: {c.get('address','')}\n")
                    f.write(f"Added: {c.get('created','')}\n\n")
            messagebox.showinfo("Export", f"Contacts exported to {filename.name}")
            self.update_status(f"Exported {len(self.contacts)} contacts → {filename.name}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Couldn't export:\n{e}")

    # ---------- app frame ----------

    def update_status(self, msg):
        self.status_var.set(f"Ready | {msg}")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # friendly hello (only first run)
        if not self.contacts:
            messagebox.showinfo(
                "Welcome!",
                "📞 Welcome to Contact Manager!\n\n"
                "How to start:\n"
                "• Fill the form on the right\n"
                "• Click 'Add'\n"
                "• Use Search to quickly find stuff\n\n"
                "Tips:\n"
                "• Name + Phone required\n"
                "• Email is optional (but validated)\n"
                "• Export makes a backup file\n\n"
                "Have fun organizing! 🚀"
            )
        self.root.mainloop()

    def on_close(self):
        self.save_contacts()
        self.root.destroy()


def main():
    app = ContactManager()
    app.run()


if __name__ == "__main__":
    main()
