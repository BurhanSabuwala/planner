"""
Personal Planner Application (PyQt Version)
Author: Burhan Sabuwala
Date: Jan 24, 2025

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License.
You are free to share and adapt this code for non-commercial purposes, provided that you give appropriate credit 
and indicate if changes were made. For more details, visit: 

https://creativecommons.org/licenses/by-nc/4.0/
"""

import sys
import csv
import os
import re
import subprocess
import calendar
from datetime import datetime

# PyQt imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox, QMenu, QAction, QDialog,
    QFileDialog, QTextEdit, QComboBox, QScrollArea, QFrame, QMenuBar,
    QCalendarWidget, QStyle, QSplitter, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSlot, QDateTime
from PyQt5.QtGui import QFont, QPainter, QPen, QColor


# ----------------------------- Dialog for Adding Events -----------------------------#
class AddEventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Event")
        self.setFixedSize(300, 420)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        self.title_label = QLabel("Event Title:")
        self.title_label.setFont(QFont("Helvetica", 14))
        self.title_edit = QLineEdit()
        self.title_edit.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_edit)

        # Start Time
        self.start_label = QLabel("Start Time:")
        self.start_label.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.start_label)

        self.start_hour_combo = QComboBox()
        self.start_minute_combo = QComboBox()
        self.start_hour_combo.setFont(QFont("Helvetica", 14))
        self.start_minute_combo.setFont(QFont("Helvetica", 14))
        for h in range(8, 20):
            self.start_hour_combo.addItem(f"{h:02}")
        for m in range(0, 60, 15):
            self.start_minute_combo.addItem(f"{m:02}")

        layout.addWidget(self.start_hour_combo)
        layout.addWidget(self.start_minute_combo)

        # End Time
        self.end_label = QLabel("End Time:")
        self.end_label.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.end_label)

        self.end_hour_combo = QComboBox()
        self.end_minute_combo = QComboBox()
        self.end_hour_combo.setFont(QFont("Helvetica", 14))
        self.end_minute_combo.setFont(QFont("Helvetica", 14))
        for h in range(8, 20):
            self.end_hour_combo.addItem(f"{h:02}")
        for m in range(0, 60, 15):
            self.end_minute_combo.addItem(f"{m:02}")

        layout.addWidget(self.end_hour_combo)
        layout.addWidget(self.end_minute_combo)

        # Color
        self.color_label = QLabel("Select Background Color:")
        self.color_label.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.color_label)

        self.color_combo = QComboBox()
        self.color_combo.setFont(QFont("Helvetica", 14))
        color_options = ["lightblue", "lightgreen", "yellow", "pink", "orange", "grey"]
        self.color_combo.addItems(color_options)
        layout.addWidget(self.color_combo)

        # Submit Button
        self.submit_button = QPushButton("Add Event")
        self.submit_button.setFont(QFont("Helvetica", 14))
        self.submit_button.clicked.connect(self.submit_event)
        layout.addWidget(self.submit_button)

    def submit_event(self):
        title = self.title_edit.text().strip()
        start_hour = self.start_hour_combo.currentText()
        start_minute = self.start_minute_combo.currentText()
        end_hour = self.end_hour_combo.currentText()
        end_minute = self.end_minute_combo.currentText()
        color = self.color_combo.currentText()

        if not title:
            QMessageBox.warning(self, "Error", "Please enter a valid event title.")
            return

        start_idx = int(start_hour) - 8 + (int(start_minute)/60)
        end_idx = int(end_hour) - 8 + (int(end_minute)/60)
        if start_idx >= end_idx:
            QMessageBox.warning(self, "Error", "End time must be after start time.")
            return

        # Gather data for the main window to place the event
        self.event_data = {
            "title": title,
            "start_idx": start_idx,
            "end_idx": end_idx,
            "color": color
        }
        self.accept()


# ----------------------------- Dialog for Markdown Notes -----------------------------#
class NotesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Markdown Notes")
        self.resize(700, 600)
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Title
        self.title_label = QLabel("Notes Title:")
        self.title_label.setFont(QFont("Helvetica", 16, QFont.Bold))
        self.main_layout.addWidget(self.title_label)

        self.title_edit = QLineEdit()
        self.title_edit.setFont(QFont("Helvetica", 16))
        self.main_layout.addWidget(self.title_edit)

        # Markdown Text
        self.notes_label = QLabel("Notes in Markdown:")
        self.notes_label.setFont(QFont("Helvetica", 16, QFont.Bold))
        self.main_layout.addWidget(self.notes_label)

        self.notes_text = QTextEdit()
        self.notes_text.setFont(QFont("Helvetica", 14))
        self.main_layout.addWidget(self.notes_text)

        # Metadata label
        self.metadata_label = QLabel("")
        self.metadata_label.setFont(QFont("Helvetica", 12))
        self.main_layout.addWidget(self.metadata_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Notes")
        self.save_btn.setFont(QFont("Helvetica", 14))
        self.save_btn.clicked.connect(self.save_notes)

        self.open_btn = QPushButton("Open Notes")
        self.open_btn.setFont(QFont("Helvetica", 14))
        self.open_btn.clicked.connect(self.open_notes)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.open_btn)
        self.main_layout.addLayout(btn_layout)

    @pyqtSlot()
    def save_notes(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Markdown Files (*.md)")
        if not file_path:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # If file exists, read metadata
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            metadata_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
            if metadata_match:
                metadata = metadata_match.group(1)
                try:
                    created_date = re.search(r'Date Created: (.*)', metadata).group(1)
                except:
                    created_date = now
                try:
                    title_match = re.search(r'Title: (.*)', metadata)
                    old_title = title_match.group(1) if title_match else "Untitled"
                except:
                    old_title = "Untitled"
                last_modified = now
            else:
                created_date = now
                old_title = self.title_edit.text().strip() or "Untitled"
                last_modified = now
        else:
            created_date = now
            last_modified = now
            old_title = self.title_edit.text().strip() or "Untitled"

        final_title = self.title_edit.text().strip() or old_title
        text_body = self.notes_text.toPlainText().strip()

        markdown_content = f"""---
Title: {final_title}
Date Created: {created_date}
Last Modified: {last_modified}
---

{text_body}
"""

        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        QMessageBox.information(self, "Success", f"Notes saved at {file_path}")

        # Attempt PDF conversion via pandoc
        pdf_path = file_path.replace(".md", ".pdf")
        try:
            subprocess.run(["pandoc", file_path, "-o", pdf_path], check=True)
            QMessageBox.information(self, "Success", f"PDF saved at {pdf_path}")
        except Exception as e:
            QMessageBox.warning(self, "Conversion Error", f"Failed to convert to PDF: {e}")

    @pyqtSlot()
    def open_notes(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
            if metadata_match:
                metadata = metadata_match.group(1)
                content_body = content[len(metadata_match.group(0)):].strip()

                # Extract data
                try:
                    title = re.search(r'Title: (.*)', metadata).group(1)
                except:
                    title = "Untitled"
                try:
                    created_date = re.search(r'Date Created: (.*)', metadata).group(1)
                except:
                    created_date = ""
                try:
                    last_modified = re.search(r'Last Modified: (.*)', metadata).group(1)
                except:
                    last_modified = ""

                self.title_edit.setText(title)
                self.metadata_label.setText(f"Created: {created_date} | Last Modified: {last_modified}")
                self.notes_text.setPlainText(content_body)
            else:
                QMessageBox.warning(self, "Error", "Invalid or missing metadata in file.")


# ----------------------------- Dialog for Text-based Calendar -----------------------------#
class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendar")
        self.resize(400, 450)

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Top controls
        control_layout = QHBoxLayout()
        self.month_combo = QComboBox()
        self.month_combo.setFont(QFont("Helvetica", 14))
        for m in list(calendar.month_name)[1:]:
            self.month_combo.addItem(m)
        self.month_combo.setCurrentText(calendar.month_name[self.current_month])
        self.month_combo.currentIndexChanged.connect(self.select_month)

        self.year_combo = QComboBox()
        self.year_combo.setFont(QFont("Helvetica", 14))
        for y in range(1900, 2101):
            self.year_combo.addItem(str(y))
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentIndexChanged.connect(self.select_year)

        control_layout.addWidget(self.month_combo)
        control_layout.addWidget(self.year_combo)
        main_layout.addLayout(control_layout)

        # Calendar label
        self.calendar_label = QLabel()
        self.calendar_label.setFont(QFont("Courier", 14))
        main_layout.addWidget(self.calendar_label)

        self.update_calendar(self.current_year, self.current_month)

    def select_month(self):
        selected_month = self.month_combo.currentText()
        self.current_month = list(calendar.month_name).index(selected_month)
        self.update_calendar(self.current_year, self.current_month)

    def select_year(self):
        self.current_year = int(self.year_combo.currentText())
        self.update_calendar(self.current_year, self.current_month)

    def update_calendar(self, year, month):
        now = datetime.now()
        today = now.day if (year == now.year and month == now.month) else None

        cal = calendar.monthcalendar(year, month)
        cal_text = f"{calendar.month_name[month]} {year}\n\n"
        cal_text += " Mo  Tu  We  Th  Fr  Sa  Su\n"

        for week in cal:
            for day in week:
                if day == 0:
                    cal_text += "    "
                else:
                    # Mark today with an asterisk
                    if day == today:
                        cal_text += f"{day:3d}*"
                    else:
                        cal_text += f"{day:3d} "
            cal_text += "\n"

        self.calendar_label.setText(cal_text)


# ----------------------------- Main Window -----------------------------#
class PlannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Planner (PyQt)")
        self.resize(900, 750)

        # For theming
        self.univ_bg_day = "#FFECD8"
        self.text_color_day = "#381d2a"
        self.schedule_color_day = "#88D5D3"
        self.button_color_day = "#E3E6B5"

        self.univ_bg_night = "#231123"
        self.text_color_night = "#da4167"
        self.schedule_color_night = "#3E0F06"
        self.button_color_night = "#3B5360"

        # State variables
        self.isNightMode = False
        self.todo_tasks = []
        self.initMenu()
        self.initUI()
        self.applyTheme()  # apply day theme by default

    def initMenu(self):
        menubar = self.menuBar()

        # Calendar menu
        calendar_menu = menubar.addMenu("Calendar")
        open_calendar_action = QAction("Open Calendar", self)
        open_calendar_action.triggered.connect(self.open_calendar)
        calendar_menu.addAction(open_calendar_action)

        # Themes menu (demonstration of multiple possible themes)
        themes_menu = menubar.addMenu("Theme")
        toggle_theme_action = QAction("Toggle Day/Night", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        themes_menu.addAction(toggle_theme_action)

    def initUI(self):
        # Main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header label with current date
        current_date = datetime.now().strftime("%B %d, %Y | %A")
        self.header_label = QLabel(current_date)
        self.header_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        main_layout.addWidget(self.header_label, alignment=Qt.AlignCenter)

        # Split the area: left (todo) and right (schedule)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, stretch=1)

        # Left side: To-Do List
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        self.todo_label = QLabel("To-Do List")
        self.todo_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        left_layout.addWidget(self.todo_label)

        # Input for new tasks
        self.todo_entry = QLineEdit()
        self.todo_entry.setFont(QFont("Helvetica", 16))
        self.todo_entry.returnPressed.connect(self.add_task)
        left_layout.addWidget(self.todo_entry)

        # Scroll area for tasks
        self.todo_scroll = QScrollArea()
        self.todo_scroll.setWidgetResizable(True)
        self.todo_container = QWidget()
        self.todo_layout = QVBoxLayout()
        self.todo_container.setLayout(self.todo_layout)
        self.todo_scroll.setWidget(self.todo_container)

        left_layout.addWidget(self.todo_scroll)

        # Right side: Schedule
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        self.schedule_label = QLabel("Schedule")
        self.schedule_label.setFont(QFont("Helvetica", 20, QFont.Bold))
        right_layout.addWidget(self.schedule_label)

        # A frame where we will place the time slots and events
        self.schedule_frame = QFrame()
        self.schedule_frame.setMinimumHeight(500)
        self.schedule_frame.setMinimumWidth(400)
        self.schedule_frame.setFrameShape(QFrame.StyledPanel)
        self.schedule_frame.setFrameShadow(QFrame.Raised)
        right_layout.addWidget(self.schedule_frame)

        # We’ll do manual painting for time slots:
        # Alternatively, you could build a layout with many rows.
        self.create_time_labels()

        # Real-time line indicator
        self.time_indicator = QFrame(self.schedule_frame)
        self.time_indicator.setStyleSheet("background-color: red;")
        self.time_indicator.setGeometry(QRect(0, 0, 400, 2))

        # Timer to update line every minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_indicator)
        self.timer.start(60_000)  # 60 seconds
        self.update_time_indicator()  # initial positioning

        # Buttons (Add Event, Open Notes, Save, Load)
        btn_layout = QHBoxLayout()
        right_layout.addLayout(btn_layout)

        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.setFont(QFont("Helvetica", 16))
        self.add_event_btn.clicked.connect(self.add_event)
        btn_layout.addWidget(self.add_event_btn)

        self.notes_btn = QPushButton("Open Notes")
        self.notes_btn.setFont(QFont("Helvetica", 16))
        self.notes_btn.clicked.connect(self.open_notes_window)
        btn_layout.addWidget(self.notes_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setFont(QFont("Helvetica", 16))
        self.save_btn.clicked.connect(self.save_data)
        btn_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("Load")
        self.load_btn.setFont(QFont("Helvetica", 16))
        self.load_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.load_btn)

    # ----------------------------- To-Do List Methods -----------------------------#
    @pyqtSlot()
    def add_task(self):
        task_text = self.todo_entry.text().strip()
        if task_text:
            # Create container widget for the task
            container = QWidget()
            container_layout = QHBoxLayout()
            container.setLayout(container_layout)

            # CheckBox
            checkbox = QCheckBox(task_text)
            checkbox.setFont(QFont("Helvetica", 16))
            checkbox.stateChanged.connect(lambda state, cb=checkbox: self.toggle_task(cb))
            container_layout.addWidget(checkbox)

            # Right-click to remove
            checkbox.setContextMenuPolicy(Qt.CustomContextMenu)
            checkbox.customContextMenuRequested.connect(lambda pos, cont=container: self.show_remove_menu(pos, cont))

            self.todo_layout.addWidget(container)
            self.todo_tasks.append(container)
            self.todo_entry.clear()

    def show_remove_menu(self, pos, container):
        menu = QMenu()
        remove_action = QAction("Remove Task", self)
        remove_action.triggered.connect(lambda: self.remove_task(container))
        menu.addAction(remove_action)
        menu.exec_(container.mapToGlobal(pos))

    def remove_task(self, container):
        index = self.todo_layout.indexOf(container)
        if index != -1:
            widget_item = self.todo_layout.takeAt(index)
            if widget_item is not None:
                widget_item.widget().deleteLater()
        if container in self.todo_tasks:
            self.todo_tasks.remove(container)

    def toggle_task(self, checkbox):
        if checkbox.isChecked():
            # Strikethrough style
            checkbox.setStyleSheet("color: lightgray; text-decoration: line-through;")
        else:
            checkbox.setStyleSheet("")

    # ----------------------------- Save/Load Data (CSV) -----------------------------#
    @pyqtSlot()
    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Completed", "Task"])
            # Go through each task container
            for container in self.todo_tasks:
                checkbox = container.findChild(QCheckBox)
                completed = "Yes" if checkbox.isChecked() else "No"
                writer.writerow([completed, checkbox.text()])

        QMessageBox.information(self, "Success", f"To-Do List saved to {file_path}")

    @pyqtSlot()
    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        # Clear existing tasks
        for container in self.todo_tasks:
            container.setParent(None)
            container.deleteLater()
        self.todo_tasks.clear()

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                completed_str, task_text = row
                completed = (completed_str.strip().lower() == "yes")

                container = QWidget()
                container_layout = QHBoxLayout()
                container.setLayout(container_layout)

                checkbox = QCheckBox(task_text)
                checkbox.setFont(QFont("Helvetica", 16))
                checkbox.setChecked(completed)
                checkbox.stateChanged.connect(lambda state, cb=checkbox: self.toggle_task(cb))
                if completed:
                    checkbox.setStyleSheet("color: lightgray; text-decoration: line-through;")

                # Right-click
                checkbox.setContextMenuPolicy(Qt.CustomContextMenu)
                checkbox.customContextMenuRequested.connect(lambda pos, cont=container: self.show_remove_menu(pos, cont))

                container_layout.addWidget(checkbox)

                self.todo_layout.addWidget(container)
                self.todo_tasks.append(container)

        QMessageBox.information(self, "Success", "To-Do List loaded successfully!")

    # ----------------------------- Schedule & Events -----------------------------#
    def create_time_labels(self):
        """
        Create the "time-slot" labels from 8AM to 8PM and place them in the schedule_frame.
        We'll do manual geometry for demonstration (similar to Tkinter's place).
        """
        start_hour = 8
        end_hour = 20
        num_hours = end_hour - start_hour
        frame_height = 500
        slot_height = frame_height / num_hours
        frame_width = self.schedule_frame.width()

        for i in range(num_hours):
            hour = start_hour + i
            label_text = ""
            if hour < 12:
                label_text = f"{hour}:00 AM"
            elif hour == 12:
                label_text = "12:00 PM"
            else:
                label_text = f"{hour - 12}:00 PM"

            lbl = QLabel(label_text, self.schedule_frame)
            lbl.setFont(QFont("Arial", 14))
            lbl.setFrameStyle(QLabel.Box | QLabel.Plain)
            # Place it
            lbl.setGeometry(0, int(i * slot_height), int(frame_width * 0.35), int(slot_height))

    def add_event(self):
        dialog = AddEventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.event_data
            self.place_event(data)

    def place_event(self, data):
        """
        Place an event label within the schedule frame based on start_idx and end_idx,
        which are fractional positions in [0..12].
        """
        start_idx = data["start_idx"]
        end_idx = data["end_idx"]
        title = data["title"]
        color = data["color"]

        # The schedule covers 8AM->8PM => 12 hours
        # schedule_frame height is ~500 by default
        total_hours = 12.0
        frame_height = self.schedule_frame.height()
        # x, width
        x = int(self.schedule_frame.width() * 0.35)
        w = int(self.schedule_frame.width() * 0.60)
        # y positions
        y_start = int((start_idx / total_hours) * frame_height)
        y_end = int((end_idx / total_hours) * frame_height)

        event_label = QLabel(title, self.schedule_frame)
        event_label.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        event_label.setFont(QFont("Helvetica", 14))
        event_label.setAlignment(Qt.AlignCenter)
        event_label.setGeometry(x, y_start, w, y_end - y_start)
        event_label.show()

    def update_time_indicator(self):
        """
        Similar to the Tkinter version, place a line to indicate the current time.
        Hide it if outside 8AM -> 8PM.
        """
        now = datetime.now()
        hour = now.hour
        minute = now.minute

        if 8 <= hour < 20:
            # total = 12 hours from 8 -> 20
            total_hours = 12
            frame_height = self.schedule_frame.height()
            # fraction of day so far
            offset = (hour - 8) + minute/60
            rel_pos = offset / total_hours  # 0..1
            y = int(rel_pos * frame_height)
            self.time_indicator.setGeometry(0, y, self.schedule_frame.width(), 2)
            self.time_indicator.show()
        else:
            self.time_indicator.hide()

    # ----------------------------- Notes -----------------------------#
    def open_notes_window(self):
        dialog = NotesDialog(self)
        dialog.exec_()

    # ----------------------------- Calendar -----------------------------#
    def open_calendar(self):
        dialog = CalendarDialog(self)
        dialog.exec_()

    # ----------------------------- Toggle Theme -----------------------------#
    def toggle_theme(self):
        self.isNightMode = not self.isNightMode
        self.applyTheme()

    def applyTheme(self):
        if self.isNightMode:
            univ_bg = self.univ_bg_night
            text_color = self.text_color_night
            schedule_color = self.schedule_color_night
            button_color = self.button_color_night
        else:
            univ_bg = self.univ_bg_day
            text_color = self.text_color_day
            schedule_color = self.schedule_color_day
            button_color = self.button_color_day

        # Build a style sheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {univ_bg};
            }}
            QWidget {{
                background-color: {univ_bg};
                color: {text_color};
            }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                background-color: white;
                color: black;
            }}
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
            }}
            QCheckBox {{
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
        """)

        # For the schedule slots, we could do something more targeted:
        # Find all children in schedule_frame that are "hour labels"
        for child in self.schedule_frame.children():
            if isinstance(child, QLabel):
                child.setStyleSheet(f"background-color: {schedule_color}; color: {text_color};")


# ----------------------------- Run Application -----------------------------#
def main():
    app = QApplication(sys.argv)
    window = PlannerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
