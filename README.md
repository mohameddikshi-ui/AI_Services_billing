# AI Analytics Service

FastAPI-based AI analytics microservice for Jewellery Work Order and Inventory Optimization.

---

# Features

- Inventory Recommendation System
- Top Selling Product Analysis
- Dead Stock Detection
- Demand Forecasting
- Smart Alerts System
- Purchase Pattern Analysis
- Trend Analysis
- Category Performance Analysis
- Seasonal Insights
- AI Auto Insights

---

# Tech Stack

- FastAPI
- SQLAlchemy
- SQL Server
- PyODBC
- Python

---

# Project Structure

ai-service/

├── app/

│ ├── api/

│ ├── services/

│ ├── repository/

│ ├── core/

│ ├── utils/

│ ├── constants/

│ └── models/

├── main.py

├── requirements.txt

├── .env.example

└── README.md

---

# Setup

## Install dependencies

pip install -r requirements.txt

---

# Run Server

uvicorn main:app --reload

---

# API Documentation

Swagger UI:

http://127.0.0.1:8000/docs

---

# Environment Variables

Create `.env` file:

DB_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes

---

# Notes

- This service is designed as a standalone AI analytics microservice.
- Intended for integration with existing .NET backend systems.
- Supports scalable future AI/ML upgrades.

---

# IIS Publish

This folder is prepared to run on IIS through HttpPlatformHandler.

## Server prerequisites

- IIS with HttpPlatformHandler installed.
- Python 3.13 or a compatible Python 3 version installed on the server.
- Microsoft ODBC Driver 18 for SQL Server installed.
- An IIS application pool identity that can read this folder and write to `logs/`.

## Publish steps

1. Copy this project folder to the IIS site path.
2. Open PowerShell in the project folder and run:

```powershell
.\scripts\prepare-iis.ps1
```

On a cloud/IIS server, prefer a Python install that is available to all users, not a per-user Administrator install. For example:

```powershell
.\scripts\prepare-iis.ps1 -Python C:\Python313\python.exe -RecreateVenv
```

3. Update `.env` with the real SQL Server connection string:

```env
DB_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

4. Point the IIS site/application to this folder. If the IIS application alias is not `testai`, update `APP_ROOT_PATH` and `--root-path` in `web.config` to match the alias.
5. Restart the IIS site or run `iisreset`.
6. Verify:

```text
https://your-domain/health
https://your-domain/docs
```

The included `web.config` starts Uvicorn with `main:app` on the dynamic port provided by IIS.

## Troubleshooting

### HTTP Error 500.19 / 0x8007000d

If IIS fails before the request reaches FastAPI and reports `web.config` as invalid, verify that HttpPlatformHandler is installed on the server. The included `web.config` uses the `<httpPlatform>` IIS section, and IIS cannot read that section unless the module is registered.

Install the x64 HttpPlatformHandler for IIS, then restart IIS:

```powershell
iisreset
```

After that, browse to:

```text
http://localhost/testai/health
```

### Python executable access denied

If the log says Python cannot run from an Administrator profile path, for example:

```text
C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe: Access is denied
```

Install Python for all users, or install it to a system path such as `C:\Python313`, then rebuild the virtual environment:

```powershell
.\scripts\prepare-iis.ps1 -Python C:\Python313\python.exe -RecreateVenv
iisreset
```
