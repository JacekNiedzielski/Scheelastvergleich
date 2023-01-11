from flask import Flask, url_for, render_template, request, session
import json
import requests
import pandas as pd
import math


app = Flask(__name__)
app.config["SECRET_KEY"] = "SomethingWhatNo1CanGuess!"

df = pd.read_excel("Schneeregellasten.xlsx")
df.drop("Unnamed: 0", inplace=True, axis=1)

def shorten(element):
    element = element[:-2]
    return element

df.Stadt = df.Stadt.apply(shorten)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/show_snow_at_address", methods=["GET", "POST"])
def show_snow_at_address(old_snow=df):
    
    if request.method == "GET":
        return render_template("address.html")

    else:
        street = "Stephansplatz"
        if "street" in request.form:
            street = request.form["street"]

        house_number = "1"
        if "house_number" in request.form:
            house_number = request.form["house_number"]

        postal_code = "1010"
        if "postal_code" in request.form:
            postal_code = request.form["postal_code"]

        city = "Wien"
        if "city" in request.form:
            city = request.form["city"]

        address_string = street + " " + house_number + ", " + postal_code + " " + city

        params = {"address": address_string}
        
        r = requests.get("https://hora.gv.at/Services/Data", params)

        data = r.json()


        if city == "Wien" and postal_code == "1010":
            city = "Wien  1.,Innere Stadt"

        elif city == "Wien" and postal_code == "1020":
            city = "Wien  2.,Leopoldstadt"

        elif city == "Wien" and postal_code == "1030":
            city = "Wien  3.,Landstrasse"

        elif city == "Wien" and postal_code == "1040":
            city = "Wien  4.,Wieden" 

        elif city == "Wien" and postal_code == "1050":
            city = "Wien  5.,Margareten" 
        
        elif city == "Wien" and postal_code == "1060":
            city = "Wien  6.,Mariahilf" 
        
        elif city == "Wien" and postal_code == "1070":
            city = "Wien  7.,Neubau"

        elif city == "Wien" and postal_code == "1080":
            city = "Wien  8.,Josefstadt"

        elif city == "Wien" and postal_code == "1090":
            city = "Wien  9.,Alsergrund"

        elif city == "Wien" and postal_code == "1100":
            city = "Wien 10.,Favoriten"

        elif city == "Wien" and postal_code == "1110":
            city = "Wien 11.,Simmering"

        elif city == "Wien" and postal_code == "1120":
            city = "Wien 12.,Meidling"

        elif city == "Wien" and postal_code == "1130":
            city = "Wien 13.,Hietzing"

        elif city == "Wien" and postal_code == "1140":
            city = "Wien 14.,Penzing"    

        elif city == "Wien" and postal_code == "1150":
            city = "Wien 15.,Rudolfsheim-Fuenfhaus" 

        elif city == "Wien" and postal_code == "1160":
            city = "Wien 16.,Ottakring" 

        elif city == "Wien" and postal_code == "1170":
            city = "Wien 17.,Hernals"

        elif city == "Wien" and postal_code == "1180":
            city = "Wien 18.,Waehring"

        elif city == "Wien" and postal_code == "1190":
            city = "Wien 19.,Doebling"
        
        elif city == "Wien" and postal_code == "1200":
            city = "Wien 20.,Brigittenau"

        elif city == "Wien" and postal_code == "1210":
            city = "Wien 21.,Floridsdorf"           

        elif city == "Wien" and postal_code == "1220":
            city = "Wien 22.,Donaustadt"

        elif city == "Wien" and postal_code == "1230":
            city = "Wien 23.,Liesing"

        else:
            city = city

        schneelast = round(float(data["data"]["schneelast"]),3)
        print(schneelast)
        #print(city)
        #print(old_snow.tail())
        index = old_snow.loc[old_snow.Stadt == city]["Schneeregellast"].index[0]
        schnee_alt = old_snow.loc[old_snow.Stadt == city]["Schneeregellast"][index]
        #print(schnee_alt)

        roof_type = "Pultdach"
        if "roof_type" in request.form:
            roof_type = request.form["roof_type"]

        
        session["roof_type"] = roof_type
        session["schnee_alt"] = schnee_alt
        session["schneelast"] = schneelast
        session["address"] = address_string
        
        if roof_type == 'Satteldach':
            return render_template("snow_and_Satteldach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt, roof_type=roof_type+'.png')

        if roof_type == 'Pultdach':
            return render_template("snow_and_Pultdach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt, roof_type=roof_type+'.png')



@app.route("/show_snow_on_roof_pultdach", methods=["POST"])
def show_snow_on_roof_pultdach():

    schnee_alt = session["schnee_alt"]
    schneelast = session["schneelast"]
    roof_type = session["roof_type"]
    address_string = session["address"]

    if request.method == "POST":
        roof_angle_pultdach = 0
        if "roof_angle_pultdach" in request.form:
            roof_angle_pultdach = request.form["roof_angle_pultdach"]
    
    if int(roof_angle_pultdach) >= 0 and int(roof_angle_pultdach) < 30:
        µ_1_neu = 0.8
        µ_1_alt = 1.0 

    elif int(roof_angle_pultdach) >= 30 and int (roof_angle_pultdach) < 60:
        µ_1_neu = 0.8 * (60 - int(roof_angle_pultdach)) / 30
        µ_1_alt = 1.0 * (60 - int(roof_angle_pultdach)) / 30

    elif int(roof_angle_pultdach) >= 60:
        µ_1_neu = 0
        µ_1_alt = 0

    roof_schnee_alt = round(schnee_alt*µ_1_alt,3)
    roof_schnee_neu = round(schneelast*µ_1_neu,3)

    return render_template("results_pultdach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt,
    roof_angle_pultdach=roof_angle_pultdach, roof_schnee_alt=roof_schnee_alt, roof_schnee_neu=roof_schnee_neu, roof_type=roof_type+'.png')





@app.route("/show_snow_on_roof_satteldach", methods=["POST"])
def show_snow_on_roof_satteldach():

    schnee_alt = session["schnee_alt"]
    schneelast = session["schneelast"]
    roof_type = session["roof_type"]
    address_string = session["address"]

    if request.method == "POST":
        roof_angle_satteldach_1 = 0
        if "roof_angle_satteldach_1" in request.form:
            roof_angle_satteldach_1 = request.form["roof_angle_satteldach_1"]

        roof_angle_satteldach_2 = 0
        if "roof_angle_satteldach_2" in request.form:
            roof_angle_satteldach_2 = request.form["roof_angle_satteldach_2"]

    
    if int(roof_angle_satteldach_1) >= 0 and int(roof_angle_satteldach_1) < 15:
        µ_2_neu_1 = 0.8
        µ_2_alt_1 = 1.0

    elif int(roof_angle_satteldach_1) >= 15 and int(roof_angle_satteldach_1) < 30:
        µ_2_neu_1 = 0.8 + 0.2 * (int(roof_angle_satteldach_1) - 15) / 15
        µ_2_alt_1 = 1.0

    elif int(roof_angle_satteldach_1) >= 30 and int(roof_angle_satteldach_1) < 60:
        µ_2_neu_1 = 1.0 * (60 - int(roof_angle_satteldach_1)) / 30
        µ_2_alt_1 = 1.0 * (60 - int(roof_angle_satteldach_1)) / 30

    elif int(roof_angle_satteldach_1) >= 60:
        µ_2_neu_1 = 0
        µ_2_alt_1 = 0



    if int(roof_angle_satteldach_2) >= 0 and int(roof_angle_satteldach_2) < 15:
        µ_2_neu_2 = 0.8
        µ_2_alt_2 = 1.0

    elif int(roof_angle_satteldach_2) >= 15 and int(roof_angle_satteldach_2) < 30:
        µ_2_neu_2 = 0.8 + 0.2 * (int(roof_angle_satteldach_2) - 15) / 15
        µ_2_alt_2 = 1.0

    elif int(roof_angle_satteldach_2) >= 30 and int(roof_angle_satteldach_2) < 60:
        µ_2_neu_2 = 1.0 * (60 - int(roof_angle_satteldach_2)) / 30
        µ_2_alt_2 = 1.0 * (60 - int(roof_angle_satteldach_2)) / 30

    elif int(roof_angle_satteldach_2) >= 60:
        µ_2_neu_2 = 0
        µ_2_alt_2 = 0


    roof_schnee_alt_1 = round(schnee_alt*µ_2_alt_1,3)
    roof_schnee_neu_1 = round(schneelast*µ_2_neu_1,3)

    roof_schnee_alt_2 = round(schnee_alt*µ_2_alt_2,3)
    roof_schnee_neu_2 = round(schneelast*µ_2_neu_2,3)

    return render_template("results_satteldach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt,
    roof_angle_satteldach_1=roof_angle_satteldach_1, roof_angle_satteldach_2=roof_angle_satteldach_2, 
    roof_schnee_alt_1=roof_schnee_alt_1, roof_schnee_neu_1=roof_schnee_neu_1, 
    roof_schnee_alt_2=roof_schnee_alt_2, roof_schnee_neu_2=roof_schnee_neu_2,
    roof_type=roof_type+'.png')