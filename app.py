from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd                
import matplotlib.pyplot as plt   
import os                            

app = Flask(__name__)
app.secret_key = "supersecretkey"   # Used for flash messages (stores the message)
UPLOAD_FOLDER = 'transactions'      # Folder where CSV files are stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to analyze the selected CSV file
def analyze_csv(filepath):
    try:
        # Read the CSV file into a DataFrame (Using Pandas)
        df = pd.read_csv(filepath)

        # Converts "Amount" column to numbers
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

        # Drop rows where Amount is missing
        df.dropna(subset=['Amount'], inplace=True)

        # Calculate totals
        total_income = df[df['Amount'] > 0]['Amount'].sum()   
        total_expenses = df[df['Amount'] < 0]['Amount'].sum() 
        net_position = total_income + total_expenses

        # Group spending by Category
        category_totals = df.groupby('Category')['Amount'].sum()

        # Create and save chart
        plt.clf()   
        category_totals.plot(kind='bar') 
        plt.title("Spending by Category")
        plt.tight_layout()
        chart_path = os.path.join('static', 'chart.png') 
        plt.savefig(chart_path)

        # Return all data in a dictionary
        return {
            'transactions': df.to_dict(orient='records'), 
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_position': net_position,
            'chart': chart_path
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    # Get a list of all the CSV files in the transactions folder
    csv_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.csv')]
    return render_template('home.html', csv_files=csv_files)

@app.route('/report', methods=['POST'])
def report():
    # Get the file selected by the user
    selected_file = request.form.get('csv_file')

    # If no file is chosen, show error
    if not selected_file:
        flash("Please select a CSV file.")
        return redirect(url_for('home'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], selected_file)

    data = analyze_csv(filepath)
    if data is None:
        flash("Failed to process file. Please check the format.")
        return redirect(url_for('home'))

    return render_template('report.html', file=selected_file, data=data)

if __name__ == '__main__':
    app.run(debug=True)
