import pandas as pd

def run_reconciliation():
    # --- Load Sales Register ---
    sales_register = pd.read_excel("sales_register.xlsx")
    sales_register.columns = sales_register.columns.str.strip()

    # --- Load GSTR-1 and GSTR-3B ---
    gstr1 = pd.read_excel("gstr1.xlsx", skiprows=6)
    gstr3b = pd.read_excel("gstr3b.xlsx", skiprows=6)

    # Clean column names
    gstr1.columns = gstr1.columns.str.strip()
    gstr3b.columns = gstr3b.columns.str.strip()

    # --- Aggregate Sales Register by State ---
    sales_summary = sales_register.groupby("Place of Supply")[["Taxable value","CGST","SGST","IGST"]].sum()
    sales_summary = sales_summary.reset_index()
    sales_summary.rename(columns={"Place of Supply":"State"}, inplace=True)

    # Select correct columns from GSTR-1 and GSTR-3B
    gstr1_clean = gstr1[["Unnamed: 1","Unnamed: 45"]].rename(
        columns={"Unnamed: 1":"State","Unnamed: 45":"TotalFiled_GSTR1"}
    )
    gstr3b_clean = gstr3b[["Unnamed: 1","Unnamed: 45"]].rename(
        columns={"Unnamed: 1":"State","Unnamed: 45":"TotalFiled_GSTR3B"}
    )

    # Merge Sales Summary with GSTR-1 and GSTR-3B
    recon1 = pd.merge(sales_summary, gstr1_clean, on="State", how="left")
    recon_final = pd.merge(recon1, gstr3b_clean, on="State", how="left")

    # --- Add Difference Calculations ---
    recon_final["Diff_Sales_vs_GSTR1"] = recon_final["Taxable value"] - recon_final["TotalFiled_GSTR1"]
    recon_final["Diff_GSTR1_vs_GSTR3B"] = recon_final["TotalFiled_GSTR1"] - recon_final["TotalFiled_GSTR3B"]

    # --- Flag mismatches ---
    recon_final["Mismatch_Flag"] = (recon_final["Diff_Sales_vs_GSTR1"] != 0) | (recon_final["Diff_GSTR1_vs_GSTR3B"] != 0)

    # --- Summary ---
    mismatch_count = recon_final["Mismatch_Flag"].sum()
    overall_totals = recon_final[["Taxable value","TotalFiled_GSTR1","TotalFiled_GSTR3B"]].sum()

    # --- Export to Excel ---
    recon_final.to_excel("GST_Reconciliation.xlsx", index=False)

    return {
        "data": recon_final,
        "mismatch_count": mismatch_count,
        "overall_totals": overall_totals
    }

# Allow standalone run for debugging
if __name__ == "__main__":
    result = run_reconciliation()
    print(result["data"].head(20))
    print(f"\nTotal mismatched states: {result['mismatch_count']}")
    print("\nOverall Totals:")
    print(result["overall_totals"])
    print("\nReconciliation results have been saved to GST_Reconciliation.xlsx")