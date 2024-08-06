import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from math import isnan

times = {
    "São Paulo": "sao-paulo",
    "Botafogo": "botafogo",
    "Athletico PR": "athletico-pr",
    "CRB": "crb",
    "Flamengo": "flamengo",
    "Atlético GO": "atletico-go",
    "Corinthians": "corinthians",
    "Juventude": "juventude",
    "Vasco": "vasco",
    "RB Braga": "bragantino",
    "Atlético MG": "atletico-mg",
    "Bahia": "bahia",
    "Palmeiras": "palmeiras",
    "Grêmio": "gremio",
    "Fluminense": "fluminense",
    "Goiás": "goias",
    "San Lorenzo": "san-lorenzo",
    "Colo Colo": "colo-colo",
    "Peñarol": "penarol",
    "Talleres": "talleres-cordoba",
    "Nacional": "nacional",
    "Junior FC": "junior-barranquilla",
    "The Strongest": "the-strongest",
    "River Plate": "river-plate",
    "Bolívar": "bolivar"
}

path_planilha = "/home/thiago/Área de trabalho/palpitometro.xlsx"


def verificar_partidas_planilha(path_planilha):
    agora = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_excel(path_planilha)
    partidas_atualizar = []
    for index, row in df.iterrows():
        row_list = row.tolist()
        if not isnan(row_list[0]):
            if isinstance(row_list[1], datetime):
                data_partida = row_list[1].strftime("%Y-%m-%d")
                if agora >= data_partida and isnan(row_list[4]):
                    time_casa = row_list[2]
                    time_fora = row_list[8]
                    placar = [4, 6]
                    partidas_atualizar.append([index, time_casa, time_fora, placar, data_partida])
    return partidas_atualizar, df


def buscar_resultados(partidas_atualizar):
    partidas_resultado = []
    for partida_desatualizadas in partidas_atualizar:
        url = "https://www.placardefutebol.com.br/time/" + str(times[partida_desatualizadas[1]]) + "/ultimos-jogos"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        partidas = soup.find_all('div', attrs={'class': 'match__lg_card'})

        for chave, partida in enumerate(partidas):
            campeonato = partida.find('div', attrs={'class': 'match__lg_card--league'}).text
            if campeonato == "Copa do Brasil" or campeonato == "Copa Libertadores":
                if partida.find_all('div', attrs={'class': 'match__lg_card--date'}):
                    dia_mes = partida.find('div', attrs={'class': 'match__lg_card--date'}).text.split()[1].split("/")
                    data_partida = datetime(2024, int(dia_mes[1]), int(dia_mes[0])).strftime("%Y-%m-%d")
                    time_casa = partida.find('div', attrs={'class': 'match__lg_card--ht-name'}).text
                    time_fora = partida.find('div', attrs={'class': 'match__lg_card--at-name'}).text
                    placar = partida.find('div', attrs={'class': 'match__lg_card--scoreboard'}).text
                    placar = placar.split()
                    placar.pop(1)
                    partidas_resultado.append([campeonato, time_casa, time_fora, placar, data_partida])
    return partidas_resultado


def atualizar_partidas(partidas_atualizar, partidas_resultado, df):
    if not partidas_resultado:
        return "Nenhuma resultado encontrado"
    elif not partidas_atualizar:
        return "Nenhum jogo para atualizar"
    else:
        for chave, resultado in enumerate(partidas_resultado):
            if resultado[4] == partidas_atualizar[chave][4]:
                df.iloc[partidas_atualizar[chave][0], 4] = float(resultado[3][0])
                df.iloc[partidas_atualizar[chave][0], 6] = float(resultado[3][1])
    return df


partidas_atualizar, df = verificar_partidas_planilha(path_planilha)
partidas_resultado = buscar_resultados(partidas_atualizar)
df_atualizado = atualizar_partidas(partidas_atualizar, partidas_resultado, df)

print(partidas_atualizar)
print(partidas_resultado)
for partida in partidas_atualizar:
    print(df_atualizado.iloc[partida[0]].tolist()[2:9])