import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, simpledialog, messagebox, filedialog
from datetime import datetime
import subprocess

# Function to add task to todo list
def add_task(event=None):
    task_text = todo_entry.get().strip()
    if task_text:
        task_var = tk.StringVar(value=task_text)
        task_checkbox = tk.Checkbutton(todo_frame, text=task_text, variable=tk.IntVar(), 
                                       font=("Helvetica", 20), command=lambda: toggle_task(task_var, task_checkbox))
        task_checkbox.pack(anchor='w', pady=2)
        todo_tasks.append((task_var, task_checkbox))
        todo_entry.delete(0, tk.END)

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
    notes_window.geometry("500x400")

    tk.Label(notes_window, text="Notes in Markdown:", font=("Helvetica", 24, "bold")).pack(pady=5)
    notes_text = tk.Text(notes_window, font=("Helvetica", 24), wrap="word")
    notes_text.pack(expand=True, fill="both", padx=10, pady=10)

    def save_notes():
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(notes_text.get("1.0", tk.END))
            messagebox.showinfo("Success", f"Notes saved at {file_path}")
            
            # Convert to PDF using Pandoc
            pdf_path = file_path.replace(".md", ".pdf")
            try:
                subprocess.run(["pandoc", file_path, "-o", pdf_path], check=True)
                messagebox.showinfo("Success", f"PDF saved at {pdf_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert to PDF: {e}")

    tk.Button(notes_window, text="Save Notes", command=save_notes, font=("Helvetica", 20)).pack(pady=5)

# Function to switch between day and night modes
def toggle_theme():
    if theme_switch.get():
        root.config(bg="black")
        header_label.config(bg="black", fg="white")
        todo_label.config(bg="black", fg="white")
        schedule_label.config(bg="black", fg="white")
    else:
        root.config(bg="white")
        header_label.config(bg="white", fg="black")
        todo_label.config(bg="white", fg="black")
        schedule_label.config(bg="white", fg="black")


def update_time_indicator():
    """Function to update the position of the time indicator line."""
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    # Convert current time to relative position in the schedule
    if 8 <= current_hour < 20:
        time_position = ((current_hour - 8) + (current_minute / 60)) / 12
        time_indicator.place(relx=0, rely=time_position, relwidth=1, height=2)
    else:
        time_indicator.place_forget()

    # Update every minute
    schedule_frame.after(60000, update_time_indicator)


def change_style(theme):
    # Change style
    style.theme_use(theme)

# Main application window
root = ThemedTk()
root.title("Scheduler")
root.geometry("850x700")

style = ttk.Style(root)
style.theme_use("alt")
our_themes = ttk.Style().theme_names() 
our_themes2 = root.get_themes()

my_menu = tk.Menu(root)
root.config(menu = my_menu)

theme_menu = tk.Menu(my_menu)
my_menu.add_cascade(label = "Themes", menu = theme_menu)

for t in our_themes2:
    theme_menu.add_command(label = t, command = lambda t=t: change_style(t))

# Top date label
current_date = datetime.now().strftime("%B %d, %Y")
header_label = tk.Label(root, text=current_date, font=("Helvetica", 30), anchor="center")
header_label.pack(pady=10)

# Create the main layout frames
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Left column for Todo List
left_frame = tk.Frame(main_frame, width=300, padx=10, pady=10)
left_frame.pack(side="left", fill="y")

todo_label = tk.Label(left_frame, text="To-Do List", font=("Helvetica", 24, "bold"))
todo_label.pack()

todo_entry = tk.Entry(left_frame, width=30, font=("Helvetica", 20))
todo_entry.pack(pady=5)
todo_entry.bind("<Return>", add_task)

todo_frame = tk.Frame(left_frame)
todo_frame.pack(pady=5, fill="both", expand=True)

todo_tasks = []

# Right column for Scheduler
right_frame = tk.Frame(main_frame, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

schedule_label = tk.Label(right_frame, text="Scheduler", font=("Helvetica", 24, "bold"))
schedule_label.pack()

schedule_frame = tk.Frame(right_frame, width=450, height=400, bd=1, relief="solid")
schedule_frame.pack(pady=5)

schedule_events = []

# Display scheduler time slots
hours = [f"{h}:00 AM" if h < 12 else f"{h-12}:00 PM" if h >12 else f"12:00 PM" for h in range(8, 20)]
for idx, hour in enumerate(hours):
    lbl = tk.Label(schedule_frame, text=hour, anchor="w", font=("Arial", 18), relief="ridge")
    lbl.place(relx=0, rely=idx/len(hours), relwidth=0.35, relheight=1/len(hours))

# Add real-time blue line indicator for current time
time_indicator = tk.Canvas(schedule_frame, height=2, bg="blue")
time_indicator.place(relx=0, rely=0, relwidth=1, height=2)

# Start the time tracker
update_time_indicator()

add_event_btn = tk.Button(right_frame, text="Add Event", command=add_event, font=("Helvetica", 20))
add_event_btn.pack(pady=5)

# Button to open Notes Window
notes_btn = tk.Button(root, text="Open Notes", command=open_notes_window, font=("Helvetica", 20))
notes_btn.pack(pady=5)

# Day/Night Mode Toggle
#theme_switch = tk.BooleanVar(value=False)
#toggle_button = ttk.Checkbutton(root, text="Night Mode", variable=theme_switch, command=toggle_theme, font = ("Helvetica", 20))
#toggle_button.pack(pady=10)

# Add Save and Load Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

save_btn = tk.Button(button_frame, text="Save Schedule", command=save_data, font=("Helvetica", 20))
save_btn.pack(side="left", padx=10)

load_btn = tk.Button(button_frame, text="Load Schedule", command=load_data, font=("Helvetica", 20))
load_btn.pack(side="left", padx=10)

# Run the application
root.mainloop()
