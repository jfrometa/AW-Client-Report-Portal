from app import create_app
from app.models import Client, Report
from app.routes import calculate_report_totals


def assert_close(actual, expected, name):
    if round(float(actual), 2) != round(float(expected), 2):
        raise SystemExit(f"{name} mismatch: got {actual}, expected {expected}")


def main():
    app = create_app()
    with app.app_context():
        client = Client.query.filter_by(first_name="John", last_name="Doe").first()
        if not client:
            raise SystemExit("John Doe not found. Run scripts/seed_demo_data.py first.")

        report = Report.query.filter_by(client_id=client.id).order_by(Report.report_date.desc()).first()
        if not report:
            raise SystemExit("No report found for John Doe. Run scripts/seed_demo_data.py first.")

        totals = calculate_report_totals(report)

        assert_close(totals["excess"], 4000.0, "SACS excess")
        assert_close(totals["private_reserve_target"], 71000.0, "Private reserve target")
        assert_close(totals["retirement_client1"], 26000.0, "Client 1 retirement total")
        assert_close(totals["retirement_client2"], 50000.0, "Client 2 retirement total")
        assert_close(totals["non_retirement"], 50000.0, "Non-retirement total")
        assert_close(totals["trust"], 450000.0, "Trust total")
        assert_close(totals["net_worth"], 576000.0, "Grand total net worth")
        assert_close(totals["liabilities"], 215000.0, "Liabilities total")

        print("PRD math verification passed for John Doe.")


if __name__ == "__main__":
    main()

