# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Compradores particulares, cazadores de ofertas y revendedores (*flippers* / *dealers*) que necesitan monitorear en tiempo real la publicación de nuevos artículos en plataformas de segunda mano (Wallapop y Vinted) para comprar antes que nadie.

## Product Purpose

Findly existe para eliminar la necesidad de buscar manualmente de forma repetitiva en múltiples plataformas. Permite configurar filtros precisos (palabras clave, rangos de precio, distancia con geolocalización y condición del producto) y notifica de inmediato a través de Telegram cuando aparece una coincidencia relevante. El éxito significa:
- 0 oportunidades perdidas por retrasos en notificaciones.
- Configuración y gestión centralizada sin fricción desde una interfaz web moderna.
- Acción rápida desde las alertas móviles (ver artículo o dejar de seguir con un solo toque).

## Positioning

A diferencia de las alertas nativas limitadas, lentas o restringidas de cada marketplace, Findly ofrece:
1. **Rastreo multiplataforma unificado** (Wallapop + Vinted en paralelo con mapeo inteligente de estados/condiciones).
2. **Alertas compartidas en tiempo real** enviadas a grupos o canales de Telegram para equipos o compra colaborativa.
3. **Resiliencia anti-bloqueo** sin requerir proxies complejos para usuarios domésticos o self-hosted (Docker).

## Operating Context

- **Entorno de despliegue:** Servidor local / NAS / VPS ejecutándose en Docker o Portainer como servicio desatendido.
- **Canal de consumo inmediato:** Telegram (móvil y escritorio) para recibir las fotos y enlaces al instante.
- **Canal de gestión y control:** Navegador web en escritorio o tablet (dashboard local en puerto 8000).

## Capabilities and Constraints

- **Stack Frontend:** Single Page Application basada en Vue 3 y Tailwind CSS servida directamente por FastAPI sin requerir paso de compilación (*build step* con bundlers).
- **Internacionalización:** Soporte multiidioma dinámico (i18n en ES, EN, FR, IT, PT) adaptado al idioma del navegador del usuario.
- **Filtros avanzados:** Búsqueda por texto, selector no lineal de rango de precios, cálculo de radio por distancia con geocodificación OpenStreetMap (Nominatim) y selector de condición/estado físico.
- **Emparejamiento seguro:** Vinculación de chats/grupos de Telegram mediante código alfanumérico temporal de 5 dígitos (`/link CODE`).
- **Seguridad y permisos:** Contenedor ejecutado bajo usuario sin privilegios (UID 1000) con base de datos SQLite en modo WAL para alta concurrencia.

## Brand Commitments

- **Nombre:** Findly (anteriormente Wallatrack).
- **Identidad visual base:** Paleta basada en tonos verde azulado (*Teal / Deep Cyan* `#006d77`, `#83c5be`, superficie clara `#edf6f9`, texto `#2b2d42`) con tipografía Inter y Material Symbols.
- **Tono de voz:** Directo, ágil, confiable y funcional ("cero ruido, máxima velocidad").

## Evidence on Hand

- Código fuente operativo completo en FastAPI (`web.py`, `database.py`, `scheduler.py`, `wallapop.py`, `vinted.py`, `handlers.py`).
- Plantilla web activa y funcional en `templates/index.html`.
- Activos gráficos e imágenes de demostración en `assets/web_interface.png` y `assets/telegram_notification.png`.

## Product Principles

1. **Velocidad y respuesta táctil:** Cada acción (agregar búsqueda, ajustar slider, guardar configuración) debe responder inmediatamente sin recargas completas.
2. **Claridad sobre adorno:** La información crítica (precio, plataforma, estado, distancia) debe ser escaneable de un vistazo en listas y tablas.
3. **Flujo sin fricción entre Web y Telegram:** Lo que se configura en la web se refleja al instante en el bot, y las acciones en Telegram (como "Dejar de seguir") se sincronizan limpiamente en la base de datos.
4. **Auto-contenido y ligero:** Facilidad extrema de mantenimiento y despliegue; sin dependencias innecesarias en el cliente.
