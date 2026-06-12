# Student Dropout Prediction System (SDPS)

AI-powered early warning dashboard for student retention and dropout risk assessment.

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
cd dropout_app
streamlit run app.py
```

### Default Login
- Username: admin
- Email: admin@gmail.com
- Password: SDPSAdmin@2024!

**Important:** Change the default password before deploying to production.

---

## Features

- Individual Student Assessment - Predict dropout risk for single students
- Cohort Triage - Batch process and prioritize entire student cohorts
- Secure Authentication - bcrypt password hashing with session management
- Database Storage - SQLite for persistent data storage
- Real-time Analytics - Risk distribution and priority queue visualization
- Professional UI - Clean, responsive dashboard interface
- Intervention Routing - Automated priority assignment and owner allocation
- Export Functionality - Download triage plans as CSV

---

## Project Structure

```
FinalYearProject/
├── dropout_app/
│   ├── app.py                    # Main Streamlit application
│   ├── database.py               # Database operations module
│   ├── dropout_model.pkl         # Pre-trained ML model
│   ├── sdps.db                   # SQLite database (auto-created)
│   ├── .env                      # Environment configuration
│   ├── .env.example              # Environment template
│   ├── migrate_csv_to_db.py      # Data migration script
│   └── MIGRATION_GUIDE.md        # Detailed migration docs
├── assets/
│   └── logo__2_-removebg-preview.png
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Technology Stack

- Framework: Streamlit 1.58.0
- ML/Data: scikit-learn, pandas, numpy
- Visualization: matplotlib, seaborn
- Database: SQLite
- Security: bcrypt, python-dotenv

---

## Security Configuration

### Using Environment Variables (Recommended)

Create a `.env` file in the `dropout_app` folder:
```env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
```

### For Deployment (Render, Heroku, etc.)

Set environment variables in your platform dashboard:
```
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
```

---

## Model Information

The ML model predicts student dropout risk based on:
- Demographic factors (age, marital status, gender)
- Academic background (previous qualification, course enrolled)
- Application details (mode, order, displaced status)
- Support factors (scholarship, special needs, international)

### Risk Categories
- HIGH RISK (>=70% probability) - Immediate intervention required
- MODERATE RISK (40-70%) - Proactive support recommended
- LOW RISK (<40%) - Routine monitoring

### Priority Bands
- P1 - Immediate (80-100) - Retention Lead
- P2 - High (60-79) - Academic Advisor
- P3 - Medium (40-59) - Program Coordinator
- P4 - Routine (<40) - Student Support Desk

---

## Database Operations

```python
from database import Database

db = Database()

# Create admin
db.create_admin("username", "password")

# Verify login
db.verify_admin("username", "password")

# Save prediction
db.save_prediction(age=20, marital_status="Single", ...)

# Get all predictions
predictions = db.get_all_predictions()

# Get statistics
stats = db.get_prediction_stats()
```

---

## Migration from CSV

If you have an existing `prediction_history.csv` file:

```bash
cd dropout_app
python migrate_csv_to_db.py
```

This will import all historical predictions into the database.

---

## Troubleshooting

### Module not found errors
Run `pip install -r requirements.txt`

### Can't login with default credentials
Delete `dropout_app/sdps.db` and restart the app

### Database permission errors
Ensure the `dropout_app` directory has write permissions

### Old predictions not showing
Run the migration script: `python dropout_app/migrate_csv_to_db.py`

---

## Deployment

### Render Deployment

1. Push code to GitHub repository
2. Create new Web Service on Render
3. Set environment variables:
   - ADMIN_USERNAME
   - ADMIN_PASSWORD
4. Deploy

**Note:** Render free tier has ephemeral storage. For production, upgrade to paid tier or use PostgreSQL.

---

## License

Educational project - Final Year Project

---

## Acknowledgments

- UCI Machine Learning Repository for the dataset
- Streamlit framework
- scikit-learn for ML capabilities
