from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd                
import matplotlib.pyplot as plt   
import os                        
from datetime import datetime      

# Create the Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"   # Used for flash messages (stores the message)
UPLOAD_FOLDER = 'transactions'      # Folder where CSV files are stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to analyze the selected CSV file
def analyze_csv(filepath):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(filepath)

        # Convert "Amount" column to numbers (if errors, make them NaN)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

        # Drop rows where Amount is missing
        df.dropna(subset=['Amount'], inplace=True)

        # Calculate totals
        total_income = df[df['Amount'] > 0]['Amount'].sum()   # all positive values
        total_expenses = df[df['Amount'] < 0]['Amount'].sum() # all negative values
        net_position = total_income + total_expenses          # balance (income - expenses)

        # Group spending by Category
        category_totals = df.groupby('Category')['Amount'].sum()

        # Create + save chart
        plt.clf()   # clear old plots
        category_totals.plot(kind='bar')   # bar chart
        plt.title("Spending by Category")
        plt.tight_layout()
        chart_path = os.path.join('static', 'chart.png')  # save inside static folder
        plt.savefig(chart_path)

        # Return all data in a dictionary
        return {
            'transactions': df.to_dict(orient='records'),  # each row as dictionary
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_position': net_position,
            'chart': chart_path
        }

    except Exception as e:
        # If something goes wrong, print error and return None
        print(f"Error: {e}")
        return None

# Route for homepage
@app.route('/')
def home():
    # Get list of all CSV files in the transactions folder
    csv_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.csv')]

    # Function to sort files by MONTH and YEAR (ignore day)
    def extract_month_year(filename):
        try:
            base = os.path.splitext(filename)[0]  # remove ".csv"
            dt = datetime.strptime(base, "%d-%m-%Y")  # turn string into date
            return (dt.year, dt.month)  # only return year + month
        except:
            return (0, 0)  # fallback if format is wrong

    # Sort files in correct order (earliest → latest)
    csv_files.sort(key=extract_month_year)

    # Show home.html with the list of files
    return render_template('home.html', csv_files=csv_files)

# Route for report page (when a CSV file is selected)
@app.route('/report', methods=['POST'])
def report():
    # Get the file selected by user
    selected_file = request.form.get('csv_file')

    # If no file chosen, show error
    if not selected_file:
        flash("Please select a CSV file.")
        return redirect(url_for('home'))

    # Full file path
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], selected_file)

    # Analyze the file
    data = analyze_csv(filepath)

    # If analysis failed, show error
    if data is None:
        flash("Failed to process file. Please check the format.")
        return redirect(url_for('home'))

    # Show report.html with results
    return render_template('report.html', file=selected_file, data=data)

if __name__ == '__main__':
    app.run(debug=True)
