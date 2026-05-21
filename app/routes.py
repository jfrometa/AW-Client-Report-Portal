from datetime import date, datetime
import traceback

from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for

from . import db
from .models import (
    Account,
    BalanceEntry,
    Household,
    Individual,
    Liability,
    LiabilityValue,
    Report,
    TrustAsset,
    TrustValue,
)
from .utils import generate_pdf

main_bp = Blueprint('main', __name__)

def parse_float(value, default=0.0):
    if value is None:
        return float(default)
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    if value == "":
        return float(default)
    return float(value)

def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_private_reserve_target(household: Household):
    if (
        household.private_reserve_target_override is not None
        and household.private_reserve_target_override > 0
    ):
        return float(household.private_reserve_target_override)
    return (6.0 * float(household.expense_budget or 0)) + float(
        household.deductibles_total or 0
    )

@main_bp.route('/')
def index():
    households = Household.query.order_by(Household.created_at.desc()).all()
    return render_template('index.html', households=households)

@main_bp.route('/household/<int:household_id>/toggle', methods=['POST'])
def toggle_household_active(household_id):
    household = Household.query.get_or_404(household_id)
    household.active = not household.active
    db.session.commit()
    flash("Household status updated!", "success")
    return redirect(url_for('main.index'))

@main_bp.route('/household/add', methods=['GET', 'POST'])
def add_household():
    if request.method == 'POST':
        household_name = request.form.get('household_name') or ""
        monthly_salary = parse_float(request.form.get('monthly_salary'), 0)
        expense_budget = parse_float(request.form.get('expense_budget'), 0)
        deductibles_total = parse_float(request.form.get('deductibles_total'), 0)
        target_override_raw = (request.form.get("private_reserve_target_override") or "").strip()
        private_reserve_target_override = parse_float(target_override_raw, 0) if target_override_raw else None
        active = request.form.get("active") == "on"

        client1_first = request.form.get("client1_first_name") or ""
        client1_last = request.form.get("client1_last_name") or ""
        client1_dob = parse_date(request.form.get("client1_dob"))
        client1_ssn = request.form.get("client1_ssn_last_four") or ""

        client2_first = (request.form.get("client2_first_name") or "").strip()
        client2_last = (request.form.get("client2_last_name") or "").strip()
        client2_dob = parse_date(request.form.get("client2_dob"))
        client2_ssn = (request.form.get("client2_ssn_last_four") or "").strip()

        household = Household(
            household_name=household_name.strip() or f"{client1_last} Family",
            monthly_salary=monthly_salary,
            expense_budget=expense_budget,
            deductibles_total=deductibles_total,
            private_reserve_target_override=private_reserve_target_override,
            active=active,
        )
        db.session.add(household)
        db.session.flush()

        db.session.add(
            Individual(
                household_id=household.id,
                designation="client1",
                first_name=client1_first,
                last_name=client1_last,
                dob=client1_dob,
                ssn_last_four=client1_ssn,
            )
        )

        if client2_first and client2_last:
            db.session.add(
                Individual(
                    household_id=household.id,
                    designation="client2",
                    first_name=client2_first,
                    last_name=client2_last,
                    dob=client2_dob,
                    ssn_last_four=client2_ssn,
                )
            )

        db.session.commit()
        flash("Household added successfully!", "success")
        return redirect(url_for("main.household_detail", household_id=household.id))
    
    return render_template('add_household.html')

@main_bp.route('/household/<int:household_id>')
def household_detail(household_id):
    household = Household.query.get_or_404(household_id)
    individuals = sorted(household.individuals, key=lambda x: x.designation)
    private_reserve_target = get_private_reserve_target(household)
    return render_template(
        "household_detail.html",
        household=household,
        individuals=individuals,
        private_reserve_target=private_reserve_target,
    )

@main_bp.route("/household/<int:household_id>/account/add", methods=["POST"])
def add_account(household_id):
    household = Household.query.get_or_404(household_id)
    category = (request.form.get("category") or "").strip()
    account_type = (request.form.get("account_type") or "").strip()
    institution_name = (request.form.get("institution_name") or "").strip()
    account_name = (request.form.get("account_name") or "").strip()
    last_four = (request.form.get("account_number_last_four") or "").strip()

    scope = (request.form.get("scope") or "household").strip()
    owner_individual_id_raw = (request.form.get("individual_id") or "").strip()
    attributed_individual_id_raw = (request.form.get("attributed_individual_id") or "").strip()

    individual_id = int(owner_individual_id_raw) if owner_individual_id_raw else None
    attributed_individual_id = int(attributed_individual_id_raw) if attributed_individual_id_raw else None

    if category == "retirement" and not individual_id:
        flash("Retirement accounts must be assigned to Client 1 or Client 2.", "error")
        return redirect(url_for("main.household_detail", household_id=household_id))

    account = Account(
        household_id=household.id if scope == "household" else None,
        individual_id=individual_id if scope == "individual" else None,
        attributed_individual_id=attributed_individual_id,
        category=category,
        account_type=account_type,
        institution_name=institution_name,
        account_name=account_name,
        account_number_last_four=last_four,
    )
    db.session.add(account)
    db.session.commit()
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/household/<int:household_id>/edit", methods=["GET", "POST"])
def edit_household(household_id):
    household = Household.query.get_or_404(household_id)
    individuals = sorted(household.individuals, key=lambda x: x.designation)
    if request.method == 'POST':
        household.household_name = (request.form.get("household_name") or household.household_name).strip()
        household.monthly_salary = parse_float(request.form.get("monthly_salary"), 0)
        household.expense_budget = parse_float(request.form.get("expense_budget"), 0)
        household.deductibles_total = parse_float(request.form.get("deductibles_total"), 0)
        target_override_raw = (request.form.get("private_reserve_target_override") or "").strip()
        household.private_reserve_target_override = (
            parse_float(target_override_raw, 0) if target_override_raw else None
        )
        household.active = request.form.get("active") == "on"

        for designation in ["client1", "client2"]:
            ind = next((i for i in individuals if i.designation == designation), None)
            if not ind:
                continue
            ind.first_name = (request.form.get(f"{designation}_first_name") or ind.first_name).strip()
            ind.last_name = (request.form.get(f"{designation}_last_name") or ind.last_name).strip()
            ind.dob = parse_date(request.form.get(f"{designation}_dob")) or ind.dob
            ind.ssn_last_four = (request.form.get(f"{designation}_ssn_last_four") or ind.ssn_last_four).strip()

        db.session.commit()
        flash("Household updated successfully!", "success")
        return redirect(url_for("main.household_detail", household_id=household.id))
    
    return render_template("edit_household.html", household=household, individuals=individuals)


@main_bp.route("/household/<int:household_id>/trust/add", methods=["POST"])
def add_trust(household_id):
    household = Household.query.get_or_404(household_id)
    address = (request.form.get("property_address") or "").strip()
    if not address:
        flash("Property address is required.", "error")
        return redirect(url_for("main.household_detail", household_id=household_id))
    db.session.add(TrustAsset(household_id=household.id, property_address=address))
    db.session.commit()
    return redirect(url_for("main.household_detail", household_id=household_id))


@main_bp.route("/trust/<int:trust_id>/edit", methods=["POST"])
def edit_trust(trust_id):
    trust = TrustAsset.query.get_or_404(trust_id)
    address = (request.form.get("property_address") or trust.property_address).strip()
    trust.property_address = address
    db.session.commit()
    return redirect(url_for("main.household_detail", household_id=trust.household_id))


@main_bp.route("/trust/<int:trust_id>/delete", methods=["POST"])
def delete_trust(trust_id):
    trust = TrustAsset.query.get_or_404(trust_id)
    household_id = trust.household_id
    db.session.delete(trust)
    db.session.commit()
    return redirect(url_for("main.household_detail", household_id=household_id))


@main_bp.route("/household/<int:household_id>/liability/add", methods=["POST"])
def add_liability(household_id):
    loan_type = (request.form.get("loan_type") or "").strip()
    interest_rate = parse_float(request.form.get("interest_rate"), 0)
    if not loan_type:
        flash("Loan type is required.", "error")
        return redirect(url_for("main.household_detail", household_id=household_id))
    db.session.add(Liability(household_id=household_id, loan_type=loan_type, interest_rate=interest_rate))
    db.session.commit()
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/account/<int:account_id>/edit", methods=["POST"])
def edit_account(account_id):
    account = Account.query.get_or_404(account_id)
    household_id = account.household_id or account.individual.household_id
    
    category = (request.form.get("category") or account.category).strip()
    account_type = (request.form.get("account_type") or account.account_type).strip()
    institution_name = (request.form.get("institution_name") or account.institution_name).strip()
    account_name = (request.form.get("account_name") or account.account_name).strip()
    last_four = (request.form.get("account_number_last_four") or account.account_number_last_four).strip()

    scope = (request.form.get("scope") or "household").strip()
    owner_individual_id_raw = (request.form.get("individual_id") or "").strip()
    attributed_individual_id_raw = (request.form.get("attributed_individual_id") or "").strip()

    individual_id = int(owner_individual_id_raw) if owner_individual_id_raw else None
    attributed_individual_id = int(attributed_individual_id_raw) if attributed_individual_id_raw else None

    if category == "retirement" and not individual_id:
        flash("Retirement accounts must be assigned to Client 1 or Client 2.", "error")
        return redirect(url_for("main.household_detail", household_id=household_id))

    account.category = category
    account.account_type = account_type
    account.institution_name = institution_name
    account.account_name = account_name
    account.account_number_last_four = last_four
    account.household_id = household_id if scope == "household" else None
    account.individual_id = individual_id if scope == "individual" else None
    account.attributed_individual_id = attributed_individual_id

    db.session.commit()
    flash("Account updated successfully!", "success")
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/liability/<int:liability_id>/edit", methods=["POST"])
def edit_liability(liability_id):
    liability = Liability.query.get_or_404(liability_id)
    household_id = liability.household_id
    
    loan_type = (request.form.get("loan_type") or liability.loan_type).strip()
    interest_rate = parse_float(request.form.get("interest_rate"), 0)
    
    liability.loan_type = loan_type
    liability.interest_rate = interest_rate
    
    db.session.commit()
    flash("Liability updated successfully!", "success")
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/account/<int:account_id>/delete", methods=["POST"])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    household_id = account.household_id or account.individual.household_id
    db.session.delete(account)
    db.session.commit()
    flash("Account deleted successfully!", "success")
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/liability/<int:liability_id>/delete", methods=["POST"])
def delete_liability(liability_id):
    liability = Liability.query.get_or_404(liability_id)
    household_id = liability.household_id
    db.session.delete(liability)
    db.session.commit()
    flash("Liability deleted successfully!", "success")
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/report/<int:report_id>/delete", methods=["POST"])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    household_id = report.household_id
    db.session.delete(report)
    db.session.commit()
    flash("Report deleted successfully!", "success")
    return redirect(url_for("main.household_detail", household_id=household_id))

@main_bp.route("/household/<int:household_id>/report/new", methods=["GET", "POST"])
def new_report(household_id):
    household = Household.query.get_or_404(household_id)
    trust_asset = TrustAsset.query.filter_by(household_id=household_id).first()
    liabilities = Liability.query.filter_by(household_id=household_id).all()
    accounts = (
        Account.query.filter(
            (Account.household_id == household_id) | (Account.individual_id.in_([i.id for i in household.individuals]))
        )
        .order_by(Account.category.asc(), Account.account_type.asc(), Account.account_name.asc())
        .all()
    )
    if request.method == 'POST':
        report_date = parse_date(request.form.get("report_date")) or datetime.utcnow().date()

        report = Report(
            household_id=household_id,
            report_date=report_date,
            snapshot_monthly_salary=household.monthly_salary or 0.0,
            snapshot_expense_budget=household.expense_budget or 0.0,
            snapshot_deductibles_total=household.deductibles_total or 0.0,
            snapshot_private_reserve_target=get_private_reserve_target(household),
        )
        db.session.add(report)
        db.session.flush()

        for account in accounts:
            total_balance = parse_float(request.form.get(f"balance_{account.id}"), 0)
            cash_balance = parse_float(request.form.get(f"cash_balance_{account.id}"), 0)
            db.session.add(
                BalanceEntry(
                    report_id=report.id,
                    account_id=account.id,
                    total_balance=total_balance,
                    cash_balance=cash_balance,
                    as_of_date=report_date,
                )
            )

        if trust_asset:
            trust_value = parse_float(request.form.get("trust_zillow_value"), 0)
            db.session.add(
                TrustValue(
                    report_id=report.id,
                    trust_asset_id=trust_asset.id,
                    zillow_value=trust_value,
                    as_of_date=report_date,
                )
            )

        for liability in liabilities:
            balance = parse_float(request.form.get(f"liability_balance_{liability.id}"), 0)
            db.session.add(
                LiabilityValue(
                    report_id=report.id,
                    liability_id=liability.id,
                    current_balance=balance,
                    as_of_date=report_date,
                )
            )

        db.session.commit()
        return redirect(url_for("main.report_detail", report_id=report.id))

    last_report = (
        Report.query.filter_by(household_id=household_id)
        .order_by(Report.report_date.desc())
        .first()
    )
    last_account_values = {}
    last_trust_value = None
    last_liability_values = {}

    if last_report:
        for b in last_report.balance_entries:
            last_account_values[b.account_id] = {
                "balance": b.total_balance,
                "cash": b.cash_balance,
            }
        tv = last_report.trust_values[0] if last_report.trust_values else None
        if tv:
            last_trust_value = tv.zillow_value
        for lv in last_report.liability_values:
            last_liability_values[lv.liability_id] = lv.current_balance

    today_date = datetime.utcnow().strftime("%Y-%m-%d")
    return render_template(
        "new_report.html",
        household=household,
        accounts=accounts,
        trust_asset=trust_asset,
        liabilities=liabilities,
        last_account_values=last_account_values,
        last_trust_value=last_trust_value,
        last_liability_values=last_liability_values,
        today_date=today_date,
    )

@main_bp.route('/report/<int:report_id>')
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    household = report.household
    individuals = sorted(household.individuals, key=lambda x: x.designation)
    totals = calculate_report_totals(report)
    return render_template(
        "report_detail.html",
        report=report,
        household=household,
        individuals=individuals,
        totals=totals,
    )

@main_bp.route('/report/<int:report_id>/sacs')
def generate_sacs(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        household = report.household
        individuals = sorted(household.individuals, key=lambda x: x.designation)
        totals = calculate_report_totals(report)
        pdf = generate_pdf(
            "pdf/sacs.html",
            {"report": report, "household": household, "individuals": individuals, "totals": totals},
        )
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=SACS_{household.id}_{report.report_date.strftime("%Y%m%d")}.pdf'
        return response
    except Exception:
        traceback.print_exc()
        return "SACS PDF generation failed. Check server logs for details.", 500

@main_bp.route('/report/<int:report_id>/tcc')
def generate_tcc(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        household = report.household
        individuals = sorted(household.individuals, key=lambda x: x.designation)
        totals = calculate_report_totals(report)
        balances = {b.account_id: b for b in report.balance_entries}
        trust_value = report.trust_values[0] if report.trust_values else None
        liability_values = {lv.liability_id: lv for lv in report.liability_values}
        pdf = generate_pdf(
            "pdf/tcc.html",
            {
                "report": report,
                "household": household,
                "individuals": individuals,
                "totals": totals,
                "balances": balances,
                "trust_value": trust_value,
                "liability_values": liability_values,
            },
        )
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=TCC_{household.id}_{report.report_date.strftime("%Y%m%d")}.pdf'
        return response
    except Exception:
        traceback.print_exc()
        return "TCC PDF generation failed. Check server logs for details.", 500

@main_bp.route('/report/<int:report_id>/canva')
def export_canva(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        household = report.household
        individuals = sorted(household.individuals, key=lambda x: x.designation)
        totals = calculate_report_totals(report)
        balances = {b.account_id: b for b in report.balance_entries}
        trust_value = report.trust_values[0] if report.trust_values else None
        liability_values = {lv.liability_id: lv for lv in report.liability_values}
        pdf = generate_pdf(
            "pdf/tcc.html",
            {
                "report": report,
                "household": household,
                "individuals": individuals,
                "totals": totals,
                "balances": balances,
                "trust_value": trust_value,
                "liability_values": liability_values,
            },
        )
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=CANVA_IMPORT_{household.id}.pdf'
        return response
    except Exception:
        traceback.print_exc()
        return "Canva export failed. Check server logs for details.", 500

def calculate_report_totals(report):
    household = report.household
    balances = {b.account_id: b for b in report.balance_entries}

    client1 = next((i for i in household.individuals if i.designation == "client1"), None)
    client2 = next((i for i in household.individuals if i.designation == "client2"), None)

    retirement_client1 = 0.0
    retirement_client2 = 0.0
    non_retirement = 0.0
    private_reserve_balance = 0.0

    accounts = (
        Account.query.filter(
            (Account.household_id == household.id)
            | (Account.individual_id.in_([i.id for i in household.individuals]))
        )
        .all()
    )

    for account in accounts:
        b = balances.get(account.id)
        if not b:
            continue

        value = float(b.total_balance or 0)
        if account.category == "retirement":
            if client1 and account.individual_id == client1.id:
                retirement_client1 += value
            elif client2 and account.individual_id == client2.id:
                retirement_client2 += value
        elif account.category == "non_retirement":
            non_retirement += value
        elif account.category == "private_reserve":
            private_reserve_balance += value

    trust = 0.0
    if report.trust_values:
        trust = float(report.trust_values[0].zillow_value or 0)

    liabilities_total = 0.0
    for lv in report.liability_values:
        liabilities_total += float(lv.current_balance or 0)

    private_reserve_target = report.snapshot_private_reserve_target

    totals = {
        "inflow": float(report.snapshot_monthly_salary or 0),
        "outflow": float(report.snapshot_expense_budget or 0),
        "excess": float(report.snapshot_monthly_salary or 0) - float(report.snapshot_expense_budget or 0),
        "private_reserve_balance": private_reserve_balance,
        "private_reserve_target": private_reserve_target,
        "private_reserve_target_met": private_reserve_balance >= private_reserve_target
        if private_reserve_target
        else False,
        "retirement_client1": retirement_client1,
        "retirement_client2": retirement_client2,
        "non_retirement": non_retirement,
        "trust": trust,
        "liabilities": liabilities_total,
        "net_worth": retirement_client1 + retirement_client2 + non_retirement + trust,
    }

    return totals
