from neo4j import GraphDatabase
import pandas as pd
import matplotlib.pyplot as plt

uri = "bolt://127.0.0.1:7687"
username = "neo4j"
password = "yaminikoritala"

driver = GraphDatabase.driver(uri, auth=(username, password))

def reconciliation_summary(period="2025-01", state="MH"):
    # Query for matched invoices
    matched_query = """
        MATCH (s:Taxpayer)-[:FILED]->(r1:Return {type:'GSTR1', period:$period})
        MATCH (b:Taxpayer)<-[:SOLD_TO]-(i:Invoice {period:$period})
        MATCH (r2:Return {type:'GSTR2B', period:$period})-[:CONTAINS]->(i)
        RETURN count(i) AS matched_count
    """

    # Query for mismatched invoices (present in GSTR1 but missing in GSTR2B)
    mismatched_query = """
        MATCH (s:Taxpayer)-[:FILED]->(r1:Return {type:'GSTR1', period:$period})-[:CONTAINS]->(i:Invoice)
        WHERE NOT EXISTS {
            MATCH (:Return {type:'GSTR2B', period:$period})-[:CONTAINS]->(i)
        }
        RETURN count(i) AS mismatched_count
    """

    with driver.session(database="yaminikoritala") as session:
        matched = session.run(matched_query, period=period).single()["matched_count"]
        mismatched = session.run(mismatched_query, period=period).single()["mismatched_count"]

    # Build DataFrame
    df = pd.DataFrame({
        "Status": ["Matched", "Mismatched"],
        "Count": [matched, mismatched]
    })

    # --- Pie Chart ---
    plt.figure(figsize=(6,6))
    plt.pie(df["Count"], labels=df["Status"], autopct="%1.1f%%", colors=["#4CAF50", "#F44336"])
    plt.title(f"Matched vs Mismatched Invoices ({period}, {state})")
    plt.savefig(f"match_mismatch_{period}_{state}.png")
    plt.show()

    print(df)

if __name__ == "__main__":
    reconciliation_summary(period="2025-01", state="MH")
    driver.close()