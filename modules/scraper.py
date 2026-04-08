import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time


def scrap_vilas_bs4(villages_to_scrape, centro_x=182, centro_y=184, dias_inativos=2, distancia_max=25):
    todas_vilas = []
    pagina = 1
    vilas_coletadas = 0
    
    # Headers para fingir que somos um navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    while vilas_coletadas < villages_to_scrape:
        url = (f"https://travcotools.com/en/inactive-search/"
               f"?travian_server=1298"
               f"&x={centro_x}&y={centro_y}"
               f"&days={dias_inativos}"
               f"&distance_max={distancia_max}"
               f"&max_pop_increase=0"
               f"&order_by=distance"
               f"&page={pagina}")

        print(f"→ Acedendo à página {pagina}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Erro ao aceder ao site: Status {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontra a tabela (ajustado para o seletor comum do site)
            table = soup.find('table')
            if not table:
                print("⚠ Tabela não encontrada. Fim dos resultados?")
                break

            rows = table.find('tbody').find_all('tr')
            if not rows:
                break

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5: continue # Pula linhas inválidas

                # 1. Players name, number of villages and population
                player_name_habit = cols[2].text.strip()
                player_name = re.search(r'^[^\s\n]+', player_name_habit).group(0)
                numero_hab_player_aldeia = re.findall(r'\b\d+\b', player_name_habit)
                numero_hab_player = numero_hab_player_aldeia[0]
                numero_de_aldeias = numero_hab_player_aldeia[1]

                # 2. village name and coordinates
                village_text = cols[3].text.strip()
                
                # Regex to clean the village name and extract coordinates
                coord_match = re.search(r'\[(-?\d+)\|(-?\d+)\]', village_text)
                x = int(coord_match.group(1)) if coord_match else None
                y = int(coord_match.group(2)) if coord_match else None
                village_name = re.search(r'^[^\s\n]+', village_text).group(0)
                
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
                    'Jogador': player_name,
                    'Numero de Aldeias': numero_de_aldeias,
                    'Número de Habitantes': numero_hab_player,
                    'Aldeia': village_name,
                    'Coordenadas': f"[{x}|{y}]",
                    'X': x,
                    'Y': y,
                    'População': population,
                    'Distância': distance
                })

                vilas_coletadas += 1
                if vilas_coletadas >= villages_to_scrape:
                    break

            print(f"   ✓ Página {pagina} processada. Total: {vilas_coletadas}")
            
            # Se a página tiver poucos resultados, é a última
            if len(rows) < 10:
                break

            pagina += 1
            
            # Pausa amigável para não ser banido
            time.sleep(1) 

        except Exception as e:
            print(f"❌ Ocorreu um erro: {e}")
            break

    # Creat a dataframe and save to CSV
    df = pd.DataFrame(todas_vilas)
    return df