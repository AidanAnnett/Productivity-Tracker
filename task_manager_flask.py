from flask import Flask, request, render_template, redirect, url_for

from task_manager import TaskManager, Task

app = Flask(__name__)

task_manager = TaskManager()


@app.route('/')
def index():
    return render_template('index.html', tasks=task_manager.tasks)


@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form['name']
    duration = int(request.form['duration'])
    category = request.form['category']

    new_task = Task(name, duration, category)
    task_manager.add_task(new_task)

    return redirect(url_for('index'))


@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = task_manager.tasks[task_id]
    task.toggle_status()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
