# Zignaly Transaction Analysis

This project is a solution to the **Technical Assessment – Support/Data Ops** for Zignaly.  
The goal was to build a script that can analyze transaction data for a given account up to a specific cutoff timestamp, calculate balances, and present the results in a way that is both **useful and easy to understand**.

---

## 🧠 Reasoning Behind the Solution

When approaching this assessment, the main goal was to design a script that could process a CSV file of mock transactions, filter them by account and cutoff timestamp, and then generate both numeric summaries and a running balance visualization gave seriouse consideration to using Google cloud api for automatic upload to googlesheets but it seemed a little unncessary additionally i might forget to remove my payment details and i do not want to get charged for a service i barely use 😂.

We started by focusing on **data clarity and reproducibility**:

1. **Filtering by account & cutoff timestamp**

   - Transactions are filtered based on the provided account name and cutoff timestamp.
   - This ensures the script only considers relevant records, which is important for scalability when handling large datasets.

2. **Running Balance Computation**

   - Instead of just looking at “effect” (income/expenditure), we created a dedicated **running balance column** that accumulates the balance over time.
   - This gives a more accurate representation of account health.

3. **Summaries**

   - The script calculates:
     - Final balance
     - Total income vs. expenditure
     - Totals by transaction type
     - Largest transaction
     - Most frequent transaction type
   - These insights make the dataset more actionable rather than just raw numbers.

4. **Visualization**

   - A running balance line chart was added with a dynamic label at the latest point to show the current balance.
   - The label color is **green if the final balance is positive**, and **red if it is negative**, giving instant visual feedback.

5. **Export Options**
   - The results are written to an Excel sheet for further analysis.
   - Additionally, we added an option to embed the summaries into an image so they can be shared or reported easily.

This solution balances **functionality, readability, and extendability** so it can evolve if more requirements are introduced later.

---

## 🚀 Features

- Filter transactions up to any cutoff timestamp.
- Focus on a single account’s activity.
- Running balance tracking over time.
- Totals by transaction type.
- Income vs. expenditure calculation.
- Largest transaction and most frequent transaction type detection.
- Charts:
  - Bar chart of totals by type.
  - Line chart of running balance with the final value annotated (green if positive, red if negative).
  - Combined chart + text summary image.
- Export to Excel for structured review.
- Optional integration with Google Sheets for live sharing.

---

## ⚙️ How to Run

1. **Clone the repository**

   ```bash
   git clone https://github.com/jupiterBill/Zignaly-Transaction.git
   cd Zignaly-Transaction
   ```

2. **Setup Virtual Environment (Optional but Recommended)**
   ```python -m venv zigenv
   source zigenv/bin/activate   # On Linux/Mac
   zigenv\Scripts\activate
   ```
3. **Install Dependencies**

```
pip install -r requirements.txt

```

4. **Run the script**

```
py Zignaly_assessment.py
```
