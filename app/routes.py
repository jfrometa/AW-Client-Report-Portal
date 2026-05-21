from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from . import db
from .models import Client, Account, Report, Balance
from .utils import generate_pdf
from datetime import datetime
import traceback

main_bp = Blueprint('main', __name__)

def get_private_reserve_target(client):
    if client.private_reserve_target_override is not None and client.private_reserve_target_override > 0:
        return float(client.private_reserve_target_override)
    return (6.0 * float(client.expense_budget or 0)) + float(client.deductibles_total or 0)

@main_bp.route('/')
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)

@main_bp.route('/client/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob_str = request.form.get('dob')
        ssn = request.form.get('ssn_last_four')
        salary = float(request.form.get('monthly_salary', 0))
        budget = float(request.form.get('expense_budget', 0))
        deductibles_total = float(request.form.get('deductibles_total', 0))
        target_override_raw = request.form.get('private_reserve_target_override', '').strip()
        target_override = float(target_override_raw) if target_override_raw else None
        
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        
        new_client = Client(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            ssn_last_four=ssn,
            monthly_salary=salary,
            expense_budget=budget,
            deductibles_total=deductibles_total,
            private_reserve_target_override=target_override
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully!', 'success')
        return redirect(url_for('main.client_detail', client_id=new_client.id))
    
    return render_template('add_client.html')

@main_bp.route('/client/<int:client_id>')
def client_detail(client_id):
    client = Client.query.get_or_404(client_id)
    private_reserve_target = get_private_reserve_target(client)
    return render_template('client_detail.html', client=client, private_reserve_target=private_reserve_target)

@main_bp.route('/client/<int:client_id>/account/add', methods=['POST'])
def add_account(client_id):
    account_type = request.form.get('account_type')
    account_name = request.form.get('account_name')
    ssn_last_four = request.form.get('account_number_last_four')
    owner = request.form.get('owner')
    
    new_account = Account(
        client_id=client_id,
        account_type=account_type,
        account_name=account_name,
        account_number_last_four=ssn_last_four,
        owner=owner
    )
    db.session.add(new_account)
    db.session.commit()
    return redirect(url_for('main.client_detail', client_id=client_id))

@main_bp.route('/client/<int:client_id>/edit', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        client.first_name = request.form.get('first_name')
        client.last_name = request.form.get('last_name')
        dob_str = request.form.get('dob')
        client.dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        client.ssn_last_four = request.form.get('ssn_last_four')
        client.monthly_salary = float(request.form.get('monthly_salary', 0))
        client.expense_budget = float(request.form.get('expense_budget', 0))
        client.deductibles_total = float(request.form.get('deductibles_total', 0))
        target_override_raw = request.form.get('private_reserve_target_override', '').strip()
        client.private_reserve_target_override = float(target_override_raw) if target_override_raw else None
        
        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('main.client_detail', client_id=client.id))
    
    return render_template('edit_client.html', client=client)

@main_bp.route('/client/<int:client_id>/report/new', methods=['GET', 'POST'])
def new_report(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        report_date_str = request.form.get('report_date')
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date() if report_date_str else datetime.utcnow().date()
        
        report = Report(client_id=client_id, report_date=report_date)
        db.session.add(report)
        db.session.commit()
        
        # Save balances
        for account in client.accounts:
            balance_val = float(request.form.get(f'balance_{account.id}', 0))
            cash_balance_val = float(request.form.get(f'cash_balance_{account.id}', 0))
            
            balance = Balance(
                report_id=report.id,
                account_id=account.id,
                balance=balance_val,
                cash_balance=cash_balance_val,
                as_of_date=report_date
            )
            db.session.add(balance)
        
        db.session.commit()
        return redirect(url_for('main.report_detail', report_id=report.id))

    # Get last report values for reference
    last_report = Report.query.filter_by(client_id=client_id).order_by(Report.report_date.desc()).first()
    last_balances = {}
    if last_report:
        for b in last_report.balances:
            last_balances[b.account_id] = {'balance': b.balance, 'cash': b.cash_balance}

    today_date = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('new_report.html', client=client, last_balances=last_balances, today_date=today_date)

@main_bp.route('/report/<int:report_id>')
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    client = report.client
    
    # Calculate totals
    totals = calculate_report_totals(report)
    
    return render_template('report_detail.html', report=report, client=client, totals=totals)

@main_bp.route('/report/<int:report_id>/sacs')
def generate_sacs(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        client = report.client
        totals = calculate_report_totals(report)
        pdf = generate_pdf('pdf/sacs.html', {'report': report, 'client': client, 'totals': totals})
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=SACS_{client.last_name}_{report.report_date.strftime("%Y%m%d")}.pdf'
        return response
    except Exception:
        traceback.print_exc()
        return "SACS PDF generation failed. Check server logs for details.", 500

@main_bp.route('/report/<int:report_id>/tcc')
def generate_tcc(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        client = report.client
        totals = calculate_report_totals(report)
        balances = {b.account_id: b for b in report.balances}
        pdf = generate_pdf('pdf/tcc.html', {'report': report, 'client': client, 'totals': totals, 'balances': balances})
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=TCC_{client.last_name}_{report.report_date.strftime("%Y%m%d")}.pdf'
        return response
    except Exception:
        traceback.print_exc()
        return "TCC PDF generation failed. Check server logs for details.", 500

@main_bp.route('/report/<int:report_id>/canva')
def export_canva(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        client = report.client
        totals = calculate_report_totals(report)
        balances = {b.account_id: b for b in report.balances}
        pdf = generate_pdf('pdf/tcc.html', {'report': report, 'client': client, 'totals': totals, 'balances': balances})
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=CANVA_IMPORT_{client.last_name}.pdf'
        return response
    except Exception:
        traceback.print_exc()
        return "Canva export failed. Check server logs for details.", 500

def calculate_report_totals(report):
    client = report.client
    balances = {b.account_id: b for b in report.balances}
    
    private_reserve_balance = 0.0
    for account in client.accounts:
        if account.account_type != 'private_reserve':
            continue
        b = balances.get(account.id)
        if b:
            private_reserve_balance += float(b.balance or 0)

    private_reserve_target = get_private_reserve_target(client)

    totals = {
        'inflow': client.monthly_salary,
        'outflow': client.expense_budget,
        'excess': client.monthly_salary - client.expense_budget,
        'private_reserve_balance': private_reserve_balance,
        'private_reserve_target': private_reserve_target,
        'private_reserve_target_met': private_reserve_balance >= private_reserve_target if private_reserve_target else False,
        'retirement_client1': 0.0,
        'retirement_client2': 0.0,
        'non_retirement': 0.0,
        'trust': 0.0,
        'liabilities': 0.0,
        'net_worth': 0.0
    }
    
    for account in client.accounts:
        b = balances.get(account.id)
        if not b: continue
        
        if account.account_type == 'retirement':
            if account.owner == 'client1':
                totals['retirement_client1'] += b.balance
            elif account.owner == 'client2':
                totals['retirement_client2'] += b.balance
        elif account.account_type == 'non-retirement':
            totals['non_retirement'] += b.balance
        elif account.account_type == 'trust':
            totals['trust'] += b.balance
        elif account.account_type == 'liability':
            totals['liabilities'] += b.balance
            
    totals['net_worth'] = totals['retirement_client1'] + totals['retirement_client2'] + totals['non_retirement'] + totals['trust']
    
    return totals
