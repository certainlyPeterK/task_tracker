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

#Добавление задачи
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
        tasks = Task.query.order_by(Task.id.desc()).all()
        return render_template('index.html', tasks=tasks)

#Изменение статуса
@app.route('/toggle/<int:id>', methods=['POST'])
def toggle(id):
    task = Task.query.get_or_404(id)
    task.done = not task.done
    try:
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"Ошибка при обновлении: {e}"
    
#Запуск
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)