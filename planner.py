"""
Personal Planner Application
Author: Burhan Sabuwala
Date: Jan 24, 2025

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License.
You are free to share and adapt this code for non-commercial purposes, provided that you give appropriate credit 
and indicate if changes were made. For more details, visit: 

https://creativecommons.org/licenses/by-nc/4.0/
"""


import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, simpledialog, messagebox, filedialog
from datetime import datetime
import subprocess
import calendar
import json
import os
import re

# Function to add task to todo list
def add_task(event=None):
    task_text = todo_entry.get().strip()
    if task_text:
        task_var = tk.StringVar(value=task_text)
        task_frame = tk.Frame(todo_frame, bg = univ_bg)
        task_frame.pack(anchor="w", pady = 2, fill ="x")

        task_checkbox = tk.Checkbutton(task_frame, text=task_text, variable=tk.IntVar(), 
                                       font=("Helvetica", 20), command=lambda: toggle_task(task_var, task_checkbox))
        task_checkbox.configure(bg = univ_bg)
        task_checkbox.pack(anchor='w', pady=2)
        #task_checkbox.pack(side = "left", padx = 5, fill = "x", expand = True)
        task_checkbox.bind("<Button-3>", lambda e: show_remove_menu(e,task_frame, task_var))
        todo_tasks.append((task_var, task_frame))
        todo_entry.delete(0, tk.END)

def show_remove_menu(event, task_frame, task_var):
    remove_menu = tk.Menu(root, tearoff = 0)
    remove_menu.add_command(label="Remove Task", command=lambda: remove_task(task_frame, task_var))
    remove_menu.post(event.x_root, event.y_root)
    root.bind("<Button-1>", lambda event: close_menu(event, remove_menu))

def close_menu(event, menu):
    menu.unpost()
    root.unbind("<Button-1>")

# Function to remove a task
def remove_task(task_frame, task_var):
    for task in todo_tasks:
        if task[0] == task_var:
            task[1].destroy()  # Remove the whole frame (task + button)
            todo_tasks.remove(task)
            break


# Function to toggle task completion (strike-through effect)
def toggle_task(task_var, checkbox):
    if checkbox.var.get():
        checkbox.config(fg="lightgray", font=("Helvetica", 20, "overstrike"))
        task_var.set(f"✔ {task_var.get()}")
    else:
        checkbox.config(fg="black", font=("Helvetica", 20, "normal"))
        task_var.set(task_var.get().replace("✔ ", ""))


# Function to save current To-Do list and schedule
def save_data():
    data = {
        "todo_list": [{"task": task[0], "completed": task[1].var.get()} for task in todo_tasks],
        "schedule": [{"title": event["title"], "start": event["start"], "end": event["end"], "color": event["color"]} for event in scheduled_events]
    }

    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Success", f"Data saved to {file_path}")

# Function to load previously saved To-Do list and schedule
def load_data():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Clear existing tasks
        for task in todo_tasks:
            task[1].destroy()
        todo_tasks.clear()

        # Load To-Do List
        for task in data["todo_list"]:
            task_var = tk.StringVar(value=task["task"])
            task_checkbox = tk.Checkbutton(todo_frame, text=task["task"], variable=tk.IntVar(value=task["completed"]),
                                           font=("Helvetica", 20), command=lambda: toggle_task(task_var, task_checkbox))
            task_checkbox.pack(anchor='w', pady=2)
            todo_tasks.append((task["task"], task_checkbox))

        # Clear existing schedule
        for event in scheduled_events:
            event["widget"].destroy()
        scheduled_events.clear()

        # Load Schedule
        for event in data["schedule"]:
            create_event(event["title"], event["start"], event["end"], event["color"])

        messagebox.showinfo("Success", "Data loaded successfully!")

# Function to add event using dropdown selections for hours and minutes
def add_event():
    event_window = tk.Toplevel(root)
    event_window.title("Add Event")
    event_window.geometry("350x500")

    tk.Label(event_window, text="Event Title:", font=("Helvetica", 20)).pack(pady=5)
    title_entry = tk.Entry(event_window, font=("Helvetica", 20))
    title_entry.pack(pady=5)

    tk.Label(event_window, text="Start Time:", font=("Helvetica", 20)).pack(pady=5)
    start_hour = ttk.Combobox(event_window, values=[f"{h:02}" for h in range(8, 20)], width=5, font=("Helvetica", 20))
    start_hour.pack( padx=5)
    start_minute = ttk.Combobox(event_window, values=[f"{m:02}" for m in range(0, 60, 15)], width=5, font=("Helvetica", 20))
    start_minute.pack(padx=5)

    tk.Label(event_window, text="End Time:", font=("Helvetica", 20)).pack(pady=5)
    end_hour = ttk.Combobox(event_window, values=[f"{h:02}" for h in range(8, 20)], width=5, font=("Helvetica", 20))
    end_hour.pack(padx=5)
    end_minute = ttk.Combobox(event_window, values=[f"{m:02}" for m in range(0, 60, 15)], width=5, font=("Helvetica", 20))
    end_minute.pack(padx=5)

    # Background color selection dropdown
    tk.Label(event_window, text="Select Background Color:", font=("Helvetica", 20)).pack(pady=5)
    color_options = ["lightblue", "lightgreen", "yellow", "pink", "orange", "grey"]
    color_var = tk.StringVar(value="lightblue")  # Default value
    color_dropdown = ttk.Combobox(event_window, textvariable=color_var, values=color_options, font=("Helvetica", 20))
    color_dropdown.pack(padx=5)

    def submit_event():
        title = title_entry.get().strip()
        start = f"{start_hour.get()}:{start_minute.get()}"
        end = f"{end_hour.get()}:{end_minute.get()}"
        selected_color = color_var.get()

        if title and start_hour.get() and end_hour.get():
            start_idx = int(start_hour.get()) - 8 + (int(start_minute.get()) / 60)
            end_idx = int(end_hour.get()) - 8 + (int(end_minute.get()) / 60)

            if start_idx < end_idx:
                event_label = tk.Label(schedule_frame, text=f"{title}", bg=selected_color, relief="ridge", font = ("Helvetica", 16))
                event_label.place(relx=0.35, rely=start_idx / 12, relwidth=0.60, relheight=(end_idx - start_idx) / 12)
                event_window.destroy()
            else:
                messagebox.showerror("Error", "End time must be after start time.")
        else:
            messagebox.showerror("Error", "Please enter valid details.")

    tk.Button(event_window, text="Add Event", command=submit_event, font=("Helvetica", 20)).pack(pady=10)



# Function to open the notes window
def open_notes_window():
    notes_window = tk.Toplevel(root)
    notes_window.title("Markdown Notes")
    notes_window.geometry("700x600")

    # Title input
    tk.Label(notes_window, text="Notes Title:", font=("Helvetica", 20, "bold")).pack(pady=5)
    title_entry = tk.Entry(notes_window, font=("Helvetica", 20), width=40)
    title_entry.pack(pady=5, padx=10, fill="x")

    # Markdown text area with scrollbar
    tk.Label(notes_window, text="Notes in Markdown:", font=("Helvetica", 20, "bold")).pack(pady=5)

    text_frame = tk.Frame(notes_window)
    text_frame.pack(expand=True, fill="both", padx=10, pady=10)

    text_scrollbar = tk.Scrollbar(text_frame, orient="vertical", width=20)
    notes_text = tk.Text(text_frame, font=("Helvetica", 18), wrap="word", yscrollcommand = text_scrollbar.set)
    text_scrollbar.config(command = notes_text.yview)
    text_scrollbar.pack(side="right", fill = "y")
    notes_text.pack(side ="left", expand = True, fill = "both")

    metadata_label = tk.Label(notes_window, text="", font=("Helvetica", 16), fg="gray")
    metadata_label.pack(pady=5)

    # Function to save the file
    def save_notes(file_path=None):
        if not file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md")])
        if file_path:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                metadata_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
                if metadata_match:
                    metadata = metadata_match.group(1)
                    created_date = re.search(r'Date Created: (.*)', metadata).group(1)
                    title = re.search(r'Title: (.*)', metadata).group(1)
                else:
                    created_date = now
                    title = title_entry.get().strip() or "Untitled"
                last_modified = now
            else:
                created_date = now
                last_modified = now
                title = title_entry.get().strip() or "Untitled"

            markdown_content = f"""---
Title: {title}
Date Created: {created_date}
Last Modified: {last_modified}
---

{notes_text.get("1.0", tk.END).strip()}
"""

            with open(file_path, 'w') as f:
                f.write(markdown_content)

            messagebox.showinfo("Success", f"Notes saved at {file_path}")

            pdf_path = file_path.replace(".md", ".pdf")
            try:
                subprocess.run(["pandoc", file_path, "-o", pdf_path], check=True)
                messagebox.showinfo("Success", f"PDF saved at {pdf_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert to PDF: {e}")

    # Function to open an existing markdown file
    def open_notes():
        file_path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
        if file_path:
            with open(file_path, 'r') as f:
                content = f.read()

            metadata_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
            if metadata_match:
                metadata = metadata_match.group(1)
                content_body = content[len(metadata_match.group(0)):].strip()
                
                title = re.search(r'Title: (.*)', metadata).group(1)
                created_date = re.search(r'Date Created: (.*)', metadata).group(1)
                last_modified = re.search(r'Last Modified: (.*)', metadata).group(1)
                
                title_entry.delete(0, tk.END)
                title_entry.insert(0, title)
                metadata_label.config(text=f"Created: {created_date} | Last Modified: {last_modified}")
                notes_text.delete("1.0", tk.END)
                notes_text.insert("1.0", content_body)
            else:
                messagebox.showerror("Error", "Invalid or missing metadata in file.")

    # Function to select all text
    def select_all(event=None):
        notes_text.tag_add("sel", "1.0", "end")
        return "break"

    # Function to clear all content
    def clear_all():
        notes_text.delete("1.0", tk.END)

    def close_menu(event, menu):
        menu.unpost()
        notes_window.unbind("<Button-1>")

    # Keyboard shortcuts
    notes_window.bind("<Control-s>", lambda event: save_notes())  # Ctrl+S to save
    notes_window.bind("<Control-a>", select_all)  # Ctrl+A to select all
    notes_window.bind("<Control-b>", lambda event: format_text("**", "**"))  # Ctrl+B for bold
    notes_window.bind("<Control-i>", lambda event: format_text("*", "*"))  # Ctrl+I for italics
    notes_window.bind("<Control-u>", lambda event: format_text("__", "__"))  # Ctrl+U for underline

    # Right-click menu
    def show_context_menu(event):
        context_menu = tk.Menu(notes_window, tearoff=0)
        context_menu.add_command(label="Bold (Ctrl+B)", command=lambda: format_text("**", "**"))
        context_menu.add_command(label="Italic (Ctrl+I)", command=lambda: format_text("*", "*"))
        context_menu.add_command(label="Underline (Ctrl+U)", command=lambda: format_text("__", "__"))
        context_menu.add_separator()
        context_menu.add_command(label="Save", command=lambda: save_notes())
        context_menu.add_command(label="Save As", command=lambda: save_notes(None))
        context_menu.add_command(label="Open", command=open_notes)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: select_all())
        context_menu.add_command(label="Clear All", command=clear_all)
        context_menu.post(event.x_root, event.y_root)
        notes_window.bind("<Button-1>", lambda event: close_menu(event, context_menu))


    notes_text.bind("<Button-3>", show_context_menu)
    notes_window.bind("<Button-1>", lambda event: close_menu(event, context_menu))

    # Buttons for saving and opening notes
    button_frame = tk.Frame(notes_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Save Notes", command=lambda: save_notes(), font=("Helvetica", 18)).pack(side="left", padx=10)
    tk.Button(button_frame, text="Open Notes", command=open_notes, font=("Helvetica", 18)).pack(side="left", padx=10)



# Function to switch between day and night modes
def toggle_theme():
    if theme_switch.get():
        univ_bg = "#231123"
        text_color = "#da4167"
        schedule_color = "#3E0F06"
        button_color = "#3B5360"

    else:
        univ_bg = "#FFECD8"
        text_color = "#381d2a"
        schedule_color = "#88D5D3"
        button_color = "#E3E6B5"


    # Apply the new background color
    root.config(bg=univ_bg)
    header_label.configure(bg=univ_bg, fg= text_color)
    left_frame.configure(bg=univ_bg)
    todo_label.configure(bg=univ_bg, fg = text_color)
    todo_frame.configure(bg=univ_bg)
    right_frame.configure(bg=univ_bg)
    schedule_label.configure(bg=univ_bg, fg = text_color)
    schedule_frame.configure(bg=univ_bg)
    button_frame.configure(bg=univ_bg)

    for task in todo_tasks:
        task[1].configure(bg = univ_bg, fg = text_color)

    for widget in schedule_frame.winfo_children():
        widget.configure(bg = schedule_color, fg = text_color)

    # update button
    add_event_btn.configure(bg = button_color, fg = text_color)
    save_btn.configure(bg = button_color, fg = text_color)
    load_btn.configure(bg = button_color, fg = text_color)
    notes_btn.configure(bg = button_color, fg = text_color)


def update_time_indicator():
    """Function to update the position of the time indicator line."""
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    # Convert current time to relative position in the schedule
    if 8 <= current_hour < 20:
        time_position = ((current_hour - 8) + (current_minute / 60)) / 12
        time_indicator.place(relx=0, rely=time_position, relwidth=2, height=2)
    else:
        time_indicator.place_forget()

    # Update every minute
    schedule_frame.after(60000, update_time_indicator)


def change_style(theme):
    # Change style
    style.theme_use(theme)

# Function to update the calendar display for the selected month and year
def update_calendar(year, month):
    now = datetime.now()
    today = now.day if year == now.year and month == now.month else None
    
    cal = calendar.monthcalendar(year, month)
    cal_text = f"{calendar.month_name[month]} {year}\n\n"
    cal_text += " Mo  Tu  We  Th  Fr  Sa  Su \n"
    
    for week in cal:
        for day in week:
            if day == today:
                cal_text += f" {day:2d}*"
            elif day == 0:
                cal_text += "    "
            else:
                cal_text += f" {day:2d} "
        cal_text += "\n"
    
    calendar_label.config(text=cal_text)
    month_var.set(calendar.month_name[month])
    year_var.set(year)
# Function to select a month from the dropdown
def select_month(event):
    global current_month, current_year
    selected_month = month_var.get()
    current_month = list(calendar.month_name).index(selected_month)
    update_calendar(current_year, current_month)

# Function to select a year from the dropdown
def select_year(event):
    global current_month, current_year
    current_year = int(year_var.get())
    update_calendar(current_year, current_month)

# Function to show the calendar window
def open_calendar():
    global calendar_label, current_month, current_year, month_var, year_var

    # Get current date
    now = datetime.now()
    current_year, current_month = now.year, now.month

    # Create calendar window
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Calendar")
    calendar_window.geometry("400x450")
    
    header_frame = tk.Frame(calendar_window)
    header_frame.pack(pady=10)

    # Month selection dropdown
    month_var = tk.StringVar(value=calendar.month_name[current_month])
    month_menu = ttk.Combobox(header_frame, textvariable=month_var, values=list(calendar.month_name)[1:], font=("HyperFont", 20), width = 10, state="readonly")
    month_menu.pack(side="left", padx=10)
    month_menu.bind("<<ComboboxSelected>>", select_month)

    # Year selection dropdown
    year_var = tk.StringVar(value=str(current_year))
    year_menu = ttk.Combobox(header_frame, textvariable=year_var, values=[str(y) for y in range(1900, 2100)], font=("HyperFont", 20), width = 10, state="readonly")
    year_menu.pack(side="left", padx=10)
    year_menu.bind("<<ComboboxSelected>>", select_year)

    # Calendar display
    calendar_label = tk.Label(calendar_window, font=("HyperFont", 20), justify="left")
    calendar_label.pack(pady=10)

    update_calendar(current_year, current_month)


univ_bg = "#FFECD8"
text_color = "#381d2a"
schedule_color = "#88D5D3"
button_color = "#E3E6B5"

# Main application window
root = ThemedTk()
root.title("Planner")
root.geometry("850x760")

root.config(bg = univ_bg)

style = ttk.Style(root)
style.theme_use("alt")
our_themes = ttk.Style().theme_names() 
our_themes2 = root.get_themes()

my_menu = tk.Menu(root)
root.config(menu = my_menu)

theme_menu = tk.Menu(my_menu)


calendar_menu = tk.Menu(my_menu)
my_menu.add_cascade(label = "Themes", menu = theme_menu, font= ("Helvetica", 24))
my_menu.add_cascade(label = "Calendar", menu = calendar_menu, font = ("Helvetica", 24))

calendar_menu.add_command(label = "Open Calendar", command = open_calendar, font = ("Helvetica", 24))

for t in our_themes2:
    theme_menu.add_command(label = t, command = lambda t=t: change_style(t), font = ("Helvetica", 24))

# Top date label
current_date = datetime.now().strftime("%B %d, %Y | %A")
header_label = tk.Label(root, text=current_date, font=("Helvetica", 30), anchor="center")
header_label.configure(bg = univ_bg)
header_label.pack(pady=10)

# Create the main layout frames
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Left column for Todo List
left_frame = tk.Frame(main_frame, width=300, padx=10, pady=10)
left_frame.configure(bg = univ_bg)
left_frame.pack(side="left", fill="y")

todo_label = tk.Label(left_frame, text="To-Do List", font=("Helvetica", 24, "bold"))
todo_label.configure(bg=univ_bg)
todo_label.pack()

todo_entry = tk.Entry(left_frame, width=30, font=("Helvetica", 20))
todo_entry.configure(bg = univ_bg)
todo_entry.pack(pady=5)
todo_entry.bind("<Return>", add_task)

todo_frame = tk.Frame(left_frame)
todo_frame.configure(bg = univ_bg)
todo_frame.pack(pady=5, fill="both", expand=True)

todo_tasks = []

# Right column for Scheduler
right_frame = tk.Frame(main_frame, padx=10, pady=10)
right_frame.configure(bg = univ_bg)
right_frame.pack(side="right", fill="both", expand=True)

schedule_label = tk.Label(right_frame, text="Schedule", font=("Helvetica", 24, "bold"))
schedule_label.configure(bg = univ_bg)
schedule_label.pack()

schedule_frame = tk.Frame(right_frame, width=450, height=400, bd=1, relief="solid")
schedule_frame.pack(pady=5)
schedule_frame.configure(bg = univ_bg)

schedule_events = []

# Display scheduler time slots
hours = [f"{h}:00 AM" if h < 12 else f"{h-12}:00 PM" if h >12 else f"12:00 PM" for h in range(8, 20)]
for idx, hour in enumerate(hours):
    lbl = tk.Label(schedule_frame, text=hour, anchor="w", font=("Arial", 18), relief="ridge")
    lbl.configure(bg = schedule_color)
    lbl.place(relx=0, rely=idx/len(hours), relwidth=0.35, relheight=1/len(hours))

# Add real-time blue line indicator for current time
time_indicator = tk.Canvas(schedule_frame, height=2, bg = "red")
time_indicator.config(bg = "red")
time_indicator.place(relx=0, rely=0, relwidth=1, height=2)

# Start the time tracker
update_time_indicator()

add_event_btn = tk.Button(right_frame, text="Add Event", command=add_event, font=("Helvetica", 20), )
add_event_btn.configure(bg = button_color, fg = text_color)
add_event_btn.pack(pady=5)

# Button to open Notes Window
notes_btn = tk.Button(root, text="Open Notes", command=open_notes_window, font=("Helvetica", 20))
notes_btn.configure(bg = button_color, fg = text_color)
notes_btn.pack(pady=5)



# Add Save and Load Buttons
button_frame = tk.Frame(root)
button_frame.configure(bg = univ_bg)
button_frame.pack(pady=5)

save_btn = tk.Button(button_frame, text="Save", command=save_data, font=("Helvetica", 20))
save_btn.configure(bg = button_color, fg = text_color)
save_btn.pack(side="left", padx=10)

load_btn = tk.Button(button_frame, text="Load", command=load_data, font=("Helvetica", 20))
load_btn.configure(bg = button_color, fg = text_color)
load_btn.pack(side="left", padx=10)

# Day/Night Mode Toggle
theme_switch = tk.BooleanVar(value=False)
toggle_button = tk.Checkbutton(root, text="Night Mode", variable=theme_switch, command=toggle_theme, font = ("Helvetica", 20))
toggle_button.configure(bg = button_color, fg = text_color)
toggle_button.pack(pady=10)

# Run the application
root.mainloop()
