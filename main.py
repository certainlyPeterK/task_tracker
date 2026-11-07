#Импорт модулей
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

#Инициализация приложения и БД
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#Модель базы данных для задачи
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.id

#Главная страница

#Добавление и показывание задачи
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Task(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Ошибка при добавлении: {e}"
    else:
        filter_type = request.args.get('filter', 'all')
        
        if filter_type == 'active':
            tasks = Task.query.filter_by(done=False).order_by(Task.id.desc()).all()
        elif filter_type == 'done':
            tasks = Task.query.filter_by(done=True).order_by(Task.id.desc()).all()
        else:
            tasks = Task.query.order_by(Task.id.desc()).all()
            
        return render_template('index.html', tasks=tasks, current_filter=filter_type)

#Изменение статуса
@app.route('/task/toggle/<int:id>', methods=['POST'])
def toggle(id):
    task = Task.query.get_or_404(id)
    task.done = not task.done
    try:
        db.session.commit()
        filter_type = request.args.get('filter', 'all')
        if filter_type == 'all':
            return redirect(url_for('index'))
        return redirect(url_for('index', filter=filter_type))
    except Exception as e:
        return f"Ошибка при обновлении: {e}"

#Удаление
@app.route('/task/delete/<int:id>', methods=['POST'])
def delete(id):
    task = Task.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        filter_type = request.args.get('filter', 'all')
        if filter_type == 'all':
            return redirect(url_for('index'))
        return redirect(url_for('index', filter=filter_type))
    except Exception as e:
        return f"Ошибка при удалении: {e}"

#Редактирование
@app.route('/task/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    filter_type = request.args.get('filter', 'all')
    
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            if filter_type == 'all':
                return redirect(url_for('index'))
            return redirect(url_for('index', filter=filter_type))
        except Exception as e:
            return f"Ошибка при редактировании: {e}"
    else:
        return render_template('edit.html', task=task, current_filter=filter_type)

#Запуск
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
