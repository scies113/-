-- =====================================================================
-- Библиотека SQL-запросов к базе данных системы учета домашних заготовок
-- База данных: data/preserves.sqlite
-- СУБД: SQLite 3
-- =====================================================================

-- 1. SELECT / WHERE: Выборка всех активных партий в погребе (в наличии)
SELECT
    b.id,
    b.preserve_id,
    p.name AS preserve_name,
    b.production_date,
    b.quantity,
    b.is_consumed
FROM batches b
JOIN preserves p ON b.preserve_id = p.id
WHERE b.is_consumed = 0
ORDER BY b.production_date DESC;

-- 2. JOIN: Детальная карточка конкретной партии со связанной заготовкой и сырьем
SELECT
    b.id AS batch_id,
    b.production_date,
    b.quantity,
    b.is_consumed,
    p.id AS preserve_id,
    p.name AS preserve_name,
    p.recipe_notes,
    pr.id AS product_id,
    pr.name AS product_name,
    pr.category AS product_category
FROM batches b
JOIN preserves p ON b.preserve_id = p.id
JOIN products pr ON p.product_id = pr.id
WHERE b.id = 1;

-- 3. Агрегация (SUM / COUNT): Подсчет общего количества банок и партий в наличии
SELECT
    COUNT(b.id) AS active_batches_count,
    COALESCE(SUM(b.quantity), 0) AS total_jars_in_cellar
FROM batches b
WHERE b.is_consumed = 0;

-- 4. GROUP BY: Группировка запасов по видам заготовок (число партий и банок)
SELECT
    p.id AS preserve_id,
    p.name AS preserve_name,
    COUNT(b.id) AS batches_count,
    COALESCE(SUM(b.quantity), 0) AS total_quantity
FROM preserves p
LEFT JOIN batches b ON p.id = b.preserve_id
GROUP BY p.id, p.name
ORDER BY total_quantity DESC;

-- 5. HAVING: Поиск рецептов заготовок, по которым сделано более 2 партий
SELECT
    p.id AS preserve_id,
    p.name AS preserve_name,
    COUNT(b.id) AS batches_count,
    SUM(b.quantity) AS total_quantity
FROM preserves p
JOIN batches b ON p.id = b.preserve_id
GROUP BY p.id, p.name
HAVING COUNT(b.id) > 2;

-- 6. Подзапрос (NOT IN): Рецепты, по которым в данный момент нет активных партий в погребе
SELECT
    p.id,
    p.name,
    p.recipe_notes
FROM preserves p
WHERE p.id NOT IN (
    SELECT DISTINCT b.preserve_id
    FROM batches b
    WHERE b.is_consumed = 0
);

-- 7. JOIN: Полный каталог заготовок с наименованием и категорией базового сырья
SELECT
    p.id,
    p.name,
    p.recipe_notes,
    pr.id AS product_id,
    pr.name AS product_name,
    pr.category AS product_category
FROM preserves p
JOIN products pr ON p.product_id = pr.id
ORDER BY p.name ASC;

-- 8. LEFT JOIN + GROUP BY: Справочник продуктов с подсчетом связанных рецептов
SELECT
    pr.id,
    pr.name,
    pr.category,
    COUNT(p.id) AS recipes_count
FROM products pr
LEFT JOIN preserves p ON pr.id = p.product_id
GROUP BY pr.id, pr.name, pr.category
ORDER BY pr.id ASC;

-- 9. Параметризованный поиск: Фильтрация партий по точной дате производства и статусу
SELECT
    b.id,
    b.preserve_id,
    p.name AS preserve_name,
    b.production_date,
    b.quantity,
    b.is_consumed
FROM batches b
JOIN preserves p ON b.preserve_id = p.id
WHERE (b.production_date = '2026-09-10' OR '2026-09-10' = '')
  AND (b.is_consumed = 0)
ORDER BY b.id ASC;

-- 10. SELECT / WHERE: Выборка израсходованных партий для анализа истории расхода
SELECT
    b.id,
    p.name AS preserve_name,
    b.production_date,
    b.quantity,
    b.is_consumed
FROM batches b
JOIN preserves p ON b.preserve_id = p.id
WHERE b.is_consumed = 1
ORDER BY b.production_date DESC;

-- 11. JOIN + WHERE: Выборка заготовок по определенной категории сырья (овощи)
SELECT
    p.id AS preserve_id,
    p.name AS preserve_name,
    pr.name AS product_name,
    pr.category
FROM preserves p
JOIN products pr ON p.product_id = pr.id
WHERE pr.category = 'овощи';

-- 12. ORDER BY + LIMIT: Топ-3 самых запасаемых заготовок по общему числу банок
SELECT
    p.name AS preserve_name,
    COALESCE(SUM(b.quantity), 0) AS total_jars
FROM preserves p
JOIN batches b ON p.id = b.preserve_id
GROUP BY p.id, p.name
ORDER BY total_jars DESC
LIMIT 3;
