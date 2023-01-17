from flask import Flask, url_for, render_template, request, session, redirect
import json
import requests
import pandas as pd
import math
import datetime
import os

template_dir = os.path.abspath("Templates")

app = Flask(__name__, template_folder=template_dir)
app.config["SECRET_KEY"] = "SomethingWhatNo1CanGuess!"

df = pd.read_excel("Schneeregellasten.xlsx")
df.drop("Unnamed: 0", inplace=True, axis=1)


df_4000 = pd.read_excel("Schneeregellasten_4000.xlsx")
df_4000.drop("Unnamed: 0", inplace=True, axis=1)



def shorten(element):
    element = element[:-2]
    return element

df.Stadt = df.Stadt.apply(shorten)

cities_4013_EC = df.Stadt.sort_values().to_list()
cities_4000 = df_4000.Stadt.sort_values().to_list()



today = datetime.date.today()
current_year = today.year

years = []

for year in range(1960,current_year+1):
    years.append(year)



@app.route("/")
def index():
    return render_template("index.html", active_menu="Home")



@app.route("/show_snow_at_nearest_city", methods=["GET", "POST"])
def show_snow_at_nearest_city():
    if request.method == "POST":
        if "nearest_city" in request.form:
            nearest_city = request.form["nearest_city"]
            return render_template("address.html", nearest_city=nearest_city, current_year = current_year, years = years, active_menu="Eingabe von Daten")


@app.route("/show_snow_at_address", methods=["GET", "POST"])
def show_snow_at_address(old_snow=df, old_snow_4000 = df_4000):
    
    if request.method == "GET":
        return render_template("address.html", current_year = current_year, years = years, active_menu="Eingabe von Daten")

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
        print(address_string)
        r = requests.get("https://hora.gv.at/Services/Data", params)

        data = r.json()
        schneelast = round(float(data["data"]["schneelast"]),3)
        #print(schneelast)
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

        
        einrichtungsjahr = current_year
        if "einrichtungsjahr" in request.form:
            einrichtungsjahr = request.form["einrichtungsjahr"]
            einrichtungsjahr = int(einrichtungsjahr)


        
        if einrichtungsjahr >= 1984 and city in old_snow.Stadt.to_list():
            #Schneezone gemäß ÖNORM B 4013
            schneezone_4013 = old_snow.loc[old_snow.Stadt == city]["Schneezone_4013"][old_snow.loc[old_snow.Stadt == city]["Schneezone_4013"].index[0]]
            #Schneezone gemäß EC 2006
            schneezone_EC2006 = old_snow.loc[old_snow.Stadt == city]["Schneezone_EC2006"][old_snow.loc[old_snow.Stadt == city]["Schneezone_EC2006"].index[0]]
        
        elif einrichtungsjahr < 1984 and city in old_snow_4000.Stadt.tolist():
       
            schneeregellast_4000 = old_snow_4000["Schneeregellast"][old_snow_4000.loc[old_snow_4000.Stadt == city].index[0]]

        elif einrichtungsjahr < 1984 and city not in old_snow_4000.Stadt.tolist():
            return render_template("city_not_found.html", cities = cities_4000)
        
        else:
            return render_template("city_not_found.html", cities = cities_4013_EC)


    

        seehoehe = "Seehoehe von Stadt"

        if "seehoehe" in request.form:
            seehoehe = request.form["seehoehe"]
            
            if seehoehe == "Seehoehe von Stadt" and einrichtungsjahr >= 1984:
                #Schneeregellast gemäß ÖNORM B 4013 und EC 2006 ohne explizite Eingabe von Seehöhe (Wert für Stadt)
                schneeregellast_4013 = old_snow.loc[old_snow.Stadt == city]["Schneeregellast_4013"][old_snow.loc[old_snow.Stadt == city]["Schneeregellast_4013"].index[0]]
                schneeregellast_EC2006 = old_snow.loc[old_snow.Stadt == city]["Schneeregellast_EC2006"][old_snow.loc[old_snow.Stadt == city]["Schneeregellast_EC2006"].index[0]]

            elif seehoehe != "Seehoehe von Stadt" and einrichtungsjahr >=1984:
                seehoehe = int(seehoehe)

                if schneezone_4013 == "A" and seehoehe >= 200:
                    schneeregellast_4013 = 0.71 - 0.30*seehoehe/1000 + 2.58*(seehoehe/1000)**2
        
                elif schneezone_4013 == "A" and seehoehe < 200:
                    schneeregellast_4013 = 0.75
                
                elif schneezone_4013 == "B" and seehoehe >= 300:
                    schneeregellast_4013 = 1.75 - 1.85*seehoehe/1000 + 3.75*(seehoehe/1000)**2
        
                elif schneezone_4013 == "B" and seehoehe < 300:
                    schneeregellast_4013 = 1.55
        
                elif schneezone_4013 == "C":
                    schneeregellast_4013 = 2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2
        
                elif schneezone_4013 == "C*" and seehoehe <= 700:
                    schneeregellast_4013 = max(2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2, 3.8)

                elif schneezone_4013 == "C*" and seehoehe > 700:
                    schneeregellast_4013 = (2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2)*1.2
    
                elif schneezone_4013 == "D":
                    schneeregellast_4013 = min(1.25 - 2.20*seehoehe/1000 + 3.04*(seehoehe/1000)**2, 4.5)
        
                elif schneezone_4013 == "A/B" and seehoehe < 200:
                    schneeregellast_4013 = (0.75+1.55)/2
            
                elif schneezone_4013 == "A/B" and seehoehe >= 200 and seehoehe < 300:
                    schneeregellast_4013 = ( (0.71 - 0.30*seehoehe/1000 + 2.58*(seehoehe/1000)**2) + 1.55 ) / 2
        
                elif schneezone_4013 == "A/B" and seehoehe >= 300:
                    schneeregellast_4013 = ( (0.71 - 0.30*seehoehe/1000 + 2.58*(seehoehe/1000)**2) 
                                + (1.75 - 1.85*seehoehe/1000 + 3.75*(seehoehe/1000)**2) ) / 2
            
                elif schneezone_4013 == "B/C" and seehoehe < 300: 
                    schneeregellast_4013 = ( 1.55 + (2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2) ) / 2
                    
                elif schneezone_4013 == "B/C" and seehoehe >= 300:
                    schneeregellast_4013 = ( (1.75 - 1.85*seehoehe/1000 + 3.75*(seehoehe/1000)**2) 
                                + (2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2) ) / 2
        
                elif schneezone_4013 == "C/C*" and seehoehe <= 700: 
                    schneeregellast_4013 = ( (2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2)
                                + (max(2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2, 3.8)) ) / 2
            
                elif schneezone_4013 == "C/C*" and seehoehe > 700:
                    schneeregellast_4013 = ( (2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2)
                                + ((2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2)*1.2) ) / 2
        
                elif schneezone_4013 =="B/C*" and seehoehe < 300:
                    schneeregellast_4013 = (1.55 + max(2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2, 3.8)) / 2
            
                elif schneezone_4013 =="B/C*" and seehoehe >= 300 and seehoehe <= 700:
                    schneeregellast_4013 = ( (1.75 - 1.85*seehoehe/1000 + 3.75*(seehoehe/1000)**2)
                                + (max(2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2, 3.8))) / 2
        
                elif schneezone_4013 =="B/C*" and seehoehe > 700:
                    schneeregellast_4013 = ( (1.75 - 1.85*seehoehe/1000 + 3.75*(seehoehe/1000)**2)
                                + ((2.27 - 2.26*seehoehe/1000 + 4.92*(seehoehe/1000)**2)*1.2) ) / 2
        
                elif schneezone_4013 =="A/D" and seehoehe < 200: 
                    schneeregellast_4013 = ( 0.75 + min(1.25 - 2.20*seehoehe/1000 + 3.04*(seehoehe/1000)**2, 4.5)) / 2

                elif schneezone_4013 =="A/D" and seehoehe >= 200:
                    schneeregellast_4013 = ( (0.71 - 0.30*seehoehe/1000 + 2.58*(seehoehe/1000)**2)  
                                + min(1.25 - 2.20*seehoehe/1000 + 3.04*(seehoehe/1000)**2, 4.5)) / 2

                #########################################################################################################
                
                if schneezone_EC2006 == "2*":
                    schneeregellast_EC2006 = max( (0.642 * 1.6 + 0.009) * (1 + (seehoehe / 728) ** 2), 1.0)
                
                elif schneezone_EC2006 == "2*/2":
                    schneeregellast_EC2006 = max( (0.642 * 1.8 + 0.009) * (1 + (seehoehe / 728) ** 2), 1.15)

                elif schneezone_EC2006 == "2":
                    schneeregellast_EC2006 = max( (0.642 * 2 + 0.009) * (1 + (seehoehe / 728) ** 2), 1.3)

                elif schneezone_EC2006 == "2/3":
                    schneeregellast_EC2006 = max( (0.642 * 2.5 + 0.009) * (1 + (seehoehe / 728) ** 2), 1.6)

                elif schneezone_EC2006 == "3":
                    schneeregellast_EC2006 = max( (0.642 * 3 + 0.009) * (1 + (seehoehe / 728) ** 2), 1.9)

                elif schneezone_EC2006 == "3/4":
                    schneeregellast_EC2006 = max( (0.642 * 3.75 + 0.009) * (1 + (seehoehe / 728) ** 2), 2.4)

                elif schneezone_EC2006 == "4":
                    schneeregellast_EC2006 = max( (0.642 * 4.5 + 0.009) * (1 + (seehoehe / 728) ** 2), 2.9)


        
        if einrichtungsjahr < 1984 and einrichtungsjahr >=1960:
            schnee_alt = schneeregellast_4000
            norm = "ÖNORM B 4000" 
        
        
        elif einrichtungsjahr >= 1984 and einrichtungsjahr <= 2005:
            schnee_alt = schneeregellast_4013
            norm = "ÖNORM B 4013"
        
        elif einrichtungsjahr >= 2006 and  einrichtungsjahr < 2022:
            schnee_alt = schneeregellast_EC2006
            norm = "EN 1991-1-3 2006"

        elif einrichtungsjahr >= 2022:
            return render_template("no_pv_potential.html")

        roof_type = "Pultdach"
        if "roof_type" in request.form:
            roof_type = request.form["roof_type"]

        
        session["roof_type"] = roof_type
        session["schnee_alt"] = schnee_alt
        session["schneelast"] = schneelast
        session["address"] = address_string
        session["norm"] = norm
        
        if roof_type == 'Satteldach':
            return render_template("snow_and_Satteldach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt, roof_type=roof_type+'.png', norm=norm)

        if roof_type == 'Pultdach':
            return render_template("snow_and_Pultdach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt, roof_type=roof_type+'.png', norm=norm)



@app.route("/show_snow_on_roof_pultdach", methods=["POST"])
def show_snow_on_roof_pultdach():

    schnee_alt = session["schnee_alt"]
    schneelast = session["schneelast"]
    roof_type = session["roof_type"]
    address_string = session["address"]
    norm = session["norm"]

    if request.method == "POST":
        roof_angle_pultdach = 0
        if "roof_angle_pultdach" in request.form:
            roof_angle_pultdach = request.form["roof_angle_pultdach"]
    
    if int(roof_angle_pultdach) >=0 and int(roof_angle_pultdach) < 30 and norm == "ÖNORM B 4000":
        µ_1_neu = 0.8
        µ_1_alt = 1.0
    
    elif int(roof_angle_pultdach) >=30 and int(roof_angle_pultdach) < 60 and norm == "ÖNORM B 4000":
        µ_1_neu = 0.8 * (60 - int(roof_angle_pultdach)) / 30
        µ_1_alt = 1.0 * (70 - int(roof_angle_pultdach)) / 40

    elif int(roof_angle_pultdach) >= 60 and int(roof_angle_pultdach) < 70 and norm == "ÖNORM B 4000":
        µ_1_neu = 0
        µ_1_alt = 1.0 * (70 - int(roof_angle_pultdach)) / 40

    elif int(roof_angle_pultdach) >= 70 and norm == "ÖNORM B 4000":
        µ_1_neu = 0
        µ_1_alt = 0    



    elif int(roof_angle_pultdach) >= 0 and int(roof_angle_pultdach) < 30 and norm == "ÖNORM B 4013":
        µ_1_neu = 0.8
        µ_1_alt = 1.0 

    elif int(roof_angle_pultdach) >= 30 and int(roof_angle_pultdach) < 60 and norm == "ÖNORM B 4013":
        µ_1_neu = 0.8 * (60 - int(roof_angle_pultdach)) / 30
        µ_1_alt = 1.0 * (60 - int(roof_angle_pultdach)) / 30



    elif int(roof_angle_pultdach) >= 0 and int(roof_angle_pultdach) < 30 and norm == "EN 1991-1-3 2006":
        µ_1_neu = 0.8
        µ_1_alt = 0.8        

    elif int(roof_angle_pultdach) >= 30 and int(roof_angle_pultdach) < 60 and norm == "EN 1991-1-3 2006":
        µ_1_neu = 0.8 * (60 - int(roof_angle_pultdach)) / 30
        µ_1_alt = 0.8 * (60 - int(roof_angle_pultdach)) / 30

    
    
    elif int(roof_angle_pultdach) >= 60 and norm != "ÖNORM B 4000":
        µ_1_neu = 0
        µ_1_alt = 0

    roof_schnee_alt = round(schnee_alt*µ_1_alt,3)
    roof_schnee_neu = round(schneelast*µ_1_neu,3)

    return render_template("results_pultdach.html", schneelast=schneelast, address = address_string, schnee_alt=schnee_alt,
    roof_angle_pultdach=roof_angle_pultdach, roof_schnee_alt=roof_schnee_alt, roof_schnee_neu=roof_schnee_neu, roof_type=roof_type+'.png', norm=norm)



@app.route("/show_snow_on_roof_satteldach", methods=["POST"])
def show_snow_on_roof_satteldach():

    schnee_alt = session["schnee_alt"]
    schneelast = session["schneelast"]
    roof_type = session["roof_type"]
    address_string = session["address"]
    norm = session["norm"]

    if request.method == "POST":
        roof_angle_satteldach_1 = 0
        if "roof_angle_satteldach_1" in request.form:
            roof_angle_satteldach_1 = request.form["roof_angle_satteldach_1"]

        roof_angle_satteldach_2 = 0
        if "roof_angle_satteldach_2" in request.form:
            roof_angle_satteldach_2 = request.form["roof_angle_satteldach_2"]

    #First roof part
    
    if int(roof_angle_satteldach_1) >= 0 and int(roof_angle_satteldach_1) < 15 and norm == "ÖNORM B 4000":
        µ_2_neu_1 = 0.8
        µ_2_alt_1 = 1.0
    
    elif int(roof_angle_satteldach_1) >= 15 and int(roof_angle_satteldach_1) < 30 and norm == "ÖNORM B 4000":
        µ_2_neu_1 = 0.8 + 0.2 * (int(roof_angle_satteldach_1) - 15) / 15
        µ_2_alt_1 = 1.0

    elif int(roof_angle_satteldach_1) >= 30 and int(roof_angle_satteldach_1) < 60 and norm == "ÖNORM B 4000":
        µ_2_neu_1 = 1.0 * (60 - int(roof_angle_satteldach_1)) / 30
        µ_2_alt_1 = 1.0 * (70 - int(roof_angle_satteldach_1)) / 40
    
    elif int(roof_angle_satteldach_1) >= 60 and int(roof_angle_satteldach_1) < 70 and norm == "ÖNORM B 4000":
        µ_2_neu_1 = 0
        µ_2_alt_1 = 1.0 * (70 - int(roof_angle_satteldach_1)) / 40

    elif int(roof_angle_satteldach_1) >= 70 and norm == "ÖNORM B 4000":
        µ_2_neu_1 = 0
        µ_2_alt_1 = 0
  
    
    elif int(roof_angle_satteldach_1) >= 0 and int(roof_angle_satteldach_1) < 15 and norm == "ÖNORM B 4013":
        µ_2_neu_1 = 0.8
        µ_2_alt_1 = 1.0

    elif int(roof_angle_satteldach_1) >= 15 and int(roof_angle_satteldach_1) < 30 and norm == "ÖNORM B 4013":
        µ_2_neu_1 = 0.8 + 0.2 * (int(roof_angle_satteldach_1) - 15) / 15
        µ_2_alt_1 = 1.0

    elif int(roof_angle_satteldach_1) >= 30 and int(roof_angle_satteldach_1) < 60 and norm == "ÖNORM B 4013":
        µ_2_neu_1 = 1.0 * (60 - int(roof_angle_satteldach_1)) / 30
        µ_2_alt_1 = 1.0 * (60 - int(roof_angle_satteldach_1)) / 30


    elif int(roof_angle_satteldach_1) >= 0 and int(roof_angle_satteldach_1) < 15 and norm == "EN 1991-1-3 2006":
        µ_2_neu_1 = 0.8
        µ_2_alt_1 = 0.8    

    elif int(roof_angle_satteldach_1) >= 15 and int(roof_angle_satteldach_1) < 30 and norm == "EN 1991-1-3 2006":
        µ_2_neu_1 = 0.8 + 0.2 * (int(roof_angle_satteldach_1) - 15) / 15
        µ_2_alt_1 = 0.8 
    
    elif int(roof_angle_satteldach_1) >= 30 and int(roof_angle_satteldach_1) < 60 and norm == "EN 1991-1-3 2006":
        µ_2_neu_1 = 1.0 * (60 - int(roof_angle_satteldach_1)) / 30
        µ_2_alt_1 = 0.8 * (60 - int(roof_angle_satteldach_1)) / 30
    
    elif int(roof_angle_satteldach_1) >= 60 and norm != "ÖNORM B 4000":
        µ_2_neu_1 = 0
        µ_2_alt_1 = 0


    ## Second roof part

    if int(roof_angle_satteldach_2) >= 0 and int(roof_angle_satteldach_2) < 15 and norm == "ÖNORM B 4000":
        µ_2_neu_2 = 0.8
        µ_2_alt_2 = 1.0
    
    elif int(roof_angle_satteldach_2) >= 15 and int(roof_angle_satteldach_2) < 30 and norm == "ÖNORM B 4000":
        µ_2_neu_2 = 0.8 + 0.2 * (int(roof_angle_satteldach_2) - 15) / 15
        µ_2_alt_2 = 1.0

    elif int(roof_angle_satteldach_2) >= 30 and int(roof_angle_satteldach_2) < 60 and norm == "ÖNORM B 4000":
        µ_2_neu_2 = 1.0 * (60 - int(roof_angle_satteldach_2)) / 30
        µ_2_alt_2 = 1.0 * (70 - int(roof_angle_satteldach_2)) / 40
    
    elif int(roof_angle_satteldach_2) >= 60 and int(roof_angle_satteldach_2) < 70 and norm == "ÖNORM B 4000":
        µ_2_neu_2 = 0
        µ_2_alt_2 = 1.0 * (70 - int(roof_angle_satteldach_2)) / 40

    elif int(roof_angle_satteldach_2) >= 70 and norm == "ÖNORM B 4000":
        µ_2_neu_2 = 0
        µ_2_alt_2 = 0


    elif int(roof_angle_satteldach_2) >= 0 and int(roof_angle_satteldach_2) < 15 and norm == "ÖNORM B 4013":
        µ_2_neu_2 = 0.8
        µ_2_alt_2 = 1.0

    elif int(roof_angle_satteldach_2) >= 15 and int(roof_angle_satteldach_2) < 30 and norm == "ÖNORM B 4013":
        µ_2_neu_2 = 0.8 + 0.2 * (int(roof_angle_satteldach_2) - 15) / 15
        µ_2_alt_2 = 1.0

    elif int(roof_angle_satteldach_2) >= 30 and int(roof_angle_satteldach_2) < 60 and norm == "ÖNORM B 4013":
        µ_2_neu_2 = 1.0 * (60 - int(roof_angle_satteldach_2)) / 30
        µ_2_alt_2 = 1.0 * (60 - int(roof_angle_satteldach_2)) / 30


    elif int(roof_angle_satteldach_2) >= 0 and int(roof_angle_satteldach_2) < 15 and norm == "EN 1991-1-3 2006":
        µ_2_neu_2 = 0.8
        µ_2_alt_2 = 0.8    

    elif int(roof_angle_satteldach_2) >= 15 and int(roof_angle_satteldach_2) < 30 and norm == "EN 1991-1-3 2006":
        µ_2_neu_2 = 0.8 + 0.2 * (int(roof_angle_satteldach_2) - 15) / 15
        µ_2_alt_2 = 0.8 
    
    elif int(roof_angle_satteldach_2) >= 30 and int(roof_angle_satteldach_2) < 60 and norm == "EN 1991-1-3 2006":
        µ_2_neu_2 = 1.0 * (60 - int(roof_angle_satteldach_2)) / 30
        µ_2_alt_2 = 0.8 * (60 - int(roof_angle_satteldach_2)) / 30
    
    elif int(roof_angle_satteldach_2) >= 60 and norm != "ÖNORM B 4000":
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
    roof_type=roof_type+'.png', norm=norm)



if __name__ == '__main__':
    app.run(host="0.0.0.0")    