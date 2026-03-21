import pandas as pd

df_estoque = pd.read_csv('PlanilhaUNCLEK_226999_GERENTE226_0137.csv')

estoque = df_estoque.groupby(["Produto", "Cod. Produto", "Ds. Cor", "Ds. Tam", "Empresa"]).agg({"Saldo Físico Loja": "sum","Pecas Venda Liq": "sum"}).reset_index()

estoque_tab = estoque.pivot_table(
    index=["Produto", "Cod. Produto", "Ds. Cor", "Ds. Tam"],
    columns="Empresa",
    values="Saldo Físico Loja",
    fill_value=0
)

vendas_tab = estoque.pivot_table(
    index=["Produto", "Cod. Produto", "Ds. Cor", "Ds. Tam"],
    columns="Empresa",
    values="Pecas Venda Liq",
    fill_value=0
)
estoque_tab.to_csv("tabela_estoque_por_loja.csv")

tem_baixo = (estoque_tab <= 1).any(axis=1)
tem_alto = (estoque_tab > 2).any(axis=1)

problemas = estoque_tab[tem_baixo & tem_alto]

problemas.to_csv("modelos_com_problema.csv")

transferencias = []

transferencias = []

for produto in problemas.index:
    linha_estoque = estoque_tab.loc[produto].copy()
    linha_vendas = vendas_tab.loc[produto]

    lojas_falta = linha_estoque[linha_estoque <= 1]

    while True:
        lojas_sobra = linha_estoque[linha_estoque > 2]

        if lojas_sobra.empty or lojas_falta.empty:
            break

        candidatos = pd.DataFrame({
            "estoque": linha_estoque[lojas_sobra.index],
            "vendas": linha_vendas[lojas_sobra.index]
        })

        candidatos = candidatos.sort_values(
            by=["estoque", "vendas"],
            ascending=[False, True]  
        )

        loja_origem = candidatos.index[0]
        loja_destino = lojas_falta.index[0]

        estoque_origem = linha_estoque[loja_origem]

        qtd = max(1, int(estoque_origem // 2))

        transferencias.append({
            "Produto": produto,
            "De": loja_origem,
            "Para": loja_destino,
            "Quantidade": qtd
        })

        linha_estoque[loja_origem] -= qtd
        linha_estoque[loja_destino] += qtd

        lojas_falta = linha_estoque[linha_estoque <= 1]

df_transferencias = pd.DataFrame(transferencias)
df_transferencias.to_csv("transferencias.csv", index=False)