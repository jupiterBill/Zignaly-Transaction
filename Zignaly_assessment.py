import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def analyze_transactions(csv_path, account_name, cutoff_timestamp, upload_to_sheets=False, sheet_name="Zignaly Report"):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Filter by cutoff date provided by user
    cutoff = pd.to_datetime(cutoff_timestamp)
    df_filtered = df[df['timestamp'] <= cutoff]

    # Focus on user account
    df_account = df_filtered[(df_filtered['from'] == account_name) | (df_filtered['to'] == account_name)].copy()

    # Determine transaction effect
    def calculate_effect(row):
        #easiest part of the assessment used for summation of final balance
        if row['to'] == account_name:   # income
            return row['amount']
        elif row['from'] == account_name:  # expenditure
            return -row['amount']
        return 0

    df_account['effect'] = df_account.apply(calculate_effect, axis=1)

    df_account["running_balance"] = df_account["effect"].cumsum()

    # Final balance
    final_balance = df_account['effect'].sum()

    # Totals by transaction type
    totals_by_type = df_account.groupby('type')['effect'].sum()

    # Income vs Expenditure
    income = df_account[df_account['effect'] > 0]['effect'].sum()
    expenditure = -df_account[df_account['effect'] < 0]['effect'].sum()

    largest_txn_row = df_account.loc[df_account["amount"].idxmax()]
    largest_txn = {"id": largest_txn_row.get("id"), "type": largest_txn_row["type"], "amount": float(largest_txn_row["amount"]), "timestamp": largest_txn_row["timestamp"]}
    most_freq_type = df_account["type"].mode().iat[0] if not df_account["type"].mode().empty else None
    # Print summary to console
    print("📊 Balance Report")
    print(f"Account: {account_name}")
    print(f"Cutoff Timestamp: {cutoff}")
    print(f"Final Balance: {final_balance:.2f}")
    print("\nTotals by Transaction Type:")
    print(totals_by_type)
    print(f"\nTotal Income: {income:.2f}")
    print(f"Total Expenditure: {expenditure:.2f}")
    print(f"Largest Transaction: {largest_txn['amount']:,.6f} (id={largest_txn['id']}, type={largest_txn['type']}, ts={largest_txn['timestamp']})")
    print(f"Most frequent transaction type: {most_freq_type}")

    #chart and summary creation 

    create_bar_chart_summary(totals_by_type, 
    final_balance, 
    income, 
    expenditure, 
    largest_txn,  
    account_name, )


    # Line chart running balance
    plot_running_balance(df_account, account_name, cutoff)

    # Save to Excel
    with pd.ExcelWriter("Zignaly_Balance_Report.xlsx") as writer:
        df_account.to_excel(writer, sheet_name="Filtered Transactions", index=False)
        summary_df = pd.DataFrame({
            "Metric": ["Final Balance", "Total Income", "Total Expenditure"],
            "Value": [final_balance, income, expenditure]
        })
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        totals_by_type.to_excel(writer, sheet_name="TotalsByType")

    print("\n✅ Results exported to Zignaly_Balance_Report.xlsx")

    # Pie chart: income vs expenditure
    plt.figure(figsize=(6, 6))
    plt.pie([income, expenditure], labels=["Income", "Expenditure"], autopct="%1.1f%%", colors=["green", "red"])
    plt.title("Income vs Expenditure")
    plt.savefig("income_vs_expenditure_pie.png")
    plt.close()


def create_bar_chart_summary( totals_by_type, 
    final_balance, 
    income, 
    expenditure, 
    largest_txn,  
    account_name, 
    ):
     # Create chart
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot bar chart for totals
    totals_by_type.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
    ax.set_title(f"Transaction Totals by Type for {account_name}", fontsize=14)
    ax.set_xlabel("Transaction Type")
    ax.set_ylabel("Total Amount")

    # Build summary text
    summary_text = (
        f" Balance Report\n\n"
        f"Account: {account_name}\n"
        f"Final Balance: {final_balance:,.2f}\n\n"
        f"Totals by Transaction Type:\n{totals_by_type.to_string()}\n\n"
        f"Total Income: {income:,.2f}\n"
        f"Total Expenditure: {expenditure:,.2f}\n\n"
        f"Largest Transaction: {largest_txn['amount']:,.6f}\n"
    )

    # Add summary to right side of chart
    plt.gcf().text(
        0.72, 0.5, summary_text,
        fontsize=20,
        va="center",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="black", boxstyle="round")
    )

    # Adjust so text box isn’t cut off
    plt.subplots_adjust(right=0.65)

    # Save as image
    plt.savefig("balance_summary.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("✅ Combined chart + summary saved as balance_summary.png")

     # Pie chart income vs expenditure
    plt.figure(figsize=(6, 6))
    plt.pie([income, expenditure], labels=["Income", "Expenditure"],
            autopct="%1.1f%%", colors=["#4CAF50", "#F44336"])
    plt.title("Income vs Expenditure")
    plt.savefig("income_expenditure_pie.png")
    plt.close()


def plot_running_balance(df, account_name, cutoff):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot running balance line
    ax.plot(df["timestamp"], df["running_balance"], marker="o", linestyle="-", color="blue")
    ax.set_title(f"Running Balance for {account_name} up to {cutoff} : ", fontsize=14)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Balance")

    # Get last point
    last_ts = df["timestamp"].iloc[-1]
    last_balance = df["running_balance"].iloc[-1]

    #dynamic color balance

    color = "green" if last_balance >= 0 else "red"

    # Annotate last point with its value
    ax.annotate(
        f"{last_balance:,.2f}", 
        (last_ts, last_balance),
        xytext=(35, 70), textcoords="offset points",  # shift label slightly to where i feel it stands out
        fontsize=25, color=color, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="gray")
    )

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("running_balance_chart.png", dpi=300)
    plt.close()

    print("✅ Running balance chart saved as running_balance_chart.png")
if __name__ == "__main__":
    analyze_transactions(
        csv_path="mock_transactions.csv",
        account_name="ZignalyX120",
        cutoff_timestamp="2025-01-30 08:42:00",
        upload_to_sheets=False 
    )
