import io
import base64
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__, static_folder='static', template_folder='templates')  
CORS(app)

# load & clean data
DF = pd.read_csv('./data-to-visualize/Electric_Vehicle_Population_Data.csv')
DF = DF.dropna(subset=[
    'VIN (1-10)', 'Model Year', 'Make', 'Electric Range', 'Electric Vehicle Type'
])
DF['Model Year'] = DF['Model Year'].astype(int)
DF['Electric Range'] = DF['Electric Range'].astype(float)
DF['Base MSRP'] = pd.to_numeric(DF['Base MSRP'], errors='coerce').fillna(0)

# helper to convert fig to base64
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot')
def plot():
    p = request.args.get('type')

    # top 10 makes
    if p == 'make_counts':
        data = DF['Make'].value_counts().nlargest(10)
        fig, ax = plt.subplots()
        sns.barplot(x=data.values, y=data.index, ax=ax)
        ax.set_title('Top 10 EV Makes')

    # avg range by year
    elif p == 'avg_range':
        grp = DF.groupby('Model Year')['Electric Range'].mean().reset_index()
        fig, ax = plt.subplots()
        sns.lineplot(data=grp, x='Model Year', y='Electric Range', marker='o', ax=ax)
        ax.set_title('Average Electric Range by Year')

    # ev type distribution
    elif p == 'type_dist':
        dist = DF['Electric Vehicle Type'].value_counts()
        fig, ax = plt.subplots()
        dist.plot.pie(ax=ax, autopct='%1.1f%%')
        ax.set_title('EV Type Distribution')
        ax.set_ylabel('')

    # model year distribution
    elif p == 'year_dist':
        fig, ax = plt.subplots(figsize=(8,5))
        sns.countplot(data=DF, x='Model Year', ax=ax, palette='viridis')
        ax.set_title('Count of Vehicles by Model Year')
        plt.xticks(rotation=45)

    # range vs msrp
    elif p == 'range_vs_msrp':
        fig, ax = plt.subplots(figsize=(8,5))
        sns.regplot(data=DF, x='Electric Range', y='Base MSRP', scatter_kws={'alpha':0.4}, ax=ax)
        ax.set_title('Electric Range vs. Base MSRP')

    # top 10 cities by ev count
    elif p == 'top_cities':
        top = DF['City'].value_counts().nlargest(10)
        fig, ax = plt.subplots(figsize=(6,5))
        sns.barplot(x=top.values, y=top.index, ax=ax, palette='magma')
        ax.set_title('Top 10 Cities with Most EVs')

    # cafv eligibility breakdown
    elif p == 'cafv_breakdown':
        cafv = DF['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].value_counts()
        fig, ax = plt.subplots()
        cafv.plot.pie(ax=ax, autopct='%1.1f%%', startangle=140)
        ax.set_title('CAFV Eligibility')
        ax.set_ylabel('')

    # msrp distribution
    elif p == 'msrp_dist':
        fig, ax = plt.subplots(figsize=(6,5))
        sns.histplot(DF['Base MSRP'], bins=30, ax=ax)
        ax.set_title('Distribution of Base MSRP')

    # range by ev type boxplot
    elif p == 'range_type_box':
        fig, ax = plt.subplots(figsize=(8,5))
        sns.boxplot(data=DF, x='Electric Vehicle Type', y='Electric Range', ax=ax)
        ax.set_title('Electric Range by EV Type')
        plt.xticks(rotation=30)

    # bev vs phev trend over years
    elif p == 'bev_phev_trend':
        trend = DF.groupby(['Model Year','Electric Vehicle Type']).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(8,5))
        trend.plot(ax=ax, marker='o')
        ax.set_title('BEV vs. PHEV Counts Over Years')

    # range distribution for top 5 makes
    elif p == 'top5_range':
        top5 = DF['Make'].value_counts().nlargest(5).index
        fig, ax = plt.subplots(figsize=(8,5))
        sns.boxplot(data=DF[DF['Make'].isin(top5)], x='Make', y='Electric Range', ax=ax)
        ax.set_title('Range Distribution for Top 5 Makes')

    # top 10 legislative districts by count
    elif p == 'top10_districts':
        dist = DF['Legislative District'].value_counts().nlargest(10)
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(x=dist.values, y=dist.index.astype(str), ax=ax)
        ax.set_title('Top 10 Legislative Districts by EV Count')

    # correlation heatmap
    elif p == 'corr_heatmap':
        num = DF[['Model Year','Electric Range','Base MSRP']]
        corr = num.corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        ax.set_title('Correlation Matrix')

    else:
        return jsonify(error='Unknown plot type'), 400

    img = fig_to_base64(fig)
    return jsonify(img=img)

@app.route('/ev')
def ev_record():
    vin = request.args.get('vin')
    rec = DF[DF['VIN (1-10)'] == vin]
    if rec.empty:
        return jsonify(error='VIN not found'), 404
    return jsonify(record=rec.iloc[0].to_dict())

if __name__ == '__main__':
    app.run(debug=True)