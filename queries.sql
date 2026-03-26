-- 1. Gasto total por titular

SELECT t.nome_titular, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_titular t ON f.id_titular = t.id_titular
GROUP BY t.nome_titular
ORDER BY total DESC;

-- 2. Top 10 categorias

SELECT c.nome_categoria, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_categoria c ON f.id_categoria = c.id_categoria
GROUP BY c.nome_categoria
ORDER BY total DESC
LIMIT 10;

-- 3. Evolução mensal

SELECT d.ano, d.mes, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_data d ON f.id_data = d.id_data
GROUP BY d.ano, d.mes
ORDER BY d.ano, d.mes;

-- 4. Compras parceladas vs à vista

SELECT 
    CASE 
        WHEN total_parcelas > 1 THEN 'Parcelado'
        ELSE 'À vista'
    END AS tipo,
    COUNT(*) 
FROM fato_transacao
GROUP BY tipo;

-- 5. Top estabelecimentos

SELECT e.nome_estabelecimento, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_estabelecimento e ON f.id_estabelecimento = e.id_estabelecimento
GROUP BY e.nome_estabelecimento
ORDER BY total DESC
LIMIT 10;