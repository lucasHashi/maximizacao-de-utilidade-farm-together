from pprint import pprint
import pandas as pd
import json


def main():
    with open('dados_completos_v2.json', 'r') as json_dados:
        dict_dados = json.loads(json_dados.read())
    
    dict_dfs = json_to_dfs(dict_dados)
    
    colunas_final = ['tipo_colheita', 'nome', 'tipo_recurso','nivel_fazenda',
                    'custo', 'moeda_custo', 'xp', 'ganho_base',
                    'moeda_ganho', 'tempo', 'ganho_por_min',
                    'xp_por_min', 'dinheiros_por_diamante', 'tipo_ganho', 'url_img']
    # Passar por cada df e incluir a coluna de ganho/minuto
    #--------- Crops ---------
    df_crops = dict_dfs['Crops']
    df_completo_crops = calcular_medidas_crops(df_crops)
    df_final_crops = df_completo_crops[colunas_final]

    df_trees = dict_dfs['Trees']
    df_completo_trees = calcular_medidas_trees(df_trees)
    df_final_trees = df_completo_trees[colunas_final]

    df_flowers = dict_dfs['Flowers']
    df_completo_flowers = calcular_medidas_flowers(df_flowers)
    df_final_flowers = df_completo_flowers[colunas_final]

    df_ponds = dict_dfs['Ponds']
    df_completo_ponds = calcular_medidas_ponds(df_ponds)
    df_final_ponds = df_completo_ponds[colunas_final]

    df_animals = dict_dfs['Animals']
    df_completo_animals = calcular_medidas_animals(df_animals)
    df_final_animals = df_completo_animals[colunas_final]

    list_dfs_finais = [df_final_crops, df_final_trees, df_final_flowers, df_final_ponds, df_final_animals]

    df_final = pd.concat(list_dfs_finais)

    df_final.sort_values(by=['tipo_colheita','nome'], inplace=True)
    df_final.reset_index(drop=True,inplace=True)

    df_final.to_csv(path_or_buf='final.csv',index=False, float_format='%.2f', decimal='.')
    df_final.to_csv(path_or_buf='final_excel.csv',index=False, float_format='%.2f', decimal=',', sep=';')

    #print(df_final.sort_values('ganho_por_min', ascending=False)[:20])
    

    
    
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

def calcular_medidas_crops(df_crops_base):
    df_crops = df_crops_base.copy()
    CUSTO_BASE_CROPS = 10 #moeda = dinheiros

    # Classificar cada item com seu tipo de ganho
    df_crops.loc[(df_crops['moeda_custo'] == df_crops['moeda_ganho']) & (df_crops['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_dinheiro'
    df_crops.loc[(df_crops['moeda_custo'] != df_crops['moeda_ganho']) & (df_crops['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_diamante'
    df_crops.loc[(df_crops['moeda_custo'] != df_crops['moeda_ganho']) & (df_crops['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_dinheiro'
    df_crops.loc[(df_crops['moeda_custo'] == df_crops['moeda_ganho']) & (df_crops['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_diamante'

    df_crops['ganho_por_min'] = 0
    df_crops.loc[((df_crops['tipo_ganho'] == 'dinheiro_dinheiro') | (df_crops['tipo_ganho'] == 'diamante_diamante')), 'ganho_por_min'] = (df_crops['ganho_base'] - (df_crops['custo'] + CUSTO_BASE_CROPS))/df_crops['tempo']

    df_crops['xp_por_min'] = 0
    df_crops['xp_por_min'] = df_crops['xp']/df_crops['tempo']

    df_crops['dinheiros_por_diamante'] = 0
    df_crops.loc[df_crops['tipo_ganho'] == 'diamante_dinheiro', 'dinheiros_por_diamante'] = df_crops['ganho_base']/df_crops['custo']
    df_crops.loc[df_crops['tipo_ganho'] == 'dinheiro_diamante', 'dinheiros_por_diamante'] = (df_crops['custo'] + CUSTO_BASE_CROPS)/df_crops['ganho_base']

    return df_crops

def calcular_medidas_trees(df_trees_base):
    df_trees = df_trees_base.copy()

    # Classificar cada item com seu tipo de ganho
    df_trees.loc[(df_trees['moeda_custo'] == df_trees['moeda_ganho']) & (df_trees['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_dinheiro'
    df_trees.loc[(df_trees['moeda_custo'] != df_trees['moeda_ganho']) & (df_trees['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_diamante'
    df_trees.loc[(df_trees['moeda_custo'] != df_trees['moeda_ganho']) & (df_trees['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_dinheiro'
    df_trees.loc[(df_trees['moeda_custo'] == df_trees['moeda_ganho']) & (df_trees['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_diamante'

    df_trees['tempo'] = (17*4) / df_trees['quant_estacoes']

    df_trees['ganho_por_min'] = 0
    df_trees.loc[((df_trees['tipo_ganho'] == 'dinheiro_dinheiro') | (df_trees['tipo_ganho'] == 'diamante_diamante')), 'ganho_por_min'] = df_trees['ganho_base']/df_trees['tempo']

    df_trees['dinheiros_por_diamante'] = 0
    df_trees.loc[df_trees['tipo_ganho'] == 'diamante_dinheiro', 'dinheiros_por_diamante'] = df_trees['ganho_base']/df_trees['custo']
    df_trees.loc[df_trees['tipo_ganho'] == 'dinheiro_diamante', 'dinheiros_por_diamante'] = df_trees['custo']/df_trees['ganho_base']

    df_trees['xp_por_min'] = 0
    df_trees['xp_por_min'] = df_trees['xp'] / df_trees['tempo']

    df_trees['min_sem_lucro'] = 0
    df_trees.loc[(df_trees['ganho_por_min'] > 0) & ((df_trees['tipo_ganho'] == 'diamante_diamante') | (df_trees['tipo_ganho'] == 'dinheiro_dinheiro')), 'min_sem_lucro'] = df_trees['custo'] / df_trees['ganho_por_min']

    return df_trees

def calcular_medidas_flowers(df_flowers_base):
    df_flowers = df_flowers_base.copy()

    # Classificar cada item com seu tipo de ganho
    df_flowers.loc[(df_flowers['moeda_custo'] == df_flowers['moeda_ganho']) & (df_flowers['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_dinheiro'
    df_flowers.loc[(df_flowers['moeda_custo'] != df_flowers['moeda_ganho']) & (df_flowers['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_diamante'
    df_flowers.loc[(df_flowers['moeda_custo'] != df_flowers['moeda_ganho']) & (df_flowers['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_dinheiro'
    df_flowers.loc[(df_flowers['moeda_custo'] == df_flowers['moeda_ganho']) & (df_flowers['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_diamante'

    df_flowers['ganho_por_min'] = 0
    df_flowers.loc[((df_flowers['tipo_ganho'] == 'dinheiro_dinheiro') | (df_flowers['tipo_ganho'] == 'diamante_diamante')), 'ganho_por_min'] = df_flowers['ganho_base']/df_flowers['tempo']

    df_flowers['dinheiros_por_diamante'] = 0
    df_flowers.loc[df_flowers['tipo_ganho'] == 'diamante_dinheiro', 'dinheiros_por_diamante'] = df_flowers['ganho_base']/df_flowers['custo']
    df_flowers.loc[df_flowers['tipo_ganho'] == 'dinheiro_diamante', 'dinheiros_por_diamante'] = df_flowers['custo']/df_flowers['ganho_base']

    df_flowers['xp_por_min'] = 0
    df_flowers['xp_por_min'] = df_flowers['xp'] / df_flowers['tempo']

    df_flowers['min_sem_lucro'] = 0
    df_flowers.loc[(df_flowers['ganho_por_min'] > 0) & ((df_flowers['tipo_ganho'] == 'diamante_diamante') | (df_flowers['tipo_ganho'] == 'dinheiro_dinheiro')), 'min_sem_lucro'] = df_flowers['custo'] / df_flowers['ganho_por_min']

    return df_flowers

def calcular_medidas_ponds(df_ponds_base):
    df_ponds = df_ponds_base.copy()

    # Classificar cada item com seu tipo de ganho
    df_ponds.loc[(df_ponds['moeda_custo'] == df_ponds['moeda_ganho']) & (df_ponds['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_dinheiro'
    df_ponds.loc[(df_ponds['moeda_custo'] != df_ponds['moeda_ganho']) & (df_ponds['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_diamante'
    df_ponds.loc[(df_ponds['moeda_custo'] != df_ponds['moeda_ganho']) & (df_ponds['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_dinheiro'
    df_ponds.loc[(df_ponds['moeda_custo'] == df_ponds['moeda_ganho']) & (df_ponds['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_diamante'

    df_ponds['ganho_base'] = df_ponds['p_pesca'] * (df_ponds['ganho_grande'] + df_ponds['ganho_pequeno'])

    df_ponds['ganho_por_min'] = 0
    df_ponds.loc[((df_ponds['tipo_ganho'] == 'dinheiro_dinheiro') | (df_ponds['tipo_ganho'] == 'diamante_diamante')), 'ganho_por_min'] = df_ponds['ganho_base'] / (df_ponds['tempo'] * 2)

    df_ponds['dinheiros_por_diamante'] = 0
    df_ponds.loc[df_ponds['tipo_ganho'] == 'diamante_dinheiro', 'dinheiros_por_diamante'] = df_ponds['ganho_base'] / df_ponds['custo']

    df_ponds.loc[df_ponds['tipo_ganho'] == 'dinheiro_diamante', 'dinheiros_por_diamante'] = df_ponds['custo'] / df_ponds['ganho_base']

    df_ponds['xp_por_min'] = 0
    df_ponds['xp_por_min'] = df_ponds['xp'] / df_ponds['tempo']

    df_ponds['min_sem_lucro'] = 0
    df_ponds.loc[(df_ponds['ganho_por_min'] > 0) & ((df_ponds['tipo_ganho'] == 'diamante_diamante') | (df_ponds['tipo_ganho'] == 'dinheiro_dinheiro')), 'min_sem_lucro'] = df_ponds['custo'] / df_ponds['ganho_base']

    df_ponds['tipo_recurso'] = 'Fishs'

    return df_ponds

def calcular_medidas_animals(df_animals_base):
    df_animals = df_animals_base.copy()

    # Classificar cada item com seu tipo d'e ganho
    df_animals.loc[(df_animals['moeda_custo'] == df_animals['moeda_ganho']) & (df_animals['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_dinheiro'
    df_animals.loc[(df_animals['moeda_custo'] != df_animals['moeda_ganho']) & (df_animals['moeda_custo'] == 'dinheiro'), 'tipo_ganho'] = 'dinheiro_diamante'
    df_animals.loc[(df_animals['moeda_custo'] != df_animals['moeda_ganho']) & (df_animals['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_dinheiro'
    df_animals.loc[(df_animals['moeda_custo'] == df_animals['moeda_ganho']) & (df_animals['moeda_custo'] == 'diamante'), 'tipo_ganho'] = 'diamante_diamante'

    df_animals['ganho_base'] = df_animals['ganho_total'] - df_animals['comida_total']

    df_animals['ganho_por_min'] = 0
    df_animals.loc[((df_animals['tipo_ganho'] == 'dinheiro_dinheiro') | (df_animals['tipo_ganho'] == 'diamante_diamante')), 'ganho_por_min'] = df_animals['ganho_base']/df_animals['tempo']

    df_animals['dinheiros_por_diamante'] = 0
    df_animals.loc[df_animals['tipo_ganho'] == 'diamante_dinheiro', 'dinheiros_por_diamante'] = df_animals['ganho_base']/df_animals['custo']
    df_animals.loc[df_animals['tipo_ganho'] == 'dinheiro_diamante', 'dinheiros_por_diamante'] = df_animals['custo']/df_animals['ganho_base']

    df_animals['xp_por_min'] = 0
    df_animals['xp_por_min'] = df_animals['xp'] / df_animals['tempo']

    df_animals['min_sem_lucro'] = 0
    df_animals.loc[(df_animals['ganho_por_min'] > 0) & ((df_animals['tipo_ganho'] == 'diamante_diamante') | (df_animals['tipo_ganho'] == 'dinheiro_dinheiro')), 'min_sem_lucro'] = df_animals['custo'] / df_animals['ganho_base']

    return df_animals









if __name__ == '__main__':
    main()