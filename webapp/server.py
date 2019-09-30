#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:25:23 2019

@author: chengchen
"""

from flask import Flask, render_template, request
import pandas as pd
import numpy as np




# Create the application object
app = Flask(__name__)
# run server:app in terminal
@app.route('/',methods=["GET","POST"])


def home_page():   
	return render_template('index.html')

@app.route('/output', methods = ["GET", "POST"])
def tag_output():
  # Pull Input
  EVPR = float(request.form.get('slider1'))
  HCR = float(request.form.get('slider2'))
  # read results
  list_demand_ratio = np.linspace(0.00118, 0.038, num=30).tolist()
  demand_ratio_input =  EVPR*(0.1*1+0.9*(1-HCR)/5)
  list_index = int(np.round((demand_ratio_input-0.00118)/((0.038-0.00118)/29)))
  demand_ratio = list_demand_ratio[list_index]
  map_folder = '../static/maps'
  map_html = map_folder + '/TRT_map_demand_ratio_'+str(demand_ratio)[2:]+'.html'  
  data_folder = './data/processed'
  df_opt_chg_lc = pd.read_excel(data_folder +'/chg_stn_location_cluster_demand_ratio'+str(demand_ratio)[2:]+'.xlsx')
  df_opt_chg_lc = df_opt_chg_lc[['Name','Url','latitude','longitude']]
  


  return render_template("index.html",
                      my_input1=EVPR,
                      my_input2=HCR,
                      tables=[df_opt_chg_lc.to_html(classes='table table-bordered table-hover" id = "a_nice_table',
                                       index=False, border=0)],
                      map_html=map_html
                      )
  #return render_template(map_file_name)

# start the server with the 'run()' method
if __name__ == "__main__":
	app.run(host = "0.0.0.0", debug=True) 
  #app.run(debug=True) #will run locally http://127.0.0.1:5000/
