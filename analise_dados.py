from pprint import pprint
import pandas as pd
import json


def main():
    with open('dados_completos.json', 'r') as json_dados:
        dict_dados = json.loads(json_dados.read())
    
    dict_dfs = json_to_dfs(dict_dados)
    
    # Passar por cada df e incluir a coluna de ganho/minuto
    #--------- Crops ---------
    df_crops = dict_dfs['Crops']
    print(df_crops)
    
def json_to_dfs(dict_dados):
    dict_linhas = {}
    for tipo_colheita in dict_dados:
        colheita_categorias = dict_dados[tipo_colheita]
        dict_linhas[tipo_colheita] = []
        for categoria in colheita_categorias:
            categoria_itens = colheita_categorias[categoria]
            for nome_item in categoria_itens:
                item = categoria_itens[nome_item]
                item['tipo_colheita'] = tipo_colheita
                item['categoria'] = categoria
                
                dict_linhas[tipo_colheita].append(item)
    
    dict_dfs = {}
    for tipo_colheita in dict_linhas:
        dados_atual = dict_linhas[tipo_colheita]
        df_atual = pd.DataFrame(dados_atual)
        dict_dfs[tipo_colheita] = df_atual
    
    return dict_dfs








if __name__ == '__main__':
    main()