from flask import Flask, render_template, request, redirect
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask import flash, redirect,url_for
from filters import format_currency, format_date
import os

app= Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_please _change")

basedir =os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initialize SQLAlchemy database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register custom Jinja filters
app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['date'] = format_date


class Expense(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     amount = db.Column(db.Float, nullable=False)
     category = db.Column(db.String(100), nullable =False)
     date = db.Column(db.Date, nullable=False)#new fiels


class Income(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     amount = db.Column(db.Float, nullable=False)
     date = db.Column(db.Date, nullable=False)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B %Y'):
     date_obj = datetime.strptime(value, '%Y-%m')
     return date_obj.strftime(format)

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
         flash("Expense added ✅","success")
         return redirect(url_for('add_expense'))
          
             
    return render_template('add_expense.html')

@app.route('/add-income', methods=['GET', 'POST'])
def add_income():
     if request.method == 'POST':
          amount = float(request.form.get('amount'))
          date_str = request.form.get('date', '').strip()
          if not date_str:
             flash("Date is required!", "error")
             return redirect(url_for('add_expense'))
          date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

          new_income = Income(amount=amount, date=date_obj)
          db.session.add(new_income)
          db.session.commit()
          flash("Income saved✅", "success")
          return redirect(url_for('add_income'))
     
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
   
    

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
     expense = Expense.query.get_or_404(id)
     db.session.delete(expense)
     db.session.commit()
     return redirect('/expenses')

@app.route('/summary')
def summary():
     total_expense = db.session.query(func.sum(Expense.amount)).scalar() or 0
     total_income = db.session.query(func.sum(Income.amount)).scalar() or 0
     savings = total_income - total_expense

     raw_summary = db.session.query(
          Expense.category,
          func.sum(Expense.amount)
     ).group_by(Expense.category).all()

     category_summary = [(row[0], float(row[1])) for row in raw_summary]

     # Month-wise summary
     month_summary = db.session.query(
          func.strftime('%Y-%m', Expense.date),
          func.sum(Expense.amount)
     ).group_by(func.strftime('%Y-%m', Expense.date)).all()

     income_by_month = dict(
          db.session.query(
               func.strftime('%Y-%m', Income.date),
               func.sum(Income.amount)
          ).group_by(func.strftime('%Y-%m', Income.date)).all()
     )

     expense_by_month = dict(
          db.session.query(
               func.strftime('%Y-%m', Expense.date),
               func.sum(Expense.amount)
          ).group_by(func.strftime('%Y-%m', Expense.date)).all()
     )

     all_months = sorted(set(income_by_month.keys()) | set(expense_by_month.keys()))

     income_vs_expense = [
          {
               'month': m,
               'income': round(income_by_month.get(m, 0), 2),
               'expense': round(expense_by_month.get(m, 0), 2)
          }
          for m in all_months
     ]

     return render_template(
          'summary.html',
          total_expense=total_expense,
          total_income=total_income,
          savings=savings,
          category_summary=category_summary,
          month_summary=month_summary,
          income_vs_expense=income_vs_expense
     )



if __name__=='__main__':
     with app.app_context():
          db.create_all()
     print("Flask is starting...")
     app.run(debug=True)
     


        