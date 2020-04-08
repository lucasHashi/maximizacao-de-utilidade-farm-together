from bs4 import BeautifulSoup
from urllib.request import urlopen
from pprint import pprint
import pandas as pd


URL_BASE = 'https://farmtogether.fandom.com'
url = 'https://farmtogether.fandom.com/wiki/Harvestables'

def main():
    html = urlopen(url)
    
    bs = BeautifulSoup(html, features='html.parser')
    
    lista_as = bs.find_all('a', class_='image-thumbnail')
    
    tipos_colheitas = {}
    for a_colheita in lista_as:
        tipo = a_colheita['title']
        link = a_colheita['href']
        tipos_colheitas[tipo] = URL_BASE+link
    
    print('------------------------------------------------')
    print('Passo 1: Coletar os links para os tipos de colheitas\n')
    pprint(tipos_colheitas)
    
    
    print('\n------------------------------------------------')
    print('Coletando categorias de cada tipo de colheita\ne links dos itens de cada categoria\n')
    itens_por_categoria = carregar_itens_por_colheita(tipos_colheitas)
    pprint(itens_por_categoria)
    print('\nTemos até agora')
    pprint({ 'Tipo_colheita': { 'Categoria 1': { 'Item 1': 'LINK.ITEM.1.com', 'Item 2': 'LINK.ITEM.2.com' }, 'Categoria 2': { 'Item 1': 'LINK.ITEM.1.com', 'Item 2': 'LINK.ITEM.2.com' } } })
    
    print('\n------------------------------------------------')
    print('Coletando dados de cada item')
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
    #for tipo_colheita in itens_por_categoria:
    for tipo_colheita in ['Crops']:
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
                
                pprint(dados_item)
                itens_por_categoria[tipo_colheita][categoria][nome_item] = dados_item

def coletar_dados_item(tipo_colheita, link):
    if(tipo_colheita == 'Crops'):
        propriedades = coletar_dados_crop(link)
        return propriedades
    if(tipo_colheita == 'Trees'):
        propriedades = coletar_dados_tree(link)
        return propriedades
    if(tipo_colheita == 'Flowers'):
        propriedades = coletar_dados_flowers(link)
        return propriedades
    if(tipo_colheita == 'Ponds'):
        propriedades = coletar_dados_ponds(link)
        return propriedades
    if(tipo_colheita == 'Animals'):
        propriedades = coletar_dados_animal(link)
        return propriedades
    
    return {}

def coletar_dados_crop(link):
    html = urlopen(link)
    bs = BeautifulSoup(html, features='html.parser')
    
    dict_item = {}
    
    #COLETANDO DADOS DA TABELA DE CABECALHO
    tabela_ok = True
    try:
        tabela = bs.select('table.infobox')[0]
        nome = tabela.select('th h3 span')[0].get_text()
        linhas_propriedades = tabela.select('tr')
    except IndexError:
        tabela_ok = False
    
    propriedades = {}
    ganho_coletado = False
    if(tabela_ok):
        for linha in linhas_propriedades:
            if('<th' in str(linha)):
                propriedade = linha.select('th')[0]
                if('Buy' in str(propriedade)):
                    propriedade = 'custo'
                    
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
                    
                    propriedades[propriedade] = valor
                elif('Plant on' in str(propriedade)):
                    propriedade = 'estacoes'
                    estacoes = []
                    if('Fall' in str(linha)):
                        estacoes.append('fall')
                    if('Spring' in str(linha)):
                        estacoes.append('spring')
                    if('Winter' in str(linha)):
                        estacoes.append('winter')
                    if('Summer' in str(linha)):
                        estacoes.append('summer')
                    propriedades[propriedade] = estacoes
                elif('Harvest' in str(propriedade) and not 'Info' in str(propriedade) and not 'each' in str(propriedade)):
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
                    
                    if('Diamonds' in str(propriedade)):
                        moeda = 'diamantes'
                    else:
                        moeda = 'dinheiro'
                    xp = float(xp)
                    ganho = float(ganho)
                    propriedades['xp'] = xp
                    propriedades['ganho_base'] = ganho
                    propriedades['moeda_ganho'] = moeda
                elif('Harvest each' in str(propriedade)):
                    propriedade = 'tempo'
                    tempo_total = 0
                    tempos = linha.select('td')[0].get_text().split()
                    for i in tempos:
                        if('m' in i):
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
                        tempo_total += tempo
                    propriedades[propriedade] = tempo_total
                elif('Resource' in str(propriedade)):
                    propriedade = 'tipo_recurso'
                    tipo_recurso = linha.select('img')[0].get('alt')
                    propriedades[propriedade] = tipo_recurso
    else:
        propriedades['custo'] = 0
        propriedades['estacoes'] = []
        propriedades['xp'] = 0
        propriedades['tipo_recurso'] = 0
        propriedades['tempo'] = 0
        
    
    return propriedades
        


























if __name__ == '__main__':
    main()