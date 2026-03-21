import pandas as pd

df_estoque = pd.read_csv('UNCLEK_226999_GERENTE226_0043.csv')

estoque = df_estoque.groupby(["Modelo", "Loja"])["Saldo em Estoque"].sum().reset_index()

tabela = estoque.pivot(index="Modelo", columns="Loja", values="Saldo em Estoque").fillna(0)
tabela.to_csv("tabela_estoque_por_loja.csv")

tem_zero = (tabela == 0).any(axis=1)
tem_estoque = (tabela > 0).any(axis=1)
problemas = tabela[tem_zero & tem_estoque]

problemas.to_csv("modelos_com_problema.csv")

transferencias = []

for modelo in problemas.index:
    linha = problemas.loc[modelo] 
    
    loja_max = linha.idxmax()
    loja_min = linha.idxmin()
    estoque_max = linha.max()
    
    if estoque_max > 1:
        transferencias.append({
            "Modelo": modelo,
            "De": loja_max,
            "Para": loja_min,
            "Quantidade": 1
        })

df_transferencias = pd.DataFrame(transferencias)
df_transferencias.to_csv("transferencias.csv", index=False)