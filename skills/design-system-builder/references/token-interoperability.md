# Token interoperability

Use a portable source when multiple tools/platforms need tokens; CSS-only projects need
not introduce a token pipeline solely to satisfy this checklist.

The [DTCG 2025.10 format](https://www.designtokens.org/tr/2025.10/format/) is a stable
Community Group report, not a W3C Standard. Record the supported format version and
tool limitations. Typed `$value`/`$type` records, groups and aliases support exchange;
validate references, inherited types and cycles before generating outputs.

Example dimension token and alias:

```json
{
  "space": {
    "$type": "dimension",
    "small": { "$value": { "value": 4, "unit": "px" } },
    "controlGap": { "$value": "{space.small}" }
  }
}
```

Declare one editable source and generated outputs. Check tool-specific round trips,
name collisions, resolved values and theme contexts; reject generated-output drift.
Consult the [resolver module](https://www.designtokens.org/tr/2025.10/resolver/) when
interchanging contextual token sets; verify actual tool support rather than assuming it.

For [Tailwind v4](https://tailwindcss.com/docs/theme), preserve token CSS separately
from Tailwind directives. Example integration:

```css
@theme inline {
  --color-brand: var(--color-bg-brand);
}
```

`bg-brand` then uses the scoped semantic value. Test light/dark scopes in compiled CSS;
a copied `@theme` file alone does not work in a consumer without Tailwind processing.
