# STINE Semillas Argentina — Brand Identity & SEO Audit

**Dominio analizado:** https://www.stinesemillas.com.ar  
**Fecha de análisis:** 11 de junio de 2026  
**Páginas visitadas:** Homepage, Catálogo Soja, Catálogo Maíz, Hay Equipo, La Rompemos, Stiners, Tecnología Enlist, Programa I+D, Blog, Contacto, Myron Stine

---

## A. Identidad Visual

### A.1 — Paleta de Colores

> **Nota:** No se encontraron variables CSS declaradas públicamente ni hojas de estilo accesibles vía CDN. Los valores siguientes son inferidos del HTML/SVG visibles y del sistema de diseño observado.

| Rol | Color | HEX estimado | Observaciones |
|---|---|---|---|
| Primario fondo | Blanco | `#FFFFFF` | Fondo general del sitio |
| Primario texto | Negro | `#000000` / `#111111` | Headlines y body copy |
| Acento principal | Rojo/Naranja STINE | `#E63312` aprox. | Botones primarios, CTAs, destacados |
| Secundario | Amarillo maíz | `#F5C400` aprox. | Elementos de producto maíz |
| Neutro oscuro | Gris carbón | `#222222` | Fondos de sección alternados |
| Texto sobre oscuro | Blanco puro | `#FFFFFF` | Copy sobre fondos negros |

**Clasificación:**
- **Primarios:** Blanco (#FFF), Negro (#111), Rojo (#E63312)
- **Secundarios:** Amarillo (#F5C400), Gris oscuro (#222)
- **Acento/hover:** Rojo más oscuro (estimado `#C42B0E`)

### A.2 — Tipografías

| Uso | Familia inferida | Peso | Tamaño estimado |
|---|---|---|---|
| H1 / Headlines | Sans-serif bold condensed (estilo industrial — posiblemente **Barlow Condensed** o **Oswald**) | 800–900 (ExtraBold/Black) | 48–80px |
| H2 | Misma familia | 700 | 28–40px |
| H3 | Misma familia | 600–700 | 20–28px |
| Body / párrafos | Sans-serif regular (posiblemente **Inter** o **Roboto**) | 400 | 15–17px |
| CTAs / Botones | Misma que headlines, uppercase | 700–800 | 14–16px |
| Caption / Ficha técnica | Sans-serif light | 300–400 | 12–13px |

> No se detectaron declaraciones `@font-face` ni links a Google Fonts en el HTML accesible. Para confirmar familias exactas se requiere inspección DevTools del CSS compilado.

### A.3 — Logo

- **Nombre/forma:** Logotipo tipográfico "STINE" en mayúsculas, acompañado del descriptor "Semillas Argentina" en peso menor.
- **Archivo:** `StineWEB.svg` (formato vectorial)
- **Variantes detectadas:** Al menos una variante principal (horizontal). No se observaron variantes ícono-solo o vertical en el HTML analizado.
- **Colores del logo:** Versión sobre fondo blanco (colores plenos); versión sobre fondos oscuros (presumiblemente blanco). Sin confirmación de variante negativa o monocromática en el sitio.

### A.4 — Iconografía y Recursos Gráficos

- **Fotografías:** Predominan imágenes de campo (cultivos de soja y maíz), productores, maquinaria agrícola y eventos. Tratamiento de color con alto contraste y saturación — estética energética, no editorial.
- **Íconos:** No se detectaron librerías de íconos estándar (Font Awesome, Heroicons). Los íconos usados parecen ser SVG propios, de trazo simple (line style).
- **Recursos Instagram:** El homepage embebe posts/reels de Instagram directamente como galería, lo que funciona como contenido visual dinámico.
- **Imágenes de producto:** Las fichas de variedades (soja y maíz) usan imágenes con nombre de código (ej. `25EB32-back`, `9937-back`) — lo que sugiere un sistema de naming interno pero no SEO-friendly.

### A.5 — Espaciado y Layout

- **Grid:** Layout de columnas amplias, secciones a full-width con bloques de color alternados (blanco ↔ negro).
- **Densidad visual:** Alta — secciones cargadas de CTAs, testimonios, catálogos, feed de Instagram. Estética más "landing page de impacto" que minimalista.
- **Márgenes:** Generosos entre secciones (padding vertical ~80–120px estimado), compensando la densidad de cada bloque.

---

## B. Tono de Voz y Copywriting

### B.1 — Tono General

**Informal, directo, provocador y aspiracional.** El sitio habla de tú al productor, usa jerga argentina coloquial ("¡Te vas a sorprender!", "acordate lo que te digo", "la rompemos"), y combina ese registro con datos técnicos duros (patentes, ensayos, porcentajes de mercado). El resultado es un tono **confiante hasta el límite de lo jactancioso**, pensado para diferenciarse de comunicaciones agrícolas convencionales más solemnes.

### B.2 — Persona de Marca

STINE se presenta como el **disruptor experto**: una empresa global (líder mundial) que irrumpió en Argentina con actitud de challenger local. No es una marca corporativa distante — habla como un aliado del campo con credenciales globales. La combinación de "somos los mejores del mundo" + "estamos acá con vos" es el núcleo de su persona de marca.

### B.3 — Frases Representativas

| Tipo | Copy |
|---|---|
| H1 homepage | "NO ES SUERTE, ES STINE" |
| Subhéadline hero | "Si estás acá, es porque ya te diste cuenta." |
| Claim producto | "STINE tiene rinde. Tu campo también." |
| Catálogo soja | "NOS SEMBRASTE SIN SABERLO, ¡AHORA SEMBRANOS SABIÉNDOLO!" |
| Catálogo maíz | "MAÍCES STINE: LOS COMPRÁS, LOS SEMBRÁS Y ¡TE SORPRENDÉS!" |
| Institucional | "¡ALGUNOS LOCOS VIEJITOS, MUY EXPERIMENTADOS, ACOMPAÑADOS POR UN EQUIPO DE JÓVENES CON TODA LA GARRA!" |
| Programa I+D | "EL PROGRAMA DE MEJORAMIENTO GENÉTICO EN SOJA MÁS GRANDE DEL MUNDO" |
| Contacto H1 | "HOLA. HELLO. ¿CÓMO VA ESO?, ¿QUÉ ONDA? ESTAMOS PARA LO QUE NECESITES." |

### B.4 — Taglines y Claims

| Claim | Contexto de uso |
|---|---|
| "El Semillero Privado #1 del Mundo" | Header/footer |
| "NO ES SUERTE, ES STINE" | H1 homepage — tagline principal |
| "COLOR RINDE" | Asociado al portafolio (sin explicación en contexto) |
| "SEMBRÁ EVOLUCIÓN" | Programa Enlist / nueva comercialización |
| "Sin barreras. Con innovación. Un portfolio diseñado para ganar." | Catálogo 2026 |
| "50% de la soja global tiene genética STINE" | Página La Rompemos |

### B.5 — Terminología Propia

| Término | Significado |
|---|---|
| **Stiners** | Red de distribuidores/asesores comerciales de STINE |
| **Sembrá Evolución** | Nombre del programa comercial con tecnología Enlist |
| **COLOR RINDE** | Concepto/campaña vinculado al portfolio (no definido explícitamente) |
| **Programa I+D** | Programa de mejoramiento genético global de Harry/Myron Stine |
| **Tecnología Enlist E3** | Tecnología de triple resistencia herbicida (Corteva) en soja |
| **Hectárea Tecnológica** | Unidad de venta/royalty del programa Enlist ($24–$28 USD/ha) |
| **Team Stine** | Denominación interna del equipo y red comercial |

---

## C. Arquitectura de Contenidos

### C.1 — Estructura de Navegación

```
¿POR QUÉ STINE?
  ├── HAY EQUIPO
  └── LA ROMPEMOS

SOJA
  ├── CATÁLOGO SOJA
  └── SEMBRÁ EVOLUCIÓN + ENLIST

MAÍZ
  └── CATÁLOGO MAÍZ

RED COMERCIAL (→ /stiners/)

CONTACTO
```

**Páginas fuera del menú principal** (detectadas vía sitemap):
- /blog/ — Blog/Noticias (sin entrada visible en el menú)
- /programa-id/ — Programa I+D
- /myron-stine/ — Artículo institucional
- /ensayos/* — 16 páginas de ensayos de rendimiento
- /shop-maiz/, /shop-semillas-soja/, /shop-merch/ — E-commerce
- /sumate-al-team-stine/ — Empleo
- /nuestros-partners/ — Partners

### C.2 — Jerarquía de Mensajes

1. **Primero:** Identidad de marca y promesa de rinde ("No es suerte, es Stine" — H1 homepage)
2. **Segundo:** Prueba de liderazgo global (50% soja mundial, 900+ patentes, 200k variedades testeadas)
3. **Tercero:** Portafolio de productos (soja + maíz con tecnología Enlist)
4. **Cuarto:** Red comercial local (Stiners — "encontrá tu Stiner")
5. **Quinto:** Equipo y cultura ("Hay Equipo", "Sumate al Team Stine")

### C.3 — CTAs Únicos Identificados

| CTA | Página(s) |
|---|---|
| ENCONTRÁ TU STINER | Todas (footer + homepage) |
| UNITE AL TEAM STINE | Todas (footer) |
| DESCARGAR CATÁLOGO SOJA | Soja, Enlist |
| DESCARGAR CATÁLOGO MAÍZ | Maíz |
| DESCARGAR FICHA (variedad) | Catálogos |
| CONOCÉ MÁS / CONOCELO ACÁ | Homepage, Enlist |
| COMPROBALO ACÁ | Homepage |
| MIRALO ACÁ | Homepage |
| LEER MÁS | Blog |
| Ver bases y condiciones | Homepage (promo maíz) |
| PRECERTIFICÁ TU HECTÁREA TECNOLÓGICA | Enlist |
| Envianos tu CV acá | Hay Equipo, Stiners |
| ¡Contactanos! | Varias |

### C.4 — Segmentos de Audiencia Detectados

| Segmento | Señales en el sitio |
|---|---|
| **Productor agropecuario** | Tono directo "tu campo", focus en rinde, testimonios de productores en catálogo maíz |
| **Distribuidor / revendedor** | Sección Stiners, "contactanos si querés ser parte" |
| **Agrónomo / asesor técnico** | Ensayos técnicos (/ensayos/*), fichas de variedad descargables |
| **Profesional de RRHH** | Sección empleo, "envianos tu CV" |
| **Proveedor** | Email compras@stineseed.com en footer |

---

## D. Identidad de Marca Percibida

### D.1 — Valores Implícitos

| Valor | Señal en el sitio |
|---|---|
| **Rendimiento como religión** | "No es suerte, es Stine" — el rinde es mérito, no azar |
| **Ambición sin complejos** | "Vinimos a competir por el liderazgo" |
| **Ciencia al servicio del campo** | 200.000 variedades evaluadas, 900+ patentes |
| **Cercanía y confianza** | Tono coloquial, red Stiners "presencia en toda la región" |
| **Orgullo de origen** | Conexión explícita con la historia familiar (Harry/Myron Stine desde 1950) |

### D.2 — Diferenciadores Comunicados

- Única compañía privada de semillas más grande de EE.UU. (cuarta global)
- 50% de la soja global con genética Stine
- Programa de mejoramiento propio (no licenciatario)
- Tecnología Enlist E3 de triple resistencia herbicida
- Red comercial local (Stiners) con "asesoramiento 360"
- Fundación familiar, no corporativa multinacional anónima

### D.3 — Mood General

**Confiante · Disruptivo · Energético · Campero-global · Directo**

---

## E. Auditoría SEO

### E.1 — Meta y Estructura Técnica por Página

| Página | Title Tag | Chars | Meta Description | Canonical | Robots |
|---|---|---|---|---|---|
| Homepage | "STINE Semillas Argentina - El Semillero Privado #1 del Mundo" | ~61 | **No detectada** | No detectada | No detectada |
| Hay Equipo | "HAY EQUIPO - STINE Semillas Argentina" | ~38 | **No detectada** | No detectada | No detectada |
| La Rompemos | "LA ROMPEMOS - STINE Semillas Argentina" | ~39 | **No detectada** | No detectada | No detectada |
| Myron Stine | "Myron Stine: "Vinimos a competir por el liderazgo". - STINE Semillas Argentina" | ~78 | **No detectada** | No detectada | No detectada |
| Programa I+D | "PROGRAMA I+D - STINE Semillas Argentina" | ~40 | **No detectada** | No detectada | No detectada |
| Catálogo Soja | No detectada | — | **No detectada** | No detectada | No detectada |
| Catálogo Maíz | No detectada | — | **No detectada** | No detectada | No detectada |
| Blog | No detectada | — | **No detectada** | No detectada | No detectada |
| Contacto | No detectada | — | **No detectada** | No detectada | No detectada |

**Observaciones críticas:**
- **Cero meta descriptions detectadas** en todo el sitio — Google generará snippets automáticos, sin control editorial.
- Title tags detectados siguen patrón `[NOMBRE PÁGINA] - STINE Semillas Argentina`, lo cual es correcto en estructura pero carece de keywords primarias de producto en la mayoría de páginas.
- El title de la homepage (61 chars) está dentro del rango óptimo (50–60 chars, aunque 61 está al límite).
- No se detectaron tags hreflang (correcto si el sitio es solo en español).
- No se detectaron Open Graph tags, lo que impacta cómo se ve el sitio al compartir en redes.
- **Robots.txt:** El archivo `/robots.txt` devolvió HTTP 404 — **no existe**. Esto es un gap técnico.
- **Sitemap XML:** Existe en `/sitemap.xml` (sin www) con 56 URLs. No se encontró en `/sitemap.xml` con www.

---

### E.2 — Árbol de Encabezados por Página

#### Homepage
```
H1: NO ES SUERTE, ES STINE
  H2: Con la compra de maíz stine, tu semilla está cubierta ante eventos climáticos adversos
  H2: SEMBRÁ EVOLUCIÓN
  H2: ¿Buscabas Rinde? Estás en el lugar indicado
  H2: ROMPIENDO BARRERAS: ¡DESCUBRÍ NUESTRO CATÁLOGO 2026!
  H2: MAÍCES STINE: ¡TE VAS A SORPRENDER, ACORDATE LO QUE TE DIGO!
```
✅ Un solo H1. ⚠️ H1 no contiene keywords de producto (soja, maíz, semillas).

#### Catálogo Soja
```
H1: NOS SEMBRASTE SIN SABERLO, ¡AHORA SEMBRANOS SABIÉNDOLO!  (aparece 2 veces)
  H2: EL LÍDER GLOBAL, ¡AHORA EN TU CAMPO!
```
❌ H1 duplicado en la página. ❌ H1 sin keywords (variedades, soja, semillas).

#### Catálogo Maíz
```
H1: MAÍCES STINE: LOS COMPRÁS, LOS SEMBRÁS Y ¡TE SORPRENDÉS! (aparece 2 veces)
  H2: SI LOS PROBÁS, TE VAS A SORPRENDER.
  H3: [nombres de productores testimoniales]
```
❌ H1 duplicado. ✅ H1 contiene "MAÍCES" — keyword relevante.

#### Hay Equipo
```
H1: ¡ALGUNOS LOCOS VIEJITOS, MUY EXPERIMENTADOS, ACOMPAÑADOS POR UN EQUIPO DE JÓVENES CON TODA LA GARRA!
  H2: SOMOS STINE ARGENTINA.
  H2: 300% ENFOCADOS.
  H2: [nombres de directivos]
  H3: [nombres de equipo comercial]
```
✅ Un solo H1. ❌ H1 sin keywords institucionales.

#### La Rompemos
```
H1: NOS SEMBRASTE SIN SABERLO, ¡AHORA SEMBRANOS SABIÉNDOLO! ES HORA DE STINE.
  H2: UN DESAFÍO. UN COMPROMISO.
  H2: LA TENDENCIA, SON LOS DATOS.
  H2: OTROS HITOS IMPORTANTES.
  H2: EL LÍDER INDISCUTIDO DE SOJA A ESCALA GLOBAL ES STINE.
```
✅ Un solo H1. ❌ H1 sin keywords relevantes para SEO.

#### Stiners (Red Comercial)
```
H1: RED COMERCIAL STINE SEMILLAS
  H2: ¿Qué hacemos?
  H2: ENCONTRÁ A TU STINER MÁS CERCANO
  H2: UNA RED CON RINDE
  H2: MANIFIESTO DE STINERS
  H2: EQUIPO COMERCIAL
  H3: [descriptores de servicio]
```
✅ H1 contiene keywords (red comercial, semillas). ✅ Estructura coherente.

#### Programa I+D
```
H1: EL PROGRAMA DE MEJORAMIENTO GENÉTICO EN SOJA MÁS GRANDE DEL MUNDO
  H2: ELEGIMOS SÓLO A LOS GANADORES
  H2: HARRY STINE
```
✅ Excelente H1 — contiene "mejoramiento genético", "soja". ✅ Único H1.

---

### E.3 — Contenido y Keywords

#### Top 15 términos más frecuentes (inferidos del corpus analizado)

| Término / Frase | Frecuencia estimada | Tipo |
|---|---|---|
| soja | Muy alta | Producto principal |
| maíz | Muy alta | Producto principal |
| stine / stines | Muy alta | Marca |
| rinde | Alta | Diferenciador clave |
| semillas | Alta | Categoría |
| variedades | Alta | Categoría |
| catálogo | Media-alta | Navegación/contenido |
| stiners | Media | Término propio |
| enlist | Media | Tecnología |
| rendimiento | Media | Beneficio |
| Argentina | Media | Geo |
| equipo | Media | Institucional |
| genética | Media | Técnico |
| productor(es) | Media | Audiencia |
| tecnología | Media | Diferenciador |

#### Keywords objetivo implícitas
- semillas de soja Argentina
- variedades de soja de alto rendimiento
- híbridos de maíz Argentina
- semillero privado Argentina
- tecnología Enlist soja
- mejoramiento genético soja
- semillas soja Venado Tuerto

#### Páginas con contenido thin (< 300 palabras sustantivas)
- /catalogo-soja/ — ~150–200 palabras (principalmente lista de códigos de variedad)
- /catalogo-maiz/ — ~250–300 palabras
- /blog/ — 3 posts visibles, ~350 palabras totales en previews
- /contacto/ — información de contacto sin copy editorial
- /form_gracias/ — página de confirmación (probablemente < 50 palabras)

#### Idioma
El sitio está en **español argentino** predominantemente. Se detectan términos en inglés sin traducción (Enlist, Enlist E3, LibertyLink, Roundup Ready) que son nombres de tecnología/marca — aceptable. El H1 del contacto incluye "HELLO" de forma intencional y estilística.

---

### E.4 — Imágenes

| Hallazgo | Detalle |
|---|---|
| **Alt text ausente** | La mayoría de imágenes de producto y campo carecen de alt text descriptivo. Solo se detectó "StineWEB" y "STINE-PIE-DISTRIBUIDORES" como alt texts presentes. |
| **Nombres de archivo** | Usan códigos internos (`25EB32-back`, `9937-back`, `9942 T Stine portada cultivos MAIZ_MAPA`) — parcialmente descriptivos pero no optimizados para SEO. |
| **Formato** | El logo usa SVG (correcto). Las imágenes de producto parecen JPG. No se confirmó uso de WebP. |
| **Lazy loading** | No confirmado. El feed de Instagram embebido puede ser pesado en carga inicial. |
| **Feed Instagram embebido** | Las imágenes del homepage provienen de URLs de Instagram — sin control sobre alt text ni formato. |

---

### E.5 — Links

#### Links internos
El sitio tiene interlinking básico via footer (catálogos, Stiners, Team Stine) y CTAs en secciones. No se detectó interlinking editorial entre páginas de ensayos, fichas de variedad y catálogos — oportunidad perdida.

#### Links externos detectados
| Dominio | Propósito |
|---|---|
| instagram.com/stinesemillas | Red social (múltiples links al feed embebido) |
| twitter.com/stinesemillas | Red social |
| linkedin.com/company/stinesemillas | Red social |
| youtube.com/channel/UCPGjO... | Canal YouTube |
| facebook.com/stinesemillas | Red social |
| tiktok.com/@stine.semillas | Red social |
| docs.google.com | Bases y condiciones (Google Doc) |

⚠️ El enlace a Google Docs para "bases y condiciones" es un link externo a contenido no controlado — riesgo de desaparición y mala experiencia.

#### Links rotos / problemáticos
- El archivo de robots.txt en `https://www.stinesemillas.com.ar/robots.txt` devuelve **404** — no existe.
- Links al sitemap usan URL sin www (`stinesemillas.com.ar`) mientras el sitio canónico usa www — posible inconsistencia de dominio.

---

### E.6 — Datos Estructurados (Schema Markup)

**No se detectó ningún schema markup (JSON-LD)** en ninguna de las páginas analizadas.

#### Schemas recomendados por tipo de página

| Página | Schema recomendado |
|---|---|
| Homepage | `Organization`, `WebSite` (con SearchAction) |
| Catálogo Soja / Maíz | `Product`, `ItemList` |
| Fichas de variedad individuales | `Product` (con name, description, offers) |
| Hay Equipo / Institucional | `AboutPage`, `Person` (para directivos) |
| Blog posts | `Article`, `BlogPosting` |
| Contacto | `ContactPage`, `LocalBusiness` |
| Stiners / Red Comercial | `LocalBusiness` (múltiples), `Service` |
| Ensayos | `Article`, `Dataset` |

---

### E.7 — Señales Técnicas Básicas

| Señal | Estado | Observación |
|---|---|---|
| **HTTPS** | ✅ Activo | Sin mixed content aparente |
| **www vs. non-www** | ⚠️ Inconsistencia | El sitemap usa non-www, el sitio sirve con www |
| **Mobile-friendly** | ✅ Responsive | Layout adapta a mobile (inferido de estructura moderna) |
| **Velocidad percibida** | ⚠️ Potencialmente lenta | Feed Instagram embebido + imágenes de producto sin WebP confirmado |
| **Robots.txt** | ❌ No existe | GET /robots.txt devuelve 404 |
| **Sitemap XML** | ✅ Existe | 56 URLs, generado 4 jun 2026, en `/sitemap.xml` (non-www) |
| **Open Graph tags** | ❌ No detectadas | Impacta previews en redes sociales |
| **Hreflang** | N/A | Sitio monolingüe en español |
| **Canonical tags** | ❌ No detectadas | Riesgo de contenido duplicado (www vs non-www) |
| **Blog desactualizado** | ❌ Crítico | Último post visible: marzo 2021 — 5 años sin publicar |

---

## Gaps y Oportunidades de Marca

### Identidad Visual
1. **Paleta no documentada públicamente:** No hay design tokens / variables CSS accesibles — lo que sugiere ausencia de un sistema de diseño formalizado. Cualquier nueva pieza corre riesgo de inconsistencia.
2. **Logo sin variantes confirmadas:** Solo se detectó una versión del logo. Falta: versión negativa (blanco sobre fondos oscuros), ícono solo, versión monocromática.
3. **Alt text de imágenes vacío:** Las imágenes de campo y producto carecen de descriptores — además de un problema SEO, es un problema de accesibilidad (WCAG).
4. **Feed de Instagram como "galería" del homepage:** Delegar la imagen del homepage a contenido de red social es un riesgo de consistencia visual y disponibilidad.

### Comunicación
5. **Blog abandonado desde 2021:** La sección existe pero el último artículo tiene 5 años. Esto daña la credibilidad editorial y pierde tráfico orgánico de long-tail.
6. **"COLOR RINDE" sin definición:** El claim aparece en el homepage pero nunca se explica — confunde al usuario nuevo.
7. **Bases y condiciones en Google Docs:** Contenido legal crítico hosteado en un dominio externo no controlado. Debería estar en una página propia del sitio.
8. **Sección de Ensayos sin visibilidad:** 16 páginas de ensayos técnicos (contenido de alto valor para agrónomos) están completamente fuera del menú principal.

---

## Prioridades SEO — Top 10

| # | Problema | Impacto | Acción correctiva |
|---|---|---|---|
| 1 | **Cero meta descriptions en todo el sitio** | 🔴 Crítico | Redactar meta description única (150–160 chars) por página, con keyword principal + CTA. Priorizar homepage, catálogos y ensayos. |
| 2 | **Robots.txt inexistente (404)** | 🔴 Crítico | Crear `/robots.txt` con directivas básicas: `User-agent: * / Allow: /` y apuntar al sitemap: `Sitemap: https://www.stinesemillas.com.ar/sitemap.xml` |
| 3 | **Sin schema markup en ninguna página** | 🔴 Crítico | Implementar al mínimo: `Organization` en homepage, `Product` en catálogos de variedades, `Article` en blog, `LocalBusiness` en contacto y stiners. |
| 4 | **Sin canonical tags — inconsistencia www/non-www** | 🔴 Crítico | Definir www como versión canónica, agregar `<link rel="canonical">` en todas las páginas, redirigir non-www a www vía 301, actualizar sitemap a URLs con www. |
| 5 | **Open Graph tags ausentes** | 🟠 Alto | Agregar `og:title`, `og:description`, `og:image`, `og:type` en todas las páginas. Prioriza homepage y artículos de blog. Impacta CTR en redes sociales. |
| 6 | **H1s sin keywords de producto en páginas clave** | 🟠 Alto | Reescribir H1 de homepage para incluir "semillas", "soja" o "maíz". Ej: "Semillas de Soja y Maíz de Alto Rendimiento — Esto No Es Suerte, Es Stine." |
| 7 | **H1 duplicado en catálogos (soja y maíz)** | 🟠 Alto | Eliminar el H1 duplicado en cada página de catálogo. Un solo H1 por página, idealmente con keyword de variedad/categoría. |
| 8 | **Páginas thin content (catálogos, contacto, blog)** | 🟠 Alto | Enriquecer catálogos con: descripción de cada grupo de madurez, beneficios agrónomicos, zonas recomendadas. Agregar copy editorial en página de contacto. |
| 9 | **Alt text ausente en imágenes de producto y campo** | 🟡 Medio | Agregar alt text descriptivo a todas las imágenes. Formato recomendado: `[nombre-variedad] semillas de [soja/maíz] stine [contexto]`. También mejora accesibilidad. |
| 10 | **Blog desactualizado (último post: 2021)** | 🟡 Medio | Retomar publicaciones con frecuencia mínima mensual. Priorizar: resultados de ensayos de campaña actual, notas técnicas de variedades, noticias de tecnología Enlist. El sitio ya tiene 16 páginas de ensayos que podrían adaptarse como posts. |

---

*Documento generado por Claude Code — stineseed.com — Junio 2026*
