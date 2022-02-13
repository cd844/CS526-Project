from flask import Flask, flash, redirect, render_template, request, session, abort, request, url_for, jsonify,request
import ast
import pandas as pd
import json
import plotly
import plotly.express as px
import datetime
import keras
from keras.models import model_from_json
import numpy as np
import pandas as pd
import sqlite3

# con = sqlite3.connect('repo.db')
# cur = con.cursor()
# for row in cur.execute('select * from repo.db limit 10'):
#     print(row)
app = Flask(__name__)

#We have used Bootstrap CSS and Colorlib CSS in our site (Creative Commons License)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timeline/')
def timeline():
    return render_template('timeline.html')

@app.route('/predict/')
def predict():
    return render_template('predict.html')

@app.route('/predict/', methods=['POST'])
def my_form_post():
    brand = request.form['Brand']
    price = request.form['Price']
    weekday = request.form['Weekday']
    cat1 = request.form['Cat1']
    cat2 = request.form['Cat2']
    actcount = request.form['ActCount']

    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model.h5")
    my_array = np.array([[int(brand),int(price),int(weekday),int(cat1),int(cat2),int(actcount)]])
    newdf = pd.DataFrame(my_array, columns = ['brand', 'price', 'event_weekday', 'category_code_level1', 'category_code_level2', 'activity_count'])
    z=loaded_model.predict(newdf)

    prob = ""

    if z>0.15:
        prob =  "There is a high probability that the product will be bought "
    else:
        prob =  "There are very less chances of buying this product"

    return render_template('predict.html', prob = prob)

@app.route('/graphs/')
def graphs():
    labels = ['Sun','Mon','Thu','Sat','Wed','Fri','Tue']
    size = [183486,73543,68373,120430,69027,76320,68077]
    fig = px.pie(names= labels, values=size, title='Items Bought Per Day of Week')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    labels = ['samsung', 'apple', 'xiaomi', 'huawei', 'oppo', 'lg', 'artel', 'lenovo', 'acer', 'bosch', 'indesit', 'respect', 'hp', 'midea', 'elenberg', 'haier', 'beko', 'casio', 'tefal', 'vitek']
    size = [198670, 165681, 57909, 23466, 15080, 11828, 7269, 6546, 6402, 5718, 5187, 4557, 4002, 3984, 3944, 3826, 3813, 3477, 3343, 3095]
    fig2 = px.pie(names= labels, values=size, title='Sales Per Brand')
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    labels = ['apple', 'samsung', 'xiaomi', 'lg', 'huawei', 'oppo', 'acer', 'lenovo', 'asus', 'hp', 'artel', 'indesit', 'bosch', 'haier', 'sony', 'beko', 'midea', 'vivo', 'philips', 'janome']
    lol = [[21.239999771118164, 5.610000133514404, 4.090000152587891, 69.47000122070312, 4.889999866485596, 128.4499969482422, 12.069999694824219, 5.639999866485596, 14.050000190734863, 7.699999809265137, 17.860000610351562, 16.190000534057617, 35.779998779296875, 38.59000015258789, 5.119999885559082, 100.30999755859375, 14.130000114440918, 102.94000244140625, 5.119999885559082, 98.54000091552734], [2574.0400390625, 2574.0400390625, 2033.510009765625, 2574.0400390625, 965.02001953125, 900.9000244140625, 2574.0400390625, 1956.27001953125, 2570.179931640625, 2493.02001953125, 1714.0699462890625, 595.0999755859375, 1490.0899658203125, 1801.8199462890625, 2574.0400390625, 1704.9000244140625, 1456.6700439453125, 797.9400024414062, 1698.81005859375, 1741.239990234375]]
    fig3 = px.line(x=labels, y= lol, title = 'Min Max Sale Per Company')
    newnames = {'wide_variable_0':'Min', 'wide_variable_1': 'Max'}
    fig3.for_each_trace(lambda t: t.update(name = newnames[t.name], legendgroup = newnames[t.name], hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    labels = [datetime.date(2019, 11, 1), datetime.date(2019, 11, 2), datetime.date(2019, 11, 3), datetime.date(2019, 11, 4), datetime.date(2019, 11, 5), datetime.date(2019, 11, 6), datetime.date(2019, 11, 7), datetime.date(2019, 11, 8), datetime.date(2019, 11, 9), datetime.date(2019, 11, 10), datetime.date(2019, 11, 11), datetime.date(2019, 11, 12), datetime.date(2019, 11, 13), datetime.date(2019, 11, 14), datetime.date(2019, 11, 15), datetime.date(2019, 11, 16), datetime.date(2019, 11, 17), datetime.date(2019, 11, 18), datetime.date(2019, 11, 19), datetime.date(2019, 11, 20), datetime.date(2019, 11, 21), datetime.date(2019, 11, 22), datetime.date(2019, 11, 23), datetime.date(2019, 11, 24), datetime.date(2019, 11, 25), datetime.date(2019, 11, 26), datetime.date(2019, 11, 27), datetime.date(2019, 11, 28), datetime.date(2019, 11, 29), datetime.date(2019, 11, 30)]
    size = [897686, 960658, 982167, 1101573, 1031735, 1022542, 1080119, 1177376, 1164872, 1204700, 1240183, 1235321, 1272006, 2013458, 3967561, 4096051, 4014812, 1245708, 1055544, 1022601, 992410, 960682, 978947, 993865, 962813, 1009183, 1015975, 1045067, 1219321, 1124634]
    fig4 = px.line(x= labels, y=size, title='Sales by Date')
    graphJSON4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)

    labels = ['view', 'cart','purchase']
    size = [39315226, 2115088, 659256]
    fig5 = px.pie(names= labels, values=size, title='Customer Activity')
    fig5.update_traces(textposition='outside', textinfo='percent+label')
    graphJSON5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)

    labels = ['apple', 'samsung', 'xiaomi', 'lg', 'huawei', 'oppo', 'acer', 'lenovo', 'asus', 'hp', 'artel', 'indesit', 'bosch', 'haier', 'sony', 'beko', 'midea', 'vivo', 'philips', 'janome']
    size = [127490496, 54790697, 10874049, 5029641, 4768995, 3488540, 3347306, 2698104, 1661714, 1331632, 1329815, 1306939, 1276557, 1101421, 1053351, 881037, 623492, 516173, 477813, 423589]
    fig6 = px.line(x= labels, y=size, title='Brands with Most Revenue')
    graphJSON6 = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)

    with open('test.txt', 'r') as f:
        labels = json.load(f)
    with open('test2.txt', 'r') as f:
        size = json.load(f)
    print(labels[:5])
    print(size[:5])
    fig8 = px.scatter(x=labels, y=size)
    graphJSON8 = json.dumps(fig8, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graphs.html', graphJSON = graphJSON, graphJSON2 = graphJSON2, graphJSON3 = graphJSON3, graphJSON4 = graphJSON4, graphJSON5 = graphJSON5, graphJSON6 = graphJSON6, graphJSON8 = graphJSON8)

if __name__ == "__main__":
    app.run(debug=True)