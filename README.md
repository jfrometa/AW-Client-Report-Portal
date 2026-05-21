# AW Client Report Portal

A streamlined financial planning portal for EF to generate polished quarterly SACS (cashflow) and TCC (net worth) PDF reports in minutes instead of a full day.

## Overview

This portal replaces a manual, error-prone process involving multiple data sources (Pinnacle Bank, Charles Schwab, Zillow) and manual assembly in Canva and Word documents.

### Key Features

- **Client Management**: Centralized CRM for client static data (names, DOB, SSN, account types, salary, budget)
- **Quarterly Data Entry**: Smart forms pre-populated with static data and last known values
- **Automated Calculations**: Real-time math for inflow/outflow, net worth, and account totals
- **PDF Generation**: Pixel-perfect SACS and TCC reports matching existing firm branding
- **Canva Export**: Download PDFs for manual adjustments in Canva

## Tech Stack

- **Backend**: Python 3.10+ with Flask
- **Database**: SQLite (file-based, lightweight)
- **PDF Generation**: WeasyPrint
- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+)
- **Deployment**: Railway with persistent volume

## Project Structure

```text
AW-Client-Report-Portal/
├── app/
│   ├── __init__.py          # Flask app factory & database initialization
│   ├── models.py            # SQLAlchemy models (Client, Account, Report, Balance)
│   ├── routes.py            # All Flask routes & business logic
│   ├── utils.py             # PDF generation utilities
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base layout with navigation
│   │   ├── index.html       # Dashboard (client list)
│   │   ├── add_client.html  # New client form
│   │   ├── edit_client.html # Edit client form
│   │   ├── client_detail.html # Client profile & accounts
│   │   ├── new_report.html  # Quarterly data entry form
│   │   ├── report_detail.html # Report summary & download buttons
│   │   └── pdf/             # PDF templates for WeasyPrint
│   │       ├── sacs.html    # SACS cashflow report template
│   │       └── tcc.html     # TCC net worth report template
│   └── static/              # Static assets (CSS, JS, images)
│       ├── css/
│       ├── js/
│       └── img/
├── instance/                 # SQLite database directory
│   └── portal.db            # Auto-generated database file
├── main.py                  # Application entry point
├── requirements.txt          # Python dependencies
├── Procfile                 # Railway deployment config
├── nixpacks.toml            # Nixpacks build config (WeasyPrint deps)
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone git@github.com:jfrometa/AW-Client-Report-Portal.git
   cd AW-Client-Report-Portal
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5001`

### Railway Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin git@github.com:jfrometa/AW-Client-Report-Portal.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Connect your GitHub repository to Railway
   - Railway will auto-detect Python and deploy using the Procfile
   - **Important**: Add a persistent volume mount at `/app/instance` to store the SQLite database

3. **Environment Variables**
   Set the following in Railway:
   - `RAILWAY_DATABASE_PATH`: `/app/instance/portal.db`
   - `SECRET_KEY`: Generate a secure random string

## Usage

## Demo Data & PRD Math Verification

To populate a couple of demo clients (including the John Doe dataset aligned to the PRD math rules):

```bash
python scripts/seed_demo_data.py
```

To verify the PRD-required calculation outputs for John Doe:

```bash
python scripts/verify_prd_math.py
```

### Adding a New Client

1. Click **Add Client** on the dashboard
2. Fill in personal information (name, DOB, SSN last 4)
3. Enter financial baseline (monthly salary, expense budget, deductibles; optional target override)
4. Click **Create Client**

### Managing Accounts

1. Open a client's profile
2. Click **+ Add Account**
3. Select account type (retirement, non-retirement, trust, liability)
4. Assign owner (Client 1, Client 2, or Joint)
5. Enter last 4 digits of account number

### Generating Quarterly Reports

1. From client profile, click **Generate Report**
2. Enter current balances for each account
3. Use **"Use Last"** button to auto-fill unchanged values
4. Click **Save & Calculate**

### Downloading Reports

On the Report Details page:
- **Download SACS PDF**: Cashflow bubble diagram
- **Download TCC PDF**: Net worth circle chart
- **Export to Canva**: PDF formatted for Canva editing

## Data Model

### Client
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| first_name | String | Client's first name |
| last_name | String | Client's last name |
| dob | Date | Date of birth |
| ssn_last_four | String | Last 4 digits of SSN |
| monthly_salary | Float | Monthly inflow (take-home pay) |
| expense_budget | Float | Monthly outflow (agreed expenses) |
| private_reserve_target | Float | Target savings (6X expenses + deductibles) |

### Account
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| client_id | Integer | Foreign key to Client |
| account_type | String | retirement, non-retirement, trust, liability |
| account_name | String | e.g., "Schwab Brokerage" |
| account_number_last_four | String | Last 4 digits |
| owner | String | client1, client2, or joint |

### Report & Balance
- **Report**: Links a client to a specific quarter's data
- **Balance**: Records the balance for each account as of the report date

## Calculations

### SACS (Cashflow)
- **Inflow**: Monthly salary (from client profile)
- **Outflow**: Expense budget (from client profile)
- **Excess**: Inflow - Outflow

### TCC (Net Worth)
- **Client 1 Retirement**: Sum of Client 1's retirement accounts
- **Client 2 Retirement**: Sum of Client 2's retirement accounts
- **Non-Retirement**: Sum of all non-retirement accounts
- **Trust**: Sum of trust/property values (from Zillow)
- **Grand Total**: Retirement 1 + Retirement 2 + Non-Retirement + Trust
- **Liabilities**: Sum of all liabilities (displayed separately)

## Support

For questions or issues, contact the development team.

---

*Internal Use Only - EF Financial Planning*
