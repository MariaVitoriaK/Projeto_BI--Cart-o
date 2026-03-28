import pandas as pd
import glob
from sqlalchemy import create_engine

# conexão com banco
engine = create_engine("postgresql://postgres:Melissak12.@localhost/dw_cartao")

print("Testando conexão...")
with engine.connect() as conn:
    print("Conectado com sucesso!")

# =========================
# EXTRACT
# =========================

arquivos = glob.glob("dados/Fatura_*.csv")

df = pd.concat([
    pd.read_csv(arq, sep=";", encoding="utf-8")
    for arq in arquivos
])

print(f"Arquivos carregados: {len(df)} linhas")

# =========================
# TRANSFORM
# =========================

df.columns = df.columns.str.strip()

# DATA
df['Data de Compra'] = pd.to_datetime(df['Data de Compra'], format="%d/%m/%Y")

df['ano'] = df['Data de Compra'].dt.year
df['mes'] = df['Data de Compra'].dt.month
df['dia'] = df['Data de Compra'].dt.day
df['trimestre'] = df['Data de Compra'].dt.quarter
df['dia_semana'] = df['Data de Compra'].dt.day_name()

# VALOR
df['Valor (em R$)'] = (
    df['Valor (em R$)']
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
    .astype(float)
)

# CATEGORIA
df['Categoria'] = df['Categoria'].replace('-', 'Não categorizado')

# PARCELAS
def trata_parcela(x):
    if x == "Única":
        return (1,1)
    elif "/" in str(x):
        a,b = x.split("/")
        return (int(a), int(b))
    return (None, None)

df[['num_parcela','total_parcelas']] = df['Parcela'].apply(lambda x: pd.Series(trata_parcela(x)))

# LIMPEZA
df['Final do Cartão'] = df['Final do Cartão'].astype(str)
df['Nome no Cartão'] = df['Nome no Cartão'].str.strip()
df['Categoria'] = df['Categoria'].str.strip()
df['Descrição'] = df['Descrição'].str.strip()

# =========================
# DIMENSÕES
# =========================

dim_data = df[['Data de Compra','dia','mes','trimestre','ano','dia_semana']].drop_duplicates()
dim_data.columns = ['data','dia','mes','trimestre','ano','dia_semana']
dim_data = dim_data.reset_index(drop=True)
dim_data['id_data'] = dim_data.index + 1

dim_titular = df[['Nome no Cartão','Final do Cartão']].drop_duplicates()
dim_titular.columns = ['nome_titular','final_cartao']
dim_titular = dim_titular.reset_index(drop=True)
dim_titular['id_titular'] = dim_titular.index + 1

dim_categoria = df[['Categoria']].drop_duplicates()
dim_categoria.columns = ['nome_categoria']
dim_categoria = dim_categoria.reset_index(drop=True)  
dim_categoria['id_categoria'] = dim_categoria.index + 1

dim_est = df[['Descrição']].drop_duplicates()
dim_est.columns = ['nome_estabelecimento']
dim_est = dim_est.reset_index(drop=True)
dim_est['id_estabelecimento'] = dim_est.index + 1

# =========================
# LOAD DIMENSÕES (rápido)
# =========================

dim_data.to_sql("dim_data", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
print("dim_data OK")

dim_titular.to_sql("dim_titular", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
print("dim_titular OK")

dim_categoria.to_sql("dim_categoria", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
print("dim_categoria OK")

dim_est.to_sql("dim_estabelecimento", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
print("dim_est OK")

# =========================
# BUSCAR DIMENSÕES
# =========================

dim_data_db = pd.read_sql("SELECT * FROM dim_data", engine)
dim_data_db['data'] = pd.to_datetime(dim_data_db['data'])

dim_titular_db = pd.read_sql("SELECT * FROM dim_titular", engine)
dim_titular_db['final_cartao'] = dim_titular_db['final_cartao'].astype(str)
dim_titular_db['nome_titular'] = dim_titular_db['nome_titular'].str.strip()

dim_categoria_db = pd.read_sql("SELECT * FROM dim_categoria", engine)
dim_est_db = pd.read_sql("SELECT * FROM dim_estabelecimento", engine)

# =========================
# MERGES (FATO)
# =========================

df_fato = df.merge(dim_data_db, left_on='Data de Compra', right_on='data')

df_fato = df_fato.merge(
    dim_titular_db,
    left_on=['Nome no Cartão','Final do Cartão'],
    right_on=['nome_titular','final_cartao']
)

df_fato = df_fato.merge(
    dim_categoria_db,
    left_on='Categoria',
    right_on='nome_categoria'
)

df_fato = df_fato.merge(
    dim_est_db,
    left_on='Descrição',
    right_on='nome_estabelecimento'
)

print(f"Linhas após joins: {len(df_fato)}")

# =========================
# FATO
# =========================

fato = df_fato[[
    'id_data',
    'id_titular',
    'id_categoria',
    'id_estabelecimento',
    'Valor (em R$)',
    'num_parcela',
    'total_parcelas'
]].copy()

fato.columns = [
    'id_data',
    'id_titular',
    'id_categoria',
    'id_estabelecimento',
    'valor_brl',
    'num_parcela',
    'total_parcelas'
]

fato.drop_duplicates(inplace=True)

print(f"Linhas na fato: {len(fato)}")

# =========================
# LOAD FATO (OTIMIZADO 🚀)
# =========================

fato.to_sql(
    "fato_transacao",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=2000
)

print("fato_transacao OK")
print("ETL finalizado com sucesso 🚀")