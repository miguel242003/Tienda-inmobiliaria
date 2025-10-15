-- Verificar clics por propiedad
SELECT 
    p.id,
    p.titulo,
    COUNT(cp.id) as total_clicks
FROM propiedades_propiedad p
LEFT JOIN propiedades_clickpropiedad cp ON p.id = cp.propiedad_id
GROUP BY p.id, p.titulo
ORDER BY total_clicks DESC;

-- Verificar total de clics
SELECT COUNT(*) as total_clicks FROM propiedades_clickpropiedad;

-- Ver clics recientes
SELECT * FROM propiedades_clickpropiedad ORDER BY fecha_click DESC LIMIT 10;