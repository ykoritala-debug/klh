from neo4j import GraphDatabase

# Replace with your actual connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "yaminikoritala"

driver = GraphDatabase.driver(uri, auth=(username, password))

def fetch_mismatches():
    query = """
    MATCH (r1:Return {type:'GSTR1'})-[:CONTAINS]->(i:Invoice)
    WHERE NOT ( (i)<-[:CONTAINS]-(:Return {type:'GSTR2B'}) )
    RETURN i.invoice_no AS invoice_no, 
           i.amount AS amount, 
           i.gst_amount AS gst_amount,
           CASE WHEN i.amount > 5000 THEN 'High Risk' ELSE 'Low Risk' END AS risk_level
    """
    with driver.session(database="yaminikoritala") as session:
        result = session.run(query)
        for record in result:
            print(record["invoice_no"], record["amount"], record["gst_amount"], record["risk_level"])

if __name__ == "__main__":
    fetch_mismatches()
    driver.close()