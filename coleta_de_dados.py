from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
import pandas as pd
import json


URL_BASE = 'https://farmtogether.fandom.com'
url = 'https://farmtogether.fandom.com/wiki/Harvestables'
P_PEIXE_GRANDE = 0.2

def main():
    html = urlopen(url)
    
    bs = BeautifulSoup(html, features='html.parser')
    
    lista_as = bs.find_all('a', class_='image-thumbnail')
    
    print('------------------------------------------------')
    print('Passo 1: Coletar os links para os tipos de colheitas\n')
    
    tipos_colheitas = {}
    for a_colheita in lista_as:
        tipo = a_colheita['title']
        link = a_colheita['href']
        tipos_colheitas[tipo] = URL_BASE+link
    
    pprint(tipos_colheitas)
    
    
    print('\n------------------------------------------------')
    print('Passo 2: Coletar categorias e links dos itens')
    print('Coletando categorias de cada tipo de colheita\ne links dos itens de cada categoria\n')
    itens_por_categoria = carregar_itens_por_colheita(tipos_colheitas)
    pprint(itens_por_categoria)
    print('\nTemos até agora')
    pprint({ 'Tipo_colheita': { 'Categoria 1': { 'Item 1': 'LINK.ITEM.1.com', 'Item 2': 'LINK.ITEM.2.com' }, 'Categoria 2': { 'Item 1': 'LINK.ITEM.1.com', 'Item 2': 'LINK.ITEM.2.com' } } })
    
    print('\n------------------------------------------------')
    print('Passo 3: Coletando dados de cada item')
    itens_completos_por_categoria = carregar_dados_por_item(itens_por_categoria)
    
def carregar_itens_por_colheita(tipos_colheitas):
    itens_por_categoria_por_colheita = {}
    for tipo in tipos_colheitas:
        print('Coletando infos sobre:',tipo)
        link_teste = tipos_colheitas[tipo]
        html = urlopen(link_teste)
        bs = BeautifulSoup(html, features='html.parser')
        
        tabelas = bs.select('table.article-table')
        
        itens_por_categoria = {}
        for tabela in tabelas:
            cat_nome = tabela.select('tr th h3 span b')[0].get_text()
            print('  Categoria:',cat_nome)
            
            itens = {}
            cat_as = tabela.select('tr td span a')
            if(not cat_as):
                cat_as = tabela.select('tr td a')
            for item in cat_as:
                nome = item.get('title')
                link = item.get('href')
                if(not (link == None) and not (item.get('class'))):
                    link = URL_BASE + link
                
                    itens[nome] = link
            
            itens_por_categoria[cat_nome] = itens
        
        itens_por_categoria_por_colheita[tipo] = itens_por_categoria
    return itens_por_categoria_por_colheita

def carregar_dados_por_item(itens_por_categoria_base):
    itens_por_categoria = itens_por_categoria_base.copy()
    
    for tipo_colheita in itens_por_categoria:
        print('Tipo de colheita:',tipo_colheita)
        categorias_tipo_atual = itens_por_categoria[tipo_colheita]
        for categoria in categorias_tipo_atual:
            print('  Categoria:',categoria)
            lista_itens_categoria = categorias_tipo_atual[categoria]
            for nome_item in lista_itens_categoria:
                print('    Item atual:',nome_item)
                link = lista_itens_categoria[nome_item]
                
                dados_item = coletar_dados_item(tipo_colheita, link)
                dados_item['nome'] = nome_item
                dados_item['link'] = link
                
                #pprint(dados_item)
                itens_por_categoria[tipo_colheita][categoria][nome_item] = dados_item
    
    with open('dados_completos.json', 'w') as json_file:
        json.dump(itens_por_categoria, json_file)

def coletar_dados_item(tipo_colheita, link):
    if(tipo_colheita == 'Crops'):
        propriedades = coletar_dados_crop(link)
        return propriedades
    if(tipo_colheita == 'Trees'):
        propriedades = coletar_dados_tree(link)
        return propriedades
    if(tipo_colheita == 'Flowers'):
        propriedades = coletar_dados_flower(link)
        return propriedades
    if(tipo_colheita == 'Ponds'):
        propriedades = coletar_dados_pond(link)
        return propriedades
    if(tipo_colheita == 'Animals'):
        propriedades = coletar_dados_animal(link)
        return propriedades
    
    return {}

def extrair_valor(linha):
    valor = linha.select('td')[0].get_text()
    if(',' in str(valor)):
        valor = valor.replace(',', '.')
    if(' ' in str(valor)):
        valor = valor.split()[0]
    if('k' in str(valor) or 'K' in str(valor)):
        valor = valor.replace('k','')
        valor = valor.replace('K','')
        valor = float(valor) * 1000
    if(not str(valor).strip()):
        valor = 0
    valor = float(valor)
    
    if('Money' in str(linha)):
        moeda = 'dinheiro'
    else:
        moeda = 'diamante'
    
    return valor, moeda

def extrair_estacoes(linha):
    estacoes = []
    if('Fall' in str(linha)):
        estacoes.append('fall')
    if('Spring' in str(linha)):
        estacoes.append('spring')
    if('Winter' in str(linha)):
        estacoes.append('winter')
    if('Summer' in str(linha)):
        estacoes.append('summer')
    
    return estacoes

def extrair_ganho(linha):
    tds = linha.select('td')
    if(tds[0].get_text().strip()):
        try:
            ganho, xp = tds[0].get_text().split()
        except:
            xp = tds[0].get_text().split()[0]
    else:
        xp = 0
    
    ganho = linha.select('td')[0].get_text()
    if(',' in str(ganho)):
        ganho = ganho.replace(',', '.')
    if(' ' in str(ganho)):
        ganho = ganho.split()[0]
    if('k' in str(ganho) or 'K' in str(ganho)):
        ganho = ganho.replace('k','')
        ganho = ganho.replace('K','')
        ganho = float(ganho) * 1000
    if(not str(ganho).strip()):
        ganho = 0
    
    if('Diamonds' in str(linha)):
        moeda = 'diamante'
    else:
        moeda = 'dinheiro'
    
    try:
        xp = float(xp)
    except ValueError:
        xp = float(str(linha).split('</a>')[1].split('<a')[0])
    
    ganho = float(ganho)
    
    return ganho, moeda, xp

def extrair_tempo(linha):
    tempo_total = 0
    tempos = linha.select('td')[0].get_text().split()
    for i in tempos:
        if('m' in i and 'h' in i):
            tempo = i.replace('m', '')
            tempo = tempo.split('h')
            tempo = float(tempo[0]) * 60 + float(tempo[1])
        elif('m' in i):
            tempo = int(i.replace('m', ''))
        elif('hours' in tempos):
            tempo = float(tempos[0]) * 60
            tempo_total += tempo
            break
        elif('h' in i):
            tempo = int(i.replace('h', ''))
            tempo = tempo * 60
        elif('d' in i):
            tempo = int(i.replace('d', ''))
            tempo = tempo * 24 * 60
        else:
            tempo = float(i)
        tempo_total += tempo
        
    return tempo_total

def extrair_recurso(linha):
    tipo_recurso = linha.select('img')[0].get('alt')
    return tipo_recurso

def extrair_p_pesca(linha):
    p_pesca = linha.select('td')[0].get_text()
    p_pesca = float(p_pesca.replace(' ', '').replace('%', ''))
    p_pesca /= 100
    
    return p_pesca

def extrair_comida_custo(linha):
    custo_tempo = linha.select('td')[0].get_text()
    if('h' in custo_tempo and 'm' in custo_tempo):
        custo_tempo = custo_tempo.replace('h ','h')
    custo, tempo = custo_tempo.replace('\n','').split()
    
    #Tratar valores do custo
    if(',' in str(custo)):
        custo = custo.replace(',', '.')
    if(' ' in str(custo)):
        custo = custo.split()[0]
    if('k' in str(custo) or 'K' in str(custo)):
        custo = custo.replace('k','')
        custo = custo.replace('K','')
        custo = float(custo) * 1000
    if(not str(custo).strip()):
        custo = 0
    
    #Tratar unidades tempo
    if('m' in tempo and 'h' in tempo):
        tempo = tempo.replace('m', '')
        tempo = tempo.split('h')
        tempo = float(tempo[0]) * 60 + float(tempo[1])
    elif('m' in tempo):
        tempo = int(tempo.replace('m', ''))
    elif('hours' in tempo):
        tempo = int(tempo.replace('hours', ''))
        tempo = float(tempo) * 60
    elif('h' in tempo):
        tempo = int(tempo.replace('h', ''))
        tempo = tempo * 60
    elif('d' in tempo):
        tempo = int(tempo.replace('d', ''))
        tempo = tempo * 24 * 60
    
    return custo, tempo

def extrair_comida_vezes(linha):
    vezes = linha.select('td')[0].get_text().replace(' ', '')
    vezes = float(vezes)
    
    return vezes

def extrair_comida_total(linha):
    total = linha.select('td')[0].get_text().replace(' ', '').replace('"','')
    total = total.replace('\n','')
    
    #Tratar valores do custo
    if(',' in str(total)):
        total = total.replace(',', '.')
    if(' ' in str(total)):
        total = total.split()[0]
    if('k' in str(total) or 'K' in str(total)):
        total = total.replace('k','')
        total = total.replace('K','')
        total = float(total) * 1000
    if(not str(total).strip()):
        total = 0
    
    total = float(total)
    
    return total

def coletar_dados_crop(link):
    #['custo', 'ganho_base', 'moeda_ganho', 'tempo', 'tipo_recurso', 'xp', 'estacoes']
    html = urlopen(link)
    bs = BeautifulSoup(html, features='html.parser')
    
    dict_item = {}
    
    #COLETANDO DADOS DA TABELA DE CABECALHO
    tabela_ok = True
    try:
        tabela = bs.select('table.infobox')[0]
        linhas_tabela = tabela.select('tr')
    except IndexError:
        tabela_ok = False
    
    propriedades = {}
    ganho_coletado = False
    if(tabela_ok):
        url_img = tabela.select('a.image')[0].get('href')
        propriedades['url_img'] = url_img
        for linha in linhas_tabela:
            if('<th' in str(linha)):
                propriedade = linha.select('th')[0]
                if('Buy' in str(propriedade)):
                    valor, moeda = extrair_valor(linha)
                    propriedades['custo'] = valor
                    propriedades['moeda_custo'] = moeda
                
                elif('Plant on' in str(propriedade)):
                    propriedade = 'estacoes'
                    estacoes = extrair_estacoes(linha)
                    propriedades[propriedade] = estacoes
                    
                elif('Harvest' in str(propriedade) and not 'Info' in str(propriedade) and not 'each' in str(propriedade)):
                    ganho, moeda, xp = extrair_ganho(linha)
                    propriedades['xp'] = xp
                    propriedades['ganho_base'] = ganho
                    propriedades['moeda_ganho'] = moeda
                
                elif('Harvest each' in str(propriedade)):
                    propriedade = 'tempo'
                    tempo_total = extrair_tempo(linha)
                    propriedades[propriedade] = tempo_total
                
                elif('Resource' in str(propriedade)):
                    propriedade = 'tipo_recurso'
                    tipo_recurso = extrair_recurso(linha)
                    propriedades[propriedade] = tipo_recurso
    else:
        propriedades['custo'] = 0
        propriedades['url_img'] = ''
        propriedades['moeda_custo'] = 0
        propriedades['estacoes'] = []
        propriedades['ganho_base'] = 0
        propriedades['xp'] = 0
        propriedades['tipo_recurso'] = 0
        propriedades['tempo'] = 0
        propriedades['moeda_ganho'] = 'dinheiro'
    
    return propriedades

def coletar_dados_tree(link):
    #['custo', 'ganho_base', 'moeda_ganho', 'tipo_recurso', 'xp', 'estacoes']
    html = urlopen(link)
    bs = BeautifulSoup(html, features='html.parser')
    
    dict_item = {}
    
    #COLETANDO DADOS DA TABELA DE CABECALHO
    tabela_ok = True
    try:
        tabela = bs.select('table.infobox')[0]
        linhas_tabela = tabela.select('tr')
    except IndexError:
        tabela_ok = False
    
    propriedades = {}
    ganho_coletado = False
    if(tabela_ok):
        url_img = tabela.select('a.image')[0].get('href')
        propriedades['url_img'] = url_img
        for linha in linhas_tabela:
            if('<th' in str(linha)):
                propriedade = linha.select('th')[0]
                if('Buy' in str(propriedade)):
                    valor, moeda = extrair_valor(linha)
                    propriedades['custo'] = valor
                    propriedades['moeda_custo'] = moeda
                
                elif('Harvest each' in str(propriedade)):
                    propriedade = 'estacoes'
                    estacoes = extrair_estacoes(linha)
                    propriedades[propriedade] = estacoes
                    
                elif('Harvest' in str(propriedade) and not 'Info' in str(propriedade) and not 'each' in str(propriedade)):
                    ganho, moeda, xp = extrair_ganho(linha)
                    propriedades['xp'] = xp
                    propriedades['ganho_base'] = ganho
                    propriedades['moeda_ganho'] = moeda
                
                elif('Resource' in str(propriedade)):
                    propriedade = 'tipo_recurso'
                    tipo_recurso = extrair_recurso(linha)
                    propriedades[propriedade] = tipo_recurso
        propriedades['quant_estacoes'] = len(propriedades['estacoes'])

    else:
        propriedades['custo'] = 0
        propriedades['url_img'] = ''
        propriedades['moeda_custo'] = 0
        propriedades['ganho_base'] = 0
        propriedades['estacoes'] = []
        propriedades['xp'] = 0
        propriedades['tipo_recurso'] = 0
        propriedades['moeda_ganho'] = 'dinheiro'
    
    return propriedades

def coletar_dados_flower(link):
    #['custo', 'ganho_base', 'moeda_ganho', 'tempo', 'tipo_recurso', 'xp']
    html = urlopen(link)
    bs = BeautifulSoup(html, features='html.parser')
    
    dict_item = {}
    
    #COLETANDO DADOS DA TABELA DE CABECALHO
    tabela_ok = True
    try:
        tabela = bs.select('table.infobox')[0]
        linhas_tabela = tabela.select('tr')
    except IndexError:
        tabela_ok = False
    
    propriedades = {}
    ganho_coletado = False
    if(tabela_ok):
        url_img = tabela.select('a.image')[0].get('href')
        propriedades['url_img'] = url_img
        for linha in linhas_tabela:
            if('<th' in str(linha)):
                propriedade = linha.select('th')[0]
                if('Buy' in str(propriedade)):
                    valor, moeda = extrair_valor(linha)
                    propriedades['custo'] = valor
                    propriedades['moeda_custo'] = moeda
                    
                elif('Harvest' in str(propriedade) and not 'Info' in str(propriedade) and not 'each' in str(propriedade)):
                    ganho, moeda, xp = extrair_ganho(linha)
                    propriedades['xp'] = xp
                    propriedades['ganho_base'] = ganho
                    propriedades['moeda_ganho'] = moeda
                
                elif('Harvest each' in str(propriedade)):
                    propriedade = 'tempo'
                    tempo_total = extrair_tempo(linha)
                    propriedades[propriedade] = tempo_total
                
                elif('Resource' in str(propriedade)):
                    propriedade = 'tipo_recurso'
                    tipo_recurso = extrair_recurso(linha)
                    propriedades[propriedade] = tipo_recurso
    else:
        propriedades['custo'] = 0
        propriedades['url_img'] = ''
        propriedades['moeda_custo'] = 0
        propriedades['ganho_base'] = 0
        propriedades['xp'] = 0
        propriedades['tipo_recurso'] = 0
        propriedades['tempo'] = 0
        propriedades['moeda_ganho'] = 'dinheiro'
    
    return propriedades

def coletar_dados_pond(link):
    #['custo', 'moeda_ganho', 'tempo', 'tipo_recurso', 'xp', 'ganho_grande', 'ganho_pequeno', 'p_pesca']
    html = urlopen(link)
    bs = BeautifulSoup(html, features='html.parser')
    
    dict_item = {}
    
    #COLETANDO DADOS DA TABELA DE CABECALHO
    tabela_ok = True
    try:
        tabela = bs.select('table.infobox')[0]
        linhas_tabela = tabela.select('tr')
    except IndexError:
        tabela_ok = False
    
    propriedades = {}
    ganho_coletado = False
    if(tabela_ok):
        url_img = tabela.select('a.image')[0].get('href')
        propriedades['url_img'] = url_img
        for linha in linhas_tabela:
            if('<th' in str(linha)):
                propriedade = linha.select('th')[0]
                if('Buy' in str(propriedade)):
                    valor, moeda = extrair_valor(linha)
                    propriedades['custo'] = valor
                    propriedades['moeda_custo'] = moeda
                
                elif('Big catch' in str(propriedade)):
                    ganho, moeda, xp = extrair_ganho(linha)
                    propriedades['xp'] = xp
                    propriedades['ganho_grande'] = ganho
                    propriedades['moeda_ganho'] = moeda
                
                elif('Small catch' in str(propriedade)):
                    ganho, moeda, _ = extrair_ganho(linha)
                    propriedades['ganho_pequeno'] = ganho
                    propriedades['moeda_ganho'] = moeda
                
                elif('Fish each' in str(propriedade)):
                    propriedade = 'tempo'
                    tempo_total = extrair_tempo(linha)
                    propriedades[propriedade] = tempo_total
                
                elif('Catch rate' in str(propriedade)):
                    p_pesca = extrair_p_pesca(linha)
                    propriedades['p_pesca'] = p_pesca
                    propriedades['p_ganho_grande'] = P_PEIXE_GRANDE
    else:
        propriedades['custo'] = 0
        propriedades['url_img'] = ''
        propriedades['tempo'] = 0
        propriedades['moeda_custo'] = 0
        propriedades['ganho_base'] = 0
        propriedades['ganho_grande'] = 0
        propriedades['ganho_pequeno'] = 0
        propriedades['moeda_ganho'] = 'dinheiro'
        propriedades['xp'] = 0
        propriedades['p_pesca'] = 0
        propriedades['p_ganho_grande'] = 0
    
    return propriedades

def coletar_dados_animal(link):
    #['custo', 'ganho_base', 'moeda_ganho', 'tempo', 'tipo_recurso', 'xp', 'comida_tempo', 'comida_custo', 'comida_vezes', 'comida_total']
    html = urlopen(link)
    bs = BeautifulSoup(html, features='html.parser')
    
    dict_item = {}
    
    #COLETANDO DADOS DA TABELA DE CABECALHO
    tabela_ok = True
    try:
        tabela = bs.select('table.infobox')[0]
        linhas_tabela = tabela.select('tr')
    except IndexError:
        tabela_ok = False
    
    propriedades = {}
    ganho_coletado = False
    if(tabela_ok):
        url_img = tabela.select('a.image')[0].get('href')
        propriedades['url_img'] = url_img
        for linha in linhas_tabela:
            if('<th' in str(linha)):
                propriedade = linha.select('th')[0]
                if('Buy' in str(propriedade)):
                    valor, moeda = extrair_valor(linha)
                    propriedades['custo'] = valor
                    propriedades['moeda_custo'] = moeda
                    
                elif('Harvest' in str(propriedade) and not 'Info' in str(propriedade) and not 'each' in str(propriedade)):
                    ganho, moeda, xp = extrair_ganho(linha)
                    propriedades['xp'] = xp
                    propriedades['ganho_total'] = ganho
                    propriedades['moeda_ganho'] = moeda
                
                elif('Harvest each' in str(propriedade)):
                    propriedade = 'tempo'
                    tempo_total = extrair_tempo(linha)
                    propriedades[propriedade] = tempo_total
                
                elif('Resource' in str(propriedade)):
                    propriedade = 'tipo_recurso'
                    tipo_recurso = extrair_recurso(linha)
                    propriedades[propriedade] = tipo_recurso
                
                elif('Feed' in str(propriedade) and not 'Steps' in str(propriedade) and not 'Info' in str(propriedade) and not 'Total' in str(propriedade)):
                    comida_custo, comida_tempo = extrair_comida_custo(linha)
                    propriedades['comida_custo'] = comida_custo
                    propriedades['comida_tempo'] = comida_tempo
                
                elif('Feed Steps' in str(propriedade)):
                    propriedade = 'comida_vezes'
                    comida_vezes = extrair_comida_vezes(linha)
                    propriedades[propriedade] = comida_vezes
                
                elif('Total Feed' in str(propriedade)):
                    propriedade = 'comida_total'
                    comida_total = extrair_comida_total(linha)
                    propriedades[propriedade] = comida_total
    else:
        propriedades['custo'] = 0
        propriedades['url_img'] = ''
        propriedades['moeda_custo'] = 0
        propriedades['ganho_base'] = 0
        propriedades['xp'] = 0
        propriedades['tipo_recurso'] = 0
        propriedades['tempo'] = 0
        propriedades['moeda_ganho'] = 'dinheiro'
        propriedades['comida_custo'] = 0
        propriedades['comida_tempo'] = 0
        propriedades['comida_vezes'] = 0
        propriedades['comida_total'] = 0
    
    return propriedades





















if __name__ == '__main__':
    main()