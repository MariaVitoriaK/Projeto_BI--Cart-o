CREATE TABLE fato_transacao (
    id SERIAL PRIMARY KEY,
    id_data INT,
    id_titular INT,
    id_categoria INT,
    id_estabelecimento INT,
    valor_brl NUMERIC(10,2),
    valor_usd NUMERIC(10,2),
    cotacao NUMERIC(10,4),
    parcela_texto VARCHAR(20),
    num_parcela INT,
    total_parcelas INT
);

CREATE TABLE dim_data (
    id_data SERIAL PRIMARY KEY,
    data DATE,
    dia INT,
    mes INT,
    trimestre INT,
    ano INT,
    dia_semana VARCHAR(20)
);

CREATE TABLE dim_titular (
    id_titular SERIAL PRIMARY KEY,
    nome_titular VARCHAR(100),
    final_cartao VARCHAR(4)
);

CREATE TABLE dim_categoria (
    id_categoria SERIAL PRIMARY KEY,
    nome_categoria VARCHAR(100)
);

CREATE TABLE dim_estabelecimento (
    id_estabelecimento SERIAL PRIMARY KEY,
    nome_estabelecimento VARCHAR(200)
);


TRUNCATE dim_data RESTART IDENTITY;
TRUNCATE dim_titular RESTART IDENTITY;
TRUNCATE dim_categoria RESTART IDENTITY;
TRUNCATE dim_estabelecimento RESTART IDENTITY;
TRUNCATE fato_transacao RESTART IDENTITY;