from flask import Flask, render_template, request, redirect
app= Flask(__name__)
expenses=[]

@app.route('/')
def index():
     return redirect('/add-expense')

@app.route('/add-expense', methods=['GET','POST'])
def add_expense():
    if request.method =='POST':
         amount =request.form.get('amount')
         category=request.form.get('category')
         expenses.append({'Amount':amount,'Category':category})
         return "Expense added ✅"
    return render_template('add_expense.html')

@app.route('/expenses')
def show_expenses():
     return {'expenses':expenses}

if __name__=='__main__':
     app.run(debug=True)


        