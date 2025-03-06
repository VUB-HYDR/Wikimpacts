# use wikidata query service via python, aim to get data of different extreme events 
#wdt means property,P31 presents instance of 
"""
dict_extreme_events = {'flood':'Q8068','heatwave':'Q215864',
                      'storm':'Q81054','drought':'Q43059','wildfire':'Q169950' (brush firebushfiregrass firehill firepeat firewildfireswild firedesert firevegetation firebush firewildland fire),
                      cold wave (Q642683)
                      heat wave (Q215864)
                      dry spell (Q122413684)
                      dryness (Q1513116)
                      water scarcity (Q5376358)
                      }
                      water stress (Q489777)
                      overdrafting (groundwater depletion) (Q7113626)
                      extreme heat (Q3774617)
                      summer heat (Q12888883) (hot weatherhot climate)
                      hot (Q28128222) (heathigh temperaturehotnesshot temperatureZafi)
                      cold (Q270952) (cold temperaturechilllow temperaturecoldnesschillycoolcoolnesscool temperature)
                      extreme cold (Q70442137)
                      cold weather (Q14212031)
                        storm surge (Q121742) (storm floodstorm tide)
                        forest fire (Q107434304)
                        cyclone (Q79602)
                        typhoon (Q140588)
                        hurricane (Q34439356)
                        blizzard (Q205418)
                        wind gust (Q3417299)
                        tornado (Q8081)
                        wind (Q8094)
                        thunderstorm (Q2857578)
                        hail (Q37602)
                        extreme rainfall (Q111089542)
                        heavy rain (Q18447212)
                        driving rain (Q2238184) (torrential rain)
                        cloudburst (Q16539644) (sudden rain)

                      """
#dict_info_data = {'country':'P17','location':'P625','point in time':'P585'}
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
for  value in dict_extreme_events.items():
    #for info, infocode in dict_info_data.items():
    
      sparql.setQuery('''
      SELECT ?item ?itemLabel ?countryLabel ?location ?locationLabel ?date ?dateLabel
      WHERE
      {{
        ?item wdt:P31 wd: {value} .
        
        OPTIONAL { ?item wdt:P17 ?country. }
        OPTIONAL { ?item wdt:P625 ?location. }
        OPTIONAL { ?item wdt:P585 ?date. }
    
         SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
       }}
       ''')
      sparql.setReturnFormat(JSON)
      results = sparql.query().convert()
      results_df = pd.json_normalize(results['results']['bindings'])
      results_df[['item.value', 'itemLabel.value']].head()