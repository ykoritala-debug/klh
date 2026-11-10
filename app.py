from fastapi import FastAPI
from contextlib import asynccontextmanager
from neo4j import GraphDatabase
from sales_register import run_reconciliation   # Import reconciliation function

# -------------------------------
# Neo4j connection
# -------------------------------
uri = "bolt://localhost:7687"
username = "neo4j"
password = "yaminikoritala"
driver = GraphDatabase.driver(uri, auth=(username, password))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI app started, Neo4j driver ready.")
    yield
    driver.close()
    print("Neo4j driver closed.")

app = FastAPI(lifespan=lifespan)
@app.get("/")
def home():
    return {
        "message": "GST Reconciliation API is running"
    }

# -------------------------------
# Neo4j Mismatches endpoint
# -------------------------------
@app.get("/mismatches")
def get_mismatches():
    query = """
    MATCH (r1:Return {type:'GSTR1'})-[:CONTAINS]->(i:Invoice)
    WHERE NOT ( (i)<-[:CONTAINS]-(:Return {type:'GSTR2B'}) )
    RETURN i.invoice_no AS invoice_no,
           i.amount AS amount,
           i.gst_amount AS gst_amount,
           CASE WHEN i.amount > 5000 THEN 'High Risk' ELSE 'Low Risk' END AS risk_level
    """
    try:
        with driver.session(database="yaminikoritala") as session:
            result = session.run(query)
            return [
                {
                    "invoice_no": record["invoice_no"],
                    "amount": record["amount"],
                    "gst_amount": record["gst_amount"],
                    "risk_level": record["risk_level"]
                }
                for record in result
            ]
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# Neo4j Reconciliation endpoint
# -------------------------------
@app.get("/reconciliation")
def tax_mismatch_report(period: str = "2025-01"):
    query = """
    MATCH (t:Taxpayer)-[:FILED]->(r1:Return {type:'GSTR1', period:$period}),
          (t)-[:FILED]->(r3:Return {type:'GSTR3B', period:$period})
    WHERE r1.total_tax <> r3.total_tax
    RETURN DISTINCT t.gstin AS gstin,
           t.name AS name,
           coalesce(t.state,'N/A') AS state,
           r1.period AS period,
           r1.total_tax AS GSTR1,
           r3.total_tax AS GSTR3B,
           r1.total_tax - r3.total_tax AS risk_amount
    """
    try:
        with driver.session(database="yaminikoritala") as session:
            result = session.run(query, {"period": period})
            return [dict(r) for r in result]
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# Excel Reconciliation endpoint
# -------------------------------
@app.get("/excel-reconciliation")
def excel_reconciliation(state: str = None):
    try:
        result = run_reconciliation()
        data = result["data"]

        # Flexible filtering by state (case-insensitive, partial, multiple states)
        if state:
            states = [s.strip().lower() for s in state.split(",")]
            mask = data["State"].str.strip().str.lower().apply(
                lambda x: any(s in x for s in states)
            )
            data = data[mask]

        return {
            "mismatch_count": int((data["Mismatch_Flag"]).sum()),
            "overall_totals": data[["Taxable value","TotalFiled_GSTR1","TotalFiled_GSTR3B"]].sum().to_dict(),
            "reconciliation_data": data.to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# Unified Full Report endpoint
# -------------------------------
@app.get("/full-report")
def full_report(period: str = "2025-01", state: str = None):
    try:
        # Neo4j mismatches
        mismatches_query = """
        MATCH (r1:Return {type:'GSTR1'})-[:CONTAINS]->(i:Invoice)
        WHERE NOT ( (i)<-[:CONTAINS]-(:Return {type:'GSTR2B'}) )
        RETURN i.invoice_no AS invoice_no,
               i.amount AS amount,
               i.gst_amount AS gst_amount,
               CASE WHEN i.amount > 5000 THEN 'High Risk' ELSE 'Low Risk' END AS risk_level
        """
        with driver.session(database="yaminikoritala") as session:
            mismatches = [
                {
                    "invoice_no": record["invoice_no"],
                    "amount": record["amount"],
                    "gst_amount": record["gst_amount"],
                    "risk_level": record["risk_level"]
                }
                for record in session.run(mismatches_query)
            ]

            # Neo4j reconciliation (filtered by period)
            reconciliation_query = """
            MATCH (t:Taxpayer)-[:FILED]->(r1:Return {type:'GSTR1', period:$period}),
                  (t)-[:FILED]->(r3:Return {type:'GSTR3B', period:$period})
            WHERE r1.total_tax <> r3.total_tax
            RETURN DISTINCT t.gstin AS gstin,
                   t.name AS name,
                   coalesce(t.state,'N/A') AS state,
                   r1.period AS period,
                   r1.total_tax AS GSTR1,
                   r3.total_tax AS GSTR3B,
                   r1.total_tax - r3.total_tax AS risk_amount
            """
            reconciliation = [dict(r) for r in session.run(reconciliation_query, {"period": period})]

        # Excel reconciliation (filtered by state)
        excel_result = run_reconciliation()
        data = excel_result["data"]
        if state:
            states = [s.strip().lower() for s in state.split(",")]
            mask = data["State"].str.strip().str.lower().apply(
                lambda x: any(s in x for s in states)
            )
            data = data[mask]

        excel_filtered = {
            "mismatch_count": int((data["Mismatch_Flag"]).sum()),
            "overall_totals": data[["Taxable value","TotalFiled_GSTR1","TotalFiled_GSTR3B"]].sum().to_dict(),
            "reconciliation_data": data.to_dict(orient="records")
        }

        return {
            "neo4j_mismatches": mismatches,
            "neo4j_reconciliation": reconciliation,
            "excel_reconciliation": excel_filtered
        }
    except Exception as e:
        return {"error": str(e)}