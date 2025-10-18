-- =====================================================
-- SCRIPT PARA LIMPIAR USUARIOS - DEJAR SOLO xmiguelastorgax@gmail.com
-- =====================================================

-- IMPORTANTE: Ejecutar desde PuTTY con:
-- mysql -u tienda_user -p tienda_inmobiliaria_prod

-- 1. Primero, verificar qué usuarios vamos a eliminar
SELECT 
    id,
    username,
    email,
    date_joined
FROM auth_user 
WHERE email != 'xmiguelastorgax@gmail.com' OR username != 'xmiguelastorgax@gmail.com';

-- 2. Eliminar credenciales de administrador asociadas a usuarios que se van a eliminar
-- (excepto la de xmiguelastorgax@gmail.com)
DELETE FROM login_admincredentials 
WHERE user_id IN (
    SELECT id FROM auth_user 
    WHERE email != 'xmiguelastorgax@gmail.com' AND username != 'xmiguelastorgax@gmail.com'
);

-- 3. Eliminar usuarios (excepto xmiguelastorgax@gmail.com)
DELETE FROM auth_user 
WHERE email != 'xmiguelastorgax@gmail.com' AND username != 'xmiguelastorgax@gmail.com';

-- 4. Verificar que solo queda el usuario deseado
SELECT 
    id,
    username,
    email,
    is_active,
    is_superuser,
    date_joined
FROM auth_user;

-- 5. Verificar credenciales de administrador
SELECT 
    id,
    user_id,
    email,
    activo,
    two_factor_enabled
FROM login_admincredentials;

-- 6. Resumen final
SELECT 
    'USUARIOS RESTANTES' as tipo,
    COUNT(*) as cantidad
FROM auth_user
UNION ALL
SELECT 
    'CREDENCIALES ADMIN RESTANTES' as tipo,
    COUNT(*) as cantidad
FROM login_admincredentials;
