from pathlib import Path

from app import create_app
from app.models import Client, Report
from app.routes import calculate_report_totals
from app.utils import generate_pdf


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
        pdf_bytes = generate_pdf("pdf/sacs.html", {"report": report, "client": client, "totals": totals})
        out_path = Path("tmp/sacs_preview.pdf")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(pdf_bytes)
        print(str(out_path))


if __name__ == "__main__":
    main()

