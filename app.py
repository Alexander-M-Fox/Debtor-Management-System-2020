from flask import *
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydata.db'
db = SQLAlchemy(app)


def initialize_db(app):
    app.app_context().push()
    db.init_app(app)
    db.create_all()


class Debtor(db.Model):
    debtorID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    contactNo = db.Column(db.Integer, nullable=True)
    loans = db.relationship('Loan', backref='debtorInfo', lazy=True)

    def __repr__(self):
        # what to return when a new element is created.
        return f"Debtor : {self.firstName} {self.lastName}"


class Loan(db.Model):
    loanID = db.Column(db.Integer, primary_key=True)
    debtorID = db.Column(db.Integer, db.ForeignKey(
        'debtor.debtorID'), nullable=False)
    amountCredited = db.Column(db.Float, nullable=False)
    dateCredited = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    currentAmountPaid = db.Column(db.Float, nullable=False, default=00.00)
    proposedPaymentDate = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    payments = db.relationship('Payment', backref='loanInfo', lazy=True)

    def __repr__(self):
        return f"Loan : {self.loanID}, Amount - {self.amountCredited}, Already Paid - {self.currentAmountPaid}"


class Payment(db.Model):
    paymentID = db.Column(db.Integer, primary_key=True)
    loanID = db.Column(db.Integer, db.ForeignKey(
        'loan.loanID'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Payment : ID - {self.paymentID}, Loan - {self.loanID}, Amount -  {self.amount}"


initialize_db(app)


@app.route('/overview')
def overview():
    currLoans = Loan.query.all()
    currDebtors = Debtor.query.all()
    return render_template('overview.html', currLoans=currLoans, currDebtors=currDebtors)


@app.route('/newLoan', methods=['GET', 'POST'])
def newLoan():
    if request.method == 'POST':
        # TODO: input validation
        # TODO: Try catch blocks
        debtorID = request.form['debtorID']
        amountCredited = request.form['amountCredited']
        dateCredited = datetime.strptime(
            request.form['dateCredited'], '%Y-%m-%d')
        proposedPaymentDate = datetime.strptime(
            request.form['proposedPaymentDate'], '%Y-%m-%d')
        notes = request.form['notes']

        new_loan = Loan(debtorID=debtorID, amountCredited=amountCredited,
                        dateCredited=dateCredited, proposedPaymentDate=proposedPaymentDate, notes=notes)

        print(type(dateCredited))
        print(dateCredited)
        db.session.add(new_loan)
        db.session.commit()
        return redirect('/')

    else:
        debtors = Debtor.query.all()
        return render_template('newLoan.html', debtors=debtors)


@app.route('/')
def actions():
    return render_template('actions.html')


@app.route('/newDebtor', methods=['GET', 'POST'])
def newDebtor():
    if request.method == 'GET':
        return render_template('newDebtor.html')
    else:
        # TODO: input validation
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        contactNo = request.form['contact']

        new_debtor = Debtor(firstName=firstName,
                            lastName=lastName, contactNo=contactNo)

        try:
            db.session.add(new_debtor)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error adding debtor'


@app.route('/deleteDebtor', methods=['GET', 'POST'])
def deleteDebtor():
    if request.method == 'GET':
        debtors = Debtor.query.all()
        return render_template('deleteDebtor.html', debtors=debtors)
    else:
        if request.form['debtorID']:
            debtorID = request.form['debtorID']
            debtorToDelete = Debtor.query.filter_by(debtorID = debtorID).first()
        else:
            return "Error, no debtorID passed in request"

        try:
            db.session.delete(debtorToDelete)
            db.session.commit()
            return redirect('/')
        except:
            return redirect('/error/deleteDebtor')


@app.route('/error/<string:errorType>')
def error(errorType):
    return render_template('error.html', error = errorType)


@app.route('/newPayment', methods = ['GET', 'POST'])
def newPayment():
    if request.method == 'GET':
        loans = Loan.query.all()
        return render_template('newPayment.html', loans=loans)
    else:
        loanID = request.form['loanID']
        loanToUpdate = Loan.query.filter_by(loanID = loanID).first()
        currToPay = loanToUpdate.amountCredited - loanToUpdate.currentAmountPaid
        if int(request.form['amountPaid']) > currToPay:
            return redirect('/error/overpay')
        else:
            try:
                loanToUpdate.currentAmountPaid += int(request.form['amountPaid'])
                db.session.commit()
                return redirect('/')
            except:
                return redirect('/error/makePayment')


@app.route('/viewDebtors')
def viewDebtors():
    debtors = Debtor.query.all()
    loans = Loan.query.all()
    return render_template('viewDebtors.html', debtors=debtors, loans=loans)


@app.route('/api/currTotalOwed/<int:debtorID>')
def currTotalOwed(debtorID):
    IDloans = Loan.query.filter_by(debtorID = debtorID).all()
    currTotalOwed = 0
    for loan in IDloans:
        currTotalOwed += (loan.amountCredited - loan.currentAmountPaid)
    return str(currTotalOwed)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
