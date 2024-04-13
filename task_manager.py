import tkinter as tk
import time
from tkinter import ttk
from datetime import datetime

'''
Task Class:
Represents a task with a name, duration, category, elapsed time, start time, and running state.

Variables:
- name: Name of the task
- duration: Duration of the task in minutes
- category: Category of the task (daily, weekly, monthly)
- elapsed_time: Total time elapsed for the task
- start_time: Time when the task's timer was started
- running: State of the task timer (True if running, False otherwise)

Functions:
- start(): Start the task timer
- pause(): Pause the task timer
- toggle_status(): Toggle the task timer's status (start/pause)
- remaining_time(): Calculate and return the time left for the task
- percentage_left(): Calculate and return the progress of the task as a percentage
'''


class Task:
    def __init__(self, name, duration, category):
        self.name = name
        self.duration = duration
        self.category = category
        self.time_progress = 0
        self.start_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def pause(self):
        if self.running:
            self.time_progress += time.time() - self.start_time
            self.running = False

    def toggle_status(self):
        if self.running:
            self.pause()
        else:
            self.start()

    def remaining_time(self):
        if self.running:
            seconds_left = max(0, (self.duration * 60 - self.time_progress - (time.time() - self.start_time)))
            hours, mins_left = divmod(seconds_left, 3600)
            minutes, seconds = divmod(mins_left, 60)
            return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
        else:
            seconds_left = max(0, (self.duration * 60) - (self.time_progress))
            hours, mins_left = divmod(seconds_left, 3600)
            minutes, seconds = divmod(mins_left, 60)
            return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def percentage_left(self):
        if self.running:
            seconds_left = max(0, self.duration * 60 - self.time_progress - (time.time() - self.start_time))
        else:
            seconds_left = max(0, self.duration * 60 - self.time_progress)

        return (seconds_left / (self.duration * 60)) * 100


'''
TaskManager Class:
Manages a list of tasks and provides methods to add, remove, and reset tasks based on their category.

Variables:
- tasks: List of current tasks

Functions:
- add_task(task): Add a task to the list of current tasks
- remove_task(task): Remove a task from the list of current tasks
- reset_daily_tasks(): Reset daily tasks by resetting their elapsed time and start time
- reset_weekly_tasks(): Reset weekly tasks by resetting their elapsed time and start time
- reset_monthly_tasks(): Reset monthly tasks by resetting their elapsed time and start time
'''


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

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


'''
AddTaskWindow Class:
Provides a window for adding new tasks with a name, duration, and category.

Variables:
- window: Popup window for adding tasks
- task_name_box: Entry widget for entering the task name
- hours_spinbox, minutes_spinbox: Spinbox widgets for selecting task duration
- category_var: StringVar for storing the selected category
- error_text: Label widget for displaying error messages

Functions:
- add_task(): Retrieve task details, validate inputs, and add the task to the task manager
'''


class AddTaskWindow:
    def __init__(self, master, task_manager, update_callback):
        self.master = master
        self.task_manager = task_manager
        self.update_callback = update_callback

        self.window = tk.Toplevel(master)
        self.window.title("Add Task")
        self.window.geometry("350x150")
        self.window.resizable(False, False)

        self.task_name_text = tk.Label(self.window, text="Task Name:")
        self.task_name_text.grid(row=0, column=0)

        self.task_name_box = tk.Entry(self.window)
        self.task_name_box.grid(row=0, column=1)

        self.hours_text = tk.Label(self.window, text="Hours:")
        self.hours_text.grid(row=1, column=0)

        self.hours_var = tk.StringVar(self.window)
        self.hours_var.set("0")
        self.hours_spinbox = tk.Spinbox(self.window, from_=0, to=24, textvariable=self.hours_var)
        self.hours_spinbox.grid(row=1, column=1)

        self.minutes_text = tk.Label(self.window, text="Minutes:")
        self.minutes_text.grid(row=2, column=0)

        self.minutes_var = tk.StringVar(self.window)
        self.minutes_var.set("0")
        self.minutes_spinbox = tk.Spinbox(self.window, from_=0, to=59, textvariable=self.minutes_var)
        self.minutes_spinbox.grid(row=2, column=1)

        self.category_text = tk.Label(self.window, text="Category:")
        self.category_text.grid(row=3, column=0)

        self.category_var = tk.StringVar()
        self.category_var.set("Daily")

        self.daily_button = tk.Radiobutton(self.window, text="Daily", variable=self.category_var, value="Daily")
        self.daily_button.grid(row=3, column=1)

        self.weekly_button = tk.Radiobutton(self.window, text="Weekly", variable=self.category_var, value="Weekly")
        self.weekly_button.grid(row=3, column=2)

        self.monthly_button = tk.Radiobutton(self.window, text="Monthly", variable=self.category_var, value="Monthly")
        self.monthly_button.grid(row=3, column=3)

        self.error_text = tk.Label(self.window, text="", fg="red")
        self.error_text.grid(row=4, column=0, columnspan=4)

        self.add_task_button = tk.Button(self.window, text="Add Task", command=self.add_task)
        self.add_task_button.grid(row=5, column=0, columnspan=4)

    def add_task(self):
        name = self.task_name_box.get()
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()

        if not name:
            self.error_text.config(text="Please give the task a name.")
            return

        if not (minutes.isdigit() and hours.isdigit()):
            self.error_text.config(text="Please enter only digits for hours and minutes.")
            return

        hours = int(hours)
        minutes = int(minutes)
        category = self.category_var.get()

        if hours == 0 and minutes == 0:
            self.error_text.config(text="Please add time to the task, it cannot be 0.")
            return

        if any(task.name == name for task in self.task_manager.tasks):
            self.error_text.config(text="Task with this name already exists.")
            return

        duration = hours * 60 + minutes
        new_task = Task(name, duration, category)
        self.task_manager.add_task(new_task)
        self.update_callback()
        self.window.destroy()


'''
App Class:
Manages the main application window and task-related functionality.

Variables:
- task_manager: Instance of TaskManager to manage tasks
- task_buttons: Dictionary to store task buttons
- task_timers: Dictionary to store task timers
- task_progress_bars: Dictionary to store task progress bars

Functions:
- open_add_task_window(): Opens the Add Task window
- toggle_task_status(task_name): Toggles the status (start/pause) of a task
- update_tasks(): Updates the task display
- update_timer(task_name): Updates the timer for a specific task
- schedule_resets(): Schedules daily, weekly, and monthly task resets
'''


class App:
    def __init__(self, master):
        self.master = master
        self.task_manager = TaskManager()
        self.task_buttons = {}
        self.task_timers = {}
        self.task_progress_bars = {}

        self.tasks_frame = tk.Frame(master)
        self.tasks_frame.grid(row=0, column=0, columnspan=3)

        self.add_task_button = tk.Button(master, text="Add Task", command=self.open_add_task_window)
        self.add_task_button.grid(row=1, column=0, columnspan=3)

        self.update_tasks()
        self.schedule_resets()

    def open_add_task_window(self):
        AddTaskWindow(self.master, self.task_manager, self.update_tasks)

    def toggle_task_status(self, task_name):
        for task in self.task_manager.tasks:
            if task.name == task_name:
                task.toggle_status()
                if not task.running:
                    self.task_buttons[task.name].config(text="Completed", state=tk.DISABLED)
                self.update_tasks()
                return

    def update_tasks(self):
        # Remove tasks so we can update them
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        # Update widgets after clearing
        for i, task in enumerate(self.task_manager.tasks):
            task_frame = tk.Frame(self.tasks_frame)
            task_frame.grid(row=i, column=0, pady=5)

            tk.Label(task_frame, text=f"{task.name} - {task.category}", padx=5).grid(row=0, column=0)

            progress_bar = ttk.Progressbar(task_frame, orient="horizontal", length=100, mode="determinate")
            progress_bar.grid(row=0, column=1, pady=5)
            if not task.running:
                action_button_text = "Start"
            else:
                action_button_text = "Pause"

            action_button = tk.Button(task_frame, text=action_button_text, command=lambda: self.toggle_task_status(task.name))
            action_button.grid(row=0, column=2, padx=5)
            self.task_buttons[task.name] = action_button

            timer_text = tk.Label(task_frame)
            timer_text.grid(row=0, column=3)
            self.task_timers[task.name] = timer_text

            self.task_progress_bars[task.name] = progress_bar

            # Update timer initially
            self.update_timer(task.name)

    def update_timer(self, task_name):
        task = None
        for t in self.task_manager.tasks:
            if t.name == task_name:
                task = t
                break
        if task:
            timer_text = self.task_timers[task_name]
            timer_text.config(text=task.remaining_time())

            progress_bar = self.task_progress_bars[task_name]
            progress_bar["value"] = task.percentage_left()

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
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
