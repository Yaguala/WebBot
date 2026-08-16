import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time


def scrap_vilas_bs4(picked_server, villages_to_scrape, vilage_coord_X, vilage_coord_Y, dias_inativos=2, distancia_max=100):
    todas_vilas = []
    pagina = 1
    vilas_coletadas = 0
    
    # Clean the coordinates to remove any unwanted characters
    centro_x=str(vilage_coord_X).replace("\u202d", "").replace("\u202c", "")
    centro_y=str(vilage_coord_Y).replace("\u202d", "").replace("\u202c", "")
    server = {"EUROPA 10": "1298", "INTERNATIONAL 4": "1435"}
    
    # Headers to pretend we are a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    while vilas_coletadas < villages_to_scrape:
        url = (f"https://travcotools.com/en/inactive-search/"
               f"?travian_server={server[picked_server]}"
               f"&x={centro_x}&y={centro_y}"
               f"&days={dias_inativos}"
               f"&distance_max={distancia_max}"
               f"&include_natars=on"
               f"&max_pop_increase=0"
               f"&order_by=distance"
               f"&page={pagina}")
        
        print(f"→ Accessing page {pagina}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Error accessing the site: Status {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table containing the villages
            table = soup.find('table')
            if not table:
                print("Table not found on the page. It might be the last page or the structure has changed.")
                break

            rows = table.find('tbody').find_all('tr')
            if not rows:
                break

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5: continue

                # 1. Players name, number of villages and population
                player_name_habit = cols[2].text.strip()
                player_name = re.search(r'^[^\s\n]+', player_name_habit).group(0)
                numero_hab_player_aldeia = re.findall(r'\b\d+\b', player_name_habit)
                numero_hab_player = numero_hab_player_aldeia[0]
                numero_de_aldeias = numero_hab_player_aldeia[1]

                # 2. Village name and coordinates
                # 1. Look for the <a> tag inside any column in this row
                a_tag = cols[3].find('a')
                village_name = a_tag.get("title")
                village_text = cols[3].text
                
                # Regex to clean the village name and extract coordinates
                coord_match = re.search(r'\[(-?\d+)\|(-?\d+)\]', village_text)
                x = int(coord_match.group(1)) if coord_match else None
                y = int(coord_match.group(2)) if coord_match else None
                #village_name = re.search(r'^[^\s\n]+', village_text).group(0)
                # 3. Population
                population = re.findall(r'\d+', village_text)
                population = int(population[-1])

                # 4. Distance
                dist_text = cols[1].text.strip().replace(',', '.')
                try:
                    distance = float(dist_text)
                except:
                    distance = 0.0

                todas_vilas.append({
                    'Player': player_name,
                    'Number of Villages': numero_de_aldeias,
                    'Population': numero_hab_player,
                    'Village': village_name,
                    'Coordinates': f"[{x}|{y}]",
                    'X': x,
                    'Y': y,
                    'População': population,
                    'Distance': distance
                })

                vilas_coletadas += 1
                if vilas_coletadas >= villages_to_scrape:
                    break

            print(f"   ✓ Page {pagina} processed. Total: {vilas_coletadas}")
            
            # If less than 10 rows are found, it means we reached the last page
            if len(rows) < 10:
                break

            pagina += 1
            
            # Stop to dont overload the server and avoid being blocked
            time.sleep(1) 

        except Exception as e:
            print(f"❌ Error occurred: {e}")
            break

    # Creat a dataframe and save to CSV
    df = pd.DataFrame(todas_vilas)
    print(df)
    return df