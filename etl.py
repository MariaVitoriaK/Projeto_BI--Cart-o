import pandas as pd
import glob
from sqlalchemy import create_engine

# conexão com banco
engine = create_engine("postgresql://usuario:senha@localhost:5432/dw_cartao")

arquivos = glob.glob("dados/Fatura_*.csv")

df_total = []

for arquivo in arquivos:
    df = pd.read_csv(arquivo, sep=";", encoding="utf-8")
    df_total.append(df)

df = pd.concat(df_total)

# =========================
# TRANSFORMAÇÕES
# =========================

# data
df['Data de Compra'] = pd.to_datetime(df['Data de Compra'], format="%d/%m/%Y")

df['ano'] = df['Data de Compra'].dt.year
df['mes'] = df['Data de Compra'].dt.month
df['dia'] = df['Data de Compra'].dt.day
df['trimestre'] = df['Data de Compra'].dt.quarter
df['dia_semana'] = df['Data de Compra'].dt.day_name()

# valores
df['Valor (em R$)'] = df['Valor (em R$)'].replace(',', '.', regex=True).astype(float)

# categoria
df['Categoria'] = df['Categoria'].replace('-', 'Não categorizado')

# parcelas
def trata_parcela(x):
    if x == "Única":
        return (1,1)
    elif "/" in str(x):
        a,b = x.split("/")
        return (int(a), int(b))
    return (None, None)

df[['num_parcela','total_parcelas']] = df['Parcela'].apply(lambda x: pd.Series(trata_parcela(x)))

# =========================
# LOAD DIMENSÕES
# =========================

dim_data = df[['Data de Compra','dia','mes','trimestre','ano','dia_semana']].drop_duplicates()
dim_data.columns = ['data','dia','mes','trimestre','ano','dia_semana']
dim_data.to_sql("dim_data", engine, if_exists="append", index=False)

dim_titular = df[['Nome no Cartão','Final do Cartão']].drop_duplicates()
dim_titular.columns = ['nome_titular','final_cartao']
dim_titular.to_sql("dim_titular", engine, if_exists="append", index=False)

dim_categoria = df[['Categoria']].drop_duplicates()
dim_categoria.columns = ['nome_categoria']
dim_categoria.to_sql("dim_categoria", engine, if_exists="append", index=False)

dim_est = df[['Descrição']].drop_duplicates()
dim_est.columns = ['nome_estabelecimento']
dim_est.to_sql("dim_estabelecimento", engine, if_exists="append", index=False)