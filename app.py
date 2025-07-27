from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
app= Flask(__name__)
basedir =os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initialize SQLAlchemy database
db = SQLAlchemy(app)

class Expense(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     amount = db.Column(db.Float, nullable=False)
     category = db.Column(db.String(100), nullable =False)
expenses=[]

@app.route('/')
def index():
     return redirect('/add-expense')

@app.route('/add-expense', methods=['GET','POST'])
def add_expense():
    if request.method =='POST':
         amount = float(request.form.get('amount'))
         category = request.form.get('category')
         new_expense = Expense(amount=amount, category=category)
         db.session.add(new_expense)
         db.session.commit()
         return "Expense added ✅"
    return render_template('add_expense.html')

@app.route('/expenses')
def show_expenses():
     expenses = Expense.query.all()
     result = [
          {'Amount': e.amount, 'Category': e.category}
          for e in expenses
     ]
     return {'expenses': result}

if __name__=='__main__':
     with app.app_context():
          db.create_all()
     app.run(debug=True)


        