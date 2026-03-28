-- 1. Gasto total por mês titular
SELECT d.ano, d.mes, SUM(f.valor_brl) AS total_gasto
FROM fato_transacao f
JOIN dim_data d ON f.id_data = d.id_data
GROUP BY d.ano, d.mes
ORDER BY d.ano, d.mes;

-- 2. Meses com maiores gastos
SELECT d.ano, d.mes, SUM(f.valor_brl) AS total_gasto
FROM fato_transacao f
JOIN dim_data d ON f.id_data = d.id_data
GROUP BY d.ano, d.mes
ORDER BY total_gasto DESC;

-- 3. Titular que mais gasta
SELECT t.nome_titular, SUM(f.valor_brl) AS total_gasto
FROM fato_transacao f
JOIN dim_titular t ON f.id_titular = t.id_titular
GROUP BY t.nome_titular
ORDER BY total_gasto DESC;


-- 4. Gastos por categoria
SELECT c.nome_categoria, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_categoria c ON f.id_categoria = c.id_categoria
GROUP BY c.nome_categoria
ORDER BY total DESC;

-- 5. Top estabelecimentos
SELECT e.nome_estabelecimento, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_estabelecimento e ON f.id_estabelecimento = e.id_estabelecimento
GROUP BY e.nome_estabelecimento
ORDER BY total DESC
LIMIT 10;

-- 6. Dia da semana com mais gastos
SELECT d.dia_semana, SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_data d ON f.id_data = d.id_data
GROUP BY d.dia_semana
ORDER BY total DESC;

-- 7. Parcelado vs à vista
SELECT 
    CASE 
        WHEN f.total_parcelas > 1 THEN 'Parcelado'
        ELSE 'À vista'
    END AS tipo_compra,
    COUNT(*) AS quantidade,
    SUM(f.valor_brl) AS total_gasto
FROM fato_transacao f
GROUP BY tipo_compra;

-- 8. Ticket médio (valor médio por transação)
SELECT AVG(valor_brl) AS ticket_medio
FROM fato_transacao;

-- 9. Total de estornos (valores negativos)
SELECT SUM(valor_brl) AS total_estornos
FROM fato_transacao
WHERE valor_brl < 0;

-- 10. Evolução de gastos por titular
SELECT 
    t.nome_titular,
    d.ano,
    d.mes,
    SUM(f.valor_brl) AS total
FROM fato_transacao f
JOIN dim_titular t ON f.id_titular = t.id_titular
JOIN dim_data d ON f.id_data = d.id_data
GROUP BY t.nome_titular, d.ano, d.mes
ORDER BY t.nome_titular, d.ano, d.mes;
