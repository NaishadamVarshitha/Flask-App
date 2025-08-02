from flask import Flask, render_template, request, redirect
from datetime import datetime
from datetime import date
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
     date = db.Column(db.Date, nullable=False)#new fiels
expenses=[]

@app.route('/')
def index():
     return redirect('/add-expense')

@app.route('/add-expense', methods=['GET','POST'])
def add_expense():
    if request.method =='POST':
         amount = float(request.form.get('amount'))
         category = request.form.get('category')
         date_str = request.form.get('date')
         date_obj= datetime.strptime(date_str, '%Y-%m-%d').date()
         
         new_expense = Expense(amount=amount, category=category, date=date_obj)
         db.session.add(new_expense)
         db.session.commit()
         return "Expense added ✅"
    return render_template('add_expense.html')

@app.route('/edit-expense/<int:id>' , methods=['GET', 'POST'])
def edit_expense(id):
     expense = Expense.query.get_or_404(id)
     if request.method == 'POST':
          expense.amount = float(request.form.get('amount'))
          expense.category = request.form.get('category')
          db.session.commit()
          return redirect('/expenses')
     return render_template('edit_expense.html' , expense=expense)

@app.route('/expenses', methods=['GET'])
def show_expenses():
     category = request.args.get('category', '')
     start_date = request.args.get('start_date')
     end_date = request.args.get('end_date')

     query=Expense.query

     if category:
          query = query.filter(Expense.category.ilike(f'%{category}%'))

     if start_date:
          try:
               start =datetime.strptime(start_date, '%Y-%m-%d').date()
               query =query.filter(Expense.date >=start)
          except ValueError:
               pass
     if end_date:
          try:
               end = datetime.strptime(end_date, '%Y-%m-%d').date()
               query = query.filter(Expense.date <=end)
          except ValueError:
               pass

     expenses = query.all()
     total_amount = sum(exp.amount for exp in expenses)

     return render_template('expenses.html', expenses=expenses, category=category, start_date=start_date, end_date=end_date, total_amount=total_amount)
   
    

@app.route('/delete-expense/<int:id>', methods=['POST'])
def delete_expense(id):
     expense = Expense.query.get_or_404(id)
     db.session.delete(expense)
     db.session.commit()
     return redirect('/expenses')

if __name__=='__main__':
     with app.app_context():
          db.create_all()
     app.run(debug=True)


        