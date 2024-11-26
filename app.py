from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load and preprocess the dataset
data = pd.read_csv('./csv/filtered_data.csv')  # Update file name if needed
data['Collision Date'] = pd.to_datetime(data['Collision Date'], errors='coerce')
data['Year Of Crash'] = pd.to_numeric(data['Year Of Crash'], errors='coerce')  # Ensure numeric type

# Home Page
@app.route('/')
def home():
    return render_template('about.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Data Page
@app.route('/data')
def data_page():
    counties = data['County'].dropna().unique()  # Get unique counties for dropdown
    return render_template('data.html', counties=counties)

# Distracted Driving Page
@app.route('/data/distracted-driving')
def distracted_driving():
    return render_template('distracted_driving.html')

# API route to get data filtered by county
@app.route('/api/crashes_by_year', methods=['GET'])
def crashes_by_year():
    county = request.args.get('county')  # Get county from the query string
    if county:
        filtered_data = data[data['County'] == county]
    else:
        filtered_data = data

    # Group data by 'Year of Crash' and count crashes
    crashes_by_year = (
        filtered_data.groupby('Year Of Crash')['Master_Record_Number']
        .count()
        .reset_index()
        .rename(columns={'Year Of Crash': 'year', 'Master_Record_Number': 'count'})
    )

    return jsonify(crashes_by_year.to_dict(orient='records'))


@app.route('/api/crashes_by_month', methods=['GET'])
def crashes_by_month():
    county = request.args.get('county')  # Get the county filter, if provided
    filtered_data = data[data['County'] == county] if county else data

    # Ensure Collision Date is datetime and extract month name
    filtered_data['Month'] = filtered_data['Collision Date'].dt.month_name()
    
    # Group data by month and count crashes
    crashes_by_month = (
        filtered_data.groupby('Month')['Master_Record_Number']
        .count()
        .reset_index()
        .rename(columns={'Month': 'month', 'Master_Record_Number': 'count'})
    )

    # Sort months in chronological order
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    crashes_by_month['month'] = pd.Categorical(crashes_by_month['month'], categories=month_order, ordered=True)
    crashes_by_month = crashes_by_month.sort_values('month')

    return jsonify(crashes_by_month.to_dict(orient='records'))


@app.route('/api/crashes_by_day', methods=['GET'])
def crashes_by_day():
    county = request.args.get('county')  # Get the county filter if provided
    filtered_data = data[data['County'] == county] if county else data

    # Ensure Collision Date is datetime and extract the day of the week
    print(filtered_data.head())  # Debugging: Check filtered data

    filtered_data['Day Name'] = filtered_data['Collision Date'].dt.day_name()

    # Group by day and count crashes
    crashes_by_day = (
        filtered_data.groupby('Day Name')['Master_Record_Number']
        .count()
        .reset_index()
        .rename(columns={'Day Name': 'day', 'Master_Record_Number': 'count'})
    )

    # Reorder days to start from Sunday
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    crashes_by_day['day'] = pd.Categorical(crashes_by_day['day'], categories=day_order, ordered=True)
    crashes_by_day = crashes_by_day.sort_values('day')

    print(crashes_by_day)  # Debugging: Check grouped data
    return jsonify(crashes_by_day.to_dict(orient='records'))


@app.route('/api/crashes_by_hour', methods=['GET'])
def crashes_by_hour():
    county = request.args.get('county')  # Get county filter if provided
    filtered_data = data[data['County'] == county] if county else data

    # Ensure Collision Date is in datetime format and extract the hour
    filtered_data['Hour'] = filtered_data['Collision Date'].dt.hour

    # Group data by hour and count crashes
    crashes_by_hour = (
        filtered_data.groupby('Hour')['Master_Record_Number']
        .count()
        .reset_index()
        .rename(columns={'Hour': 'hour', 'Master_Record_Number': 'count'})
    )

    return jsonify(crashes_by_hour.to_dict(orient='records'))


@app.route('/api/top_10_counties', methods=['GET'])
def top_10_counties():
    # Group by County and count the number of incidents
    top_counties = (
        data.groupby('County')['Master_Record_Number']
        .count()
        .reset_index()
        .rename(columns={'County': 'county', 'Master_Record_Number': 'count'})
        .sort_values('count', ascending=False)
        .head(10)
    )

    print(top_counties) 

    return jsonify(top_counties.to_dict(orient='records'))



if __name__ == '__main__':
    app.run(debug=True)