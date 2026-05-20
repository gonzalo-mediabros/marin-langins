# Design System — Marín Pistachia Landings

## Mode
EXTRACTOR — extraído del HTML aprobado `abogado-accidente-trabajo-neuquen/index.html`

---

## Color palette

| Token           | Valor     | Tailwind class                        | Uso                                              |
|-----------------|-----------|---------------------------------------|--------------------------------------------------|
| --color-brand   | #382f71   | bg-brand, text-brand, border-brand    | Violeta principal: navbar border, H1, badges, CTAs outline, CTA final bg |
| --color-cyan    | #018292   | text-cyan, bg-cyan                    | Subtítulo hero, íconos check, chips de sectores  |
| --color-rosa    | #c11672   | bg-rosa, text-rosa, shadow-rosa       | CTA primario WhatsApp (botón principal + navbar) |
| --color-azul    | #00198a   | text-azul, bg-azul                    | Número de pasos, highlights eventuales           |
| --color-surface | #ffffff   | bg-surface, text-surface              | Fondos blancos, texto sobre fondos oscuros       |

**Colores Tailwind estándar usados (no van en @theme):**
- `text-gray-800` — color base del body (`#1f2937`)
- `text-gray-600` — texto secundario / descriptivo
- `text-gray-500` — texto muted / labels
- `bg-gray-50` / `bg-slate-50` — fondos de sección alternativos

**Nota de accesibilidad:**
- `--color-brand` (#382f71) sobre blanco → ratio ~8.5:1. Pasa AAA.
- `--color-rosa` (#c11672) sobre blanco → ratio ~5.2:1. Pasa AA.
- `--color-cyan` (#018292) sobre blanco → ratio ~4.6:1. Pasa AA (borderline — no usar en texto pequeño < 14px).
- `--color-azul` (#00198a) sobre blanco → ratio ~10.1:1. Pasa AAA.

---

## Tipografía

| Token        | Valor                          | Tailwind class | Pesos usados        |
|--------------|--------------------------------|----------------|---------------------|
| --font-sans  | "Inter Variable", sans-serif   | font-sans      | 400, 500, 600, 700, 800 |

**Fuente:** Inter Variable vía `@fontsource-variable/inter` (instalada en node_modules).  
En el HTML original se usa Google Fonts CDN con pesos discretos (400/500/600/700/800). En Astro se usa la versión variable local que incluye todo el rango.

**Escala tipográfica usada en el HTML (clases Tailwind):**
- `text-sm` (14px) — badges, labels, nav CTA
- `text-base` (16px) — body, CTAs
- `text-xl` (20px) — subtítulo hero
- `text-2xl` (24px) — subtítulos de sección
- `text-3xl` (30px) — subtítulo hero desktop
- `text-4xl` (36px) — H1 mobile
- `text-5xl` (48px) — H1 desktop

---

## Contenedor y layout

| Token / Elemento  | Valor              | Descripción                           |
|-------------------|--------------------|---------------------------------------|
| m-container       | max-width: 1400px  | Contenedor principal, margin auto, padding 0 1rem |
| m-row             | flex-direction: row | Flex row; colapsa a column en < 768px |
| m-col             | flex: 1            | Columna flex con min-width: 0 para overflow seguro |

**Breakpoint de colapso de m-row:** `768px` (equivalente a `md` de Tailwind).

---

## Espaciado

El HTML usa la escala de espaciado estándar de Tailwind. No se definieron tokens custom. Valores más usados:

| Clase Tailwind | Valor   | Contexto de uso                    |
|----------------|---------|------------------------------------|
| gap-3          | 0.75rem | Gap entre botones                  |
| gap-4          | 1rem    | Gap entre items de checklist       |
| gap-6          | 1.5rem  | Gap columnas hero                  |
| gap-12         | 3rem    | Gap m-row hero mobile              |
| gap-16         | 4rem    | Gap m-row hero desktop             |
| py-3           | 0.75rem | Padding vertical navbar            |
| py-16          | 4rem    | Padding secciones mobile           |
| py-24          | 6rem    | Padding secciones desktop          |
| px-4 / px-8    | 1/2rem  | Padding horizontal botones         |
| py-2.5 / py-4  | —       | Padding vertical botones           |

---

## Border-radius

| Uso                              | Clase Tailwind |
|----------------------------------|----------------|
| Botones CTA principales          | rounded-xl     |
| Botón outline (calculadora)      | rounded-xl     |
| Badge ubicación                  | rounded-full   |
| Cards de sectores / stats        | rounded-xl     |
| Cards de proceso / lesiones      | rounded-xl     |
| Inputs, chips pequeños           | rounded-lg     |
| Blob decorativo hero             | rounded-full   |

---

## Sombras

| Clase Tailwind       | Uso                                              |
|----------------------|--------------------------------------------------|
| shadow-sm            | Navbar                                           |
| shadow-md            | Nav CTA WhatsApp                                 |
| shadow-lg            | CTA hero principal                               |
| shadow-xl            | CTA hero hover state                             |
| shadow-rosa/30       | Sombra coloreada CTA rosa (color opacity)        |
| shadow-rosa/40       | Sombra coloreada CTA rosa hover                  |

---

## Breakpoints

Tailwind v4 usa los mismos breakpoints por defecto:

| Nombre | Valor  |
|--------|--------|
| sm     | 640px  |
| md     | 768px  |
| lg     | 1024px |
| xl     | 1280px |
| 2xl    | 1536px |

El HTML usa principalmente `md:` y `lg:` para layout de dos columnas.

---

## Textura de sección

La sección `#sectores` tiene una textura sutil definida en global.css:

```css
background-image: radial-gradient(circle, #382f7112 1px, transparent 1px);
background-size: 22px 22px;
background-color: #f8fafc;
```

El color del punto `#382f7112` es `--color-brand` al 7% de opacidad. En Tailwind v4 esto podría escribirse como `bg-brand/7` si se genera la clase, pero al ser un `background-image` compuesto, queda como valor fijo en CSS.

---

## Custom Elements (no Shadow DOM)

`m-container`, `m-row` y `m-col` son HTML custom elements sin `customElements.define`. El browser los trata como elementos desconocidos con `display: inline` por defecto. Los estilos en `global.css` los convierten en elementos de layout. No requieren JavaScript.

Son equivalentes funcionales a componentes de layout pero permiten usar clases Tailwind adicionales directamente en el markup (ej: `<m-container class="flex items-center justify-between py-3">`).

---

## Notas de migración Tailwind v3 → v4

| Diferencia                  | v3 (HTML original)                          | v4 (Astro)                                      |
|-----------------------------|---------------------------------------------|-------------------------------------------------|
| Config de colores           | `tailwind.config = { theme: { extend: { colors: {...} } } }` | `@theme { --color-brand: #...; }` en CSS        |
| Config de fuentes           | `fontFamily: { sans: ['Inter', 'sans-serif'] }` | `--font-sans: "Inter Variable", sans-serif;` en @theme |
| Plugin `text-balance`       | Plugin custom en `tailwind.config`          | Utilidad nativa en Tailwind v4 — sin plugin     |
| Opacidad en sombras         | `shadow-rosa/30` funciona igual             | Compatible — sintaxis de opacidad sin cambios   |
| Clases generadas por tokens | `text-brand`, `bg-brand`, `border-brand`   | Igual — @theme genera las mismas utilidades     |
| `@apply`                    | Disponible                                  | Disponible pero no recomendado en v4; preferir utilidades directas |
