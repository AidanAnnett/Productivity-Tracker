import tkinter as tk
import time
from tkinter import ttk
from datetime import datetime
import sqlite3

class Task:
    """
    A class representing a task with a name, duration, and category.

    Variables:
    - name : The name of the task.
    - duration : The duration of the task in minutes.
    - category : The category of the task (e.g., "Daily", "Weekly", "Monthly").
    - elapsed_time : The time that has elapsed since the task started.
    - start_time : The timestamp when the task was started.
    - running : A flag indicating whether the task is currently running.

    Methods:
    - __init__(self, name, duration, category): Initializes a new task.
    - start(): Starts the task timer.
    - pause(): Pauses the task timer.
    - toggle_status(): Toggles the status between running and paused.
    - remaining_time() -> str: Returns the remaining time for the task in "HH:MM:SS" format.
    - progress_percentage() -> float: Returns the progress percentage of the task.
    """
    def __init__(self, name, duration, category):
        self.name = name
        self.duration = duration
        self.category = category
        self.elapsed_time = 0
        self.start_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def pause(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False

    def toggle_status(self):
        if self.running:
            self.pause()
        else:
            self.start()

    def remaining_time(self):
        if self.running:
            remaining_seconds = max(0, self.duration * 60 - self.elapsed_time - (time.time() - self.start_time))
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
        else:
            remaining_seconds = max(0, self.duration * 60 - self.elapsed_time)
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def progress_percentage(self):
        if self.running:
            remaining_seconds = max(0, self.duration * 60 - self.elapsed_time - (time.time() - self.start_time))
        else:
            remaining_seconds = max(0, self.duration * 60 - self.elapsed_time)

        return 100 * remaining_seconds / (self.duration * 60)


class TaskManager:
    """
    A class to manage tasks and handle database interactions.

    Variables:
    - db_file: The path to the SQLite database file.
    - conn: The SQLite connection object.
    - cursor: The SQLite cursor object.
    - tasks: A list of Task objects managed by the TaskManager.

    Methods:
    - __init__(self, db_file): Initializes the TaskManager with the database file path.
    - create_table(self): Creates the tasks table in the SQLite database if it does not exist.
    - load_tasks_from_db(self): Loads tasks from the SQLite database into the tasks list.
    - add_task(self, task): Adds a new task to the database and tasks list.
    - remove_task(self, task_name): Removes a task from the database and tasks list.
    - reset_daily_tasks(self): Resets elapsed time for daily tasks.
    - reset_weekly_tasks(self): Resets elapsed time for weekly tasks.
    - reset_monthly_tasks(self): Resets elapsed time for monthly tasks.
    """
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.tasks = []

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                                name TEXT,
                                duration INTEGER,
                                category TEXT,
                                elapsed_time REAL,
                                start_time REAL,
                                running INTEGER
                                )''')
        self.conn.commit()

    def load_tasks_from_db(self):
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        for row in rows:
            name, duration, category, elapsed_time, start_time, running = row
            task = Task(name, duration, category)
            task.elapsed_time = elapsed_time
            task.start_time = start_time
            task.running = bool(running)
            self.tasks.append(task)

    def add_task(self, task):
        self.cursor.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)",
                            (task.name, task.duration, task.category, task.elapsed_time, task.start_time, int(task.running)))
        self.conn.commit()
        self.tasks.append(task)  # Update the tasks list

    def remove_task(self, task_name):
        self.cursor.execute("DELETE FROM tasks WHERE name=?", (task_name,))
        self.conn.commit()
        self.tasks = [task for task in self.tasks if task.name != task_name]  # Update the tasks list

    def reset_daily_tasks(self):
        for task in self.tasks:
            if task.category == "Daily":
                task.elapsed_time = 0
                task.start_time = 0

    def reset_weekly_tasks(self):
        for task in self.tasks:
            if task.category == "Weekly":
                task.elapsed_time = 0
                task.start_time = 0

    def reset_monthly_tasks(self):
        for task in self.tasks:
            if task.category == "Monthly":
                task.elapsed_time = 0
                task.start_time = 0


class AddTaskWindow:
    """
    A class to create a new window for adding tasks.

    Variables:
    - master: The master Tkinter window.
    - task_manager: The TaskManager instance.
    - update_callback: The callback function to update the task list.
    - window: The top-level window for adding tasks.
    - task_name_label: Label for task name entry.
    - task_name_entry: Entry widget for task name.
    - hours_label: Label for hours spinbox.
    - hours_var: StringVar for hours spinbox value.
    - hours_spinbox: Spinbox for hours.
    - minutes_label: Label for minutes spinbox.
    - minutes_var: StringVar for minutes spinbox value.
    - minutes_spinbox: Spinbox for minutes.
    - category_label: Label for category radio buttons.
    - category_var: StringVar for selected category.
    - daily_radio: Radio button for daily category.
    - weekly_radio: Radio button for weekly category.
    - monthly_radio: Radio button for monthly category.
    - error_label: Label for displaying error messages.
    - add_button: Button to add the task.

    Methods:
    - __init__(self, master, task_manager, update_callback): Initializes the AddTaskWindow.
    - add_task(self): Adds the task to the task manager and updates the task list.
    """
    def __init__(self, master, task_manager, update_callback):
        self.master = master
        self.task_manager = task_manager
        self.update_callback = update_callback

        self.window = tk.Toplevel(master)
        self.window.title("Add Task")
        self.window.geometry("350x150")
        self.window.resizable(False, False)  # Prevent resizing

        self.task_name_label = tk.Label(self.window, text="Task Name:")
        self.task_name_label.grid(row=0, column=0)

        self.task_name_entry = tk.Entry(self.window)
        self.task_name_entry.grid(row=0, column=1)

        self.hours_label = tk.Label(self.window, text="Hours:")
        self.hours_label.grid(row=1, column=0)

        self.hours_var = tk.StringVar(self.window)
        self.hours_var.set("0")
        self.hours_spinbox = tk.Spinbox(self.window, from_=0, to=24, textvariable=self.hours_var)
        self.hours_spinbox.grid(row=1, column=1)

        self.minutes_label = tk.Label(self.window, text="Minutes:")
        self.minutes_label.grid(row=2, column=0)

        self.minutes_var = tk.StringVar(self.window)
        self.minutes_var.set("0")
        self.minutes_spinbox = tk.Spinbox(self.window, from_=0, to=59, textvariable=self.minutes_var)
        self.minutes_spinbox.grid(row=2, column=1)

        self.category_label = tk.Label(self.window, text="Category:")
        self.category_label.grid(row=3, column=0)

        self.category_var = tk.StringVar()
        self.category_var.set("Daily")

        self.daily_radio = tk.Radiobutton(self.window, text="Daily", variable=self.category_var, value="Daily")
        self.daily_radio.grid(row=3, column=1)

        self.weekly_radio = tk.Radiobutton(self.window, text="Weekly", variable=self.category_var, value="Weekly")
        self.weekly_radio.grid(row=3, column=2)

        self.monthly_radio = tk.Radiobutton(self.window, text="Monthly", variable=self.category_var, value="Monthly")
        self.monthly_radio.grid(row=3, column=3)

        self.error_label = tk.Label(self.window, text="", fg="red")
        self.error_label.grid(row=4, column=0, columnspan=4)

        self.add_button = tk.Button(self.window, text="Add Task", command=self.add_task)
        self.add_button.grid(row=5, column=0, columnspan=4)

    def add_task(self):
        name = self.task_name_entry.get()
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()

        if not name:
            self.error_label.config(text="Please give the task a name.")
            return

        if not (hours.isdigit() and minutes.isdigit()):
            self.error_label.config(text="Please enter only digits for hours and minutes.")
            return

        hours = int(hours)
        minutes = int(minutes)

        category = self.category_var.get()

        if hours == 0 and minutes == 0:
            self.error_label.config(text="Please add time to the task, it cannot be 0.")
            return

        # Check if task name already exists
        if any(task.name == name for task in self.task_manager.tasks):
            self.error_label.config(text="Task with this name already exists.")
            return

        duration = hours * 60 + minutes

        new_task = Task(name, duration, category)
        self.task_manager.add_task(new_task)
        self.update_callback()  # Update the GUI after adding the task
        self.window.destroy()


class App:
    """
    The main application class for managing tasks.

    Variables:
    - master: The main Tkinter window.
    - task_manager: The TaskManager instance.
    - task_buttons: A dictionary mapping task names to their action buttons.
    - task_timers: A dictionary mapping task names to their timer labels.
    - task_progress_bars: A dictionary mapping task names to their progress bars.
    - tasks_frame: The frame containing the task widgets.
    - add_button: The button to open the AddTaskWindow.

    Methods:
    - __init__(self, master, db_file): Initializes the application.
    - open_add_task_window(self): Opens the AddTaskWindow.
    - toggle_task_status(self, task_name): Toggles the status of the specified task.
    - remove_task(self, task_name): Removes the specified task.
    - update_tasks(self): Updates the task list in the GUI.
    - update_timer(self, task_name): Updates the timer and progress bar for the specified task.
    - schedule_resets(self): Schedules the daily, weekly, and monthly resets.
    """
    def __init__(self, master, db_file):
        self.master = master
        self.task_manager = TaskManager(db_file)
        self.task_buttons = {}
        self.task_timers = {}
        self.task_progress_bars = {}

        self.tasks_frame = tk.Frame(master)
        self.tasks_frame.grid(row=0, column=0, columnspan=3)

        self.add_button = tk.Button(master, text="Add Task", command=self.open_add_task_window)
        self.add_button.grid(row=1, column=0, columnspan=3)

        self.update_tasks()
        self.schedule_resets()

    def open_add_task_window(self):
        add_task_window = AddTaskWindow(self.master, self.task_manager, self.update_tasks)

    def toggle_task_status(self, task_name):
        for task in self.task_manager.tasks:
            if task.name == task_name:
                task.toggle_status()
                if not task.running:
                    self.task_buttons[task.name].config(text="Completed", state=tk.DISABLED)
                self.update_tasks()
                return

    def remove_task(self, task_name):
        self.task_manager.remove_task(task_name)
        self.update_tasks()

    def update_tasks(self):
        # Clear all previous task widgets
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        # Create widgets for each task
        for i, task in enumerate(self.task_manager.tasks):
            task_frame = tk.Frame(self.tasks_frame)
            task_frame.grid(row=i, column=0, pady=5)

            tk.Label(task_frame, text=f"{task.name} - {task.category}", padx=5).grid(row=0, column=0)

            progress_bar = ttk.Progressbar(task_frame, orient="horizontal", length=100, mode="determinate")
            progress_bar.grid(row=0, column=1, pady=5)

            action_button_text = "Start" if not task.running else "Pause"
            action_button = tk.Button(task_frame, text=action_button_text,
                                      command=lambda t=task.name: self.toggle_task_status(t))
            action_button.grid(row=0, column=2, padx=5)
            self.task_buttons[task.name] = action_button

            timer_label = tk.Label(task_frame)
            timer_label.grid(row=0, column=3)
            self.task_timers[task.name] = timer_label

            self.task_progress_bars[task.name] = progress_bar
            # Remove button for each task
            remove_button = tk.Button(task_frame, text="Remove", command=lambda t=task.name: self.remove_task(t))
            remove_button.grid(row=0, column=4)

            # Update timer initially
            self.update_timer(task.name)

    def update_timer(self, task_name):
        task = next((t for t in self.task_manager.tasks if t.name == task_name), None)
        if task:
            timer_label = self.task_timers[task_name]
            timer_label.config(text=task.remaining_time())

            progress_bar = self.task_progress_bars[task_name]
            progress_bar["value"] = task.progress_percentage()

            if task.running:
                self.master.after(1000, lambda: self.update_timer(task_name))

    def schedule_resets(self):
        # Schedule daily, weekly, and monthly resets
        self.master.after(60000, self.schedule_resets)  # Reschedule in 1 minute
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:  # Daily reset at midnight
            self.task_manager.reset_daily_tasks()
        if now.weekday() == 0 and now.hour == 0 and now.minute == 0:  # Weekly reset on Monday at midnight
            self.task_manager.reset_weekly_tasks()
        if now.day == 1 and now.hour == 0 and now.minute == 0:  # Monthly reset on the 1st day of the month at midnight
            self.task_manager.reset_monthly_tasks()


def main():
    root = tk.Tk()
    root.title("Task Manager")
    root.geometry("400x300")
    root.resizable(False, False)  # Prevent resizing
    db_file = "tasks.db"
    app = App(root, db_file)
    app.task_manager.load_tasks_from_db()  # Load tasks from the database when the application starts
    root.mainloop()


if __name__ == "__main__":
    main()
