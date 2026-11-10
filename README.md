GST Reconciliation & Risk Analysis System
Overview

GST Reconciliation & Risk Analysis System is a FastAPI and Neo4j based solution developed for KLU Hyderabad Hackathon (Problem Statement 76).

The system automates GST return reconciliation by comparing GSTR-1, GSTR-3B, and invoice-level transaction records. It identifies mismatches, calculates tax differences, classifies risk levels, and generates consolidated reconciliation reports for easier compliance monitoring.

Features
Invoice-level mismatch detection
GSTR-1 vs GSTR-3B reconciliation
High Risk and Low Risk classification
Neo4j graph-based tax data analysis
Excel-based GST reconciliation
State-wise filtering support
REST API endpoints using FastAPI
Unified reconciliation reporting
Technology Stack

Backend:

Python
FastAPI
Uvicorn

Database:

Neo4j Graph Database

Data Processing:

Pandas
OpenPyXL

Data Sources:

GSTR-1 Excel Data
GSTR-3B Excel Data
Sales Register Data
Project Structure

app.py
 connect.py
 validation.py
 fetch_mismatches.py
 sales_register.py
 gstr1.xlsx
 gstr3b.xlsx
 sales_register.xlsx
 README.md

API Endpoints
GET /mismatches

Returns invoices present in GSTR-1 but missing in GSTR-2B along with risk classification.

GET /reconciliation

Compares GSTR-1 and GSTR-3B tax values and identifies discrepancies.

GET /excel-reconciliation

Performs reconciliation using Excel datasets and generates mismatch statistics.

Optional Parameter:

state = Andhra Pradesh

GET /full-report

Combines:

Neo4j Invoice Mismatches
Tax Reconciliation Results
Excel Reconciliation Results

into a single consolidated report.

Example:

http://127.0.0.1:8000/full-report?period=2025-01&state=andhra%20pradesh

Installation

Clone the repository:

git clone https://github.com/ykoritala-debug/klh.git

Move into the project directory:

cd klh

Install dependencies:

pip install fastapi uvicorn pandas openpyxl neo4j

Running Neo4j
Open Neo4j Desktop.
Start the database instance.
Ensure Neo4j is running on:

bolt://localhost:7687

Running the Application

Start FastAPI:

uvicorn app:app --reload

Open Swagger Documentation:

http://127.0.0.1:8000/docs

Sample Output

Invoice Mismatch Example:

Invoice Number: INV002
 Amount: 6000
 GST Amount: 1080
 Risk Level: High Risk

Reconciliation Example:

GSTIN: 27AAAAA1111A1Z5
 Name: ABC Suppliers
 GSTR-1 Tax: 1800
 GSTR-3B Tax: 2000
 Risk Amount: -200

Future Enhancements
Dashboard Visualization
Authentication and Role Management
Automated GST Filing Suggestions
PDF Report Generation
Cloud Deployment
Real-time GST Data Integration
Hackathon Problem Statement

Problem Statement 76: GST Reconciliation & Risk Analysis

The objective of this project is to automate GST reconciliation by identifying discrepancies between GST returns and transaction records, enabling better compliance monitoring and risk assessment.

Team

Developed as part of KLU Hyderabad Hackathon.

License

This project is intended for educational, research, and demonstration purposes.
## Demo Video

A complete walkthrough of the GST Reconciliation & Risk Analysis System, including API execution, reconciliation workflow, mismatch detection, and report generation.

Video Link:
https://drive.google.com/file/d/16KoqwILBasHRvj4NOE5ieuZBqwBA0JAD/view?usp=drivesdk

