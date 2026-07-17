# Component Inventory & Spec Template

Full inventory ≈ 140 items. Real systems ship in tiers (Mantine ~100, Ant ~70, MUI ~60,
Carbon ~50 — none shipped everything at v1). Scope by tier, drive Tier 3 by product demand.

## Ship tiers

| Tier | Count | Contents |
|---|---|---|
| **1 — MVP** | ~20 | Button, Icon Button, Input, Textarea, Select, Checkbox, Radio, Switch, Form Field (label+helper+error), Card, Table, Modal, Toast, Tabs, Menu/Dropdown, Badge, Avatar, Tooltip, Alert, Spinner, Skeleton, Pagination, Breadcrumb |
| **2 — Growth** | ~50 | + Combobox, Date Picker, Drawer, Accordion, Stepper, Slider, File Upload, Empty State, Popover, Tag/Chip, Progress, Segmented Control, Number Input, Search Input, App Shell, Page Header, Filter Bar, Filter Dropdown… |
| **3 — Full** | 100+ | The rest of this file, pulled in when a product needs it |

**Hard ones**: Data Grid, Date/Range Picker, Combobox, Rich Text Editor cost more than the
rest combined. Default recommendation: headless libraries (TanStack Table, Radix/Ark,
Lexical) skinned with the system's tokens — build from scratch only on explicit request.

## Full inventory

### Form & Input (~30)
Text-based: Text Input, Textarea (+autosize), Number Input, Password Input (+strength meter), Search Input, PIN/OTP Input, Masked Input, Currency Input, Inline Edit, Mentions, Rich Text Editor, Markdown Editor, Code Editor
Selection: Select, Multi-select, Combobox/Autocomplete, Tag Input, Cascader, TreeSelect, Transfer List, Listbox
Choice: Checkbox (+Group), Radio (+Group, +Card), Switch, Segmented Control, Toggle Button Group, Choice/Filter Chips, Rating
Range/Date: Slider, Range Slider, Date Picker, Date Range Picker, Time Picker, DateTime Picker, Month/Year Picker, Color Picker, File Upload, Dropzone, Image Cropper, Signature Pad
Structure: Form, Fieldset, Label, Helper Text, Error Message, Character Counter, Input Group (prefix/suffix/addon), Required Indicator

### Actions (~10)
Button (all variants × sizes), Icon Button, Button Group, Split Button, Dropdown Button, FAB (+Speed Dial), Link, Copy Button, Reaction Button, Close Button

### Navigation (~18)
App Bar/Header, Navbar, Sidebar/Nav Drawer, Navigation Rail, Bottom Navigation, Menu, Dropdown Menu, Context Menu, Mega Menu, Tabs (scrollable/vertical), Breadcrumb, Pagination, Stepper/Wizard, Anchor/TOC, Command Palette (⌘K), Skip Link, Back to Top, Footer

### Data Display (~28)
Table, Data Grid, List, Virtualized List, Description List, Tree View, Feed/Activity, Comment Thread, Card, Stat/KPI, Badge, Notification Dot, Tag/Chip (display), Avatar (+Group), Image (+fallback), Timeline, Calendar (display), Kanban, Carousel, Lightbox/Gallery, Code Block, Kbd, Divider, QR Code, Charts (if in scope: + legend, axis, chart tooltip)
Filtering: Filter Bar (applied-filter chips + clear all), Filter Dropdown (per field/column), Filter Builder (nested and/or conditions — Tier 3, pairs with Data Grid)

### Feedback & Status (~15)
Alert/Banner, Toast/Snackbar (+queue), Notification Center, Announcement Bar, Progress Bar, Progress Circle, Spinner, Loading Overlay, Skeleton variants (text/avatar/card/table), Empty State, Result Page (success/404/500), Tour/Coach Mark, Confirm Dialog, Status Indicator (online/busy dot)

### Overlay (~10)
Modal/Dialog (sizes, fullscreen), Drawer/Sheet (4 sides), Bottom Sheet, Popover, Tooltip, Hover Card, Backdrop/Scrim, Portal, Focus Trap

### Layout (~15)
Container, Grid, Flex/Stack, Spacer, Center, Aspect Ratio, Scroll Area, Split Pane/Resizable, Collapse, Accordion, Affix/Sticky, Masonry, App Shell, Page Header, Section/Panel, Toolbar

### Typography (~8)
Heading, Text/Paragraph, Display, Caption, Truncate/Line Clamp, Highlight/Mark, Prose (rich-content typography), Styled Lists

### Utilities (~8)
Visually Hidden, Focus Ring/Trap, Click Outside, Transition presets, Theme Provider, Portal, Show/Hide (breakpoint)

### Patterns (composed — document, don't componentize prematurely)
Auth (login/register/forgot), Settings Page, Data Table + Toolbar + Filter Bar + Bulk Actions, Search Results, Detail Page, Dashboard Layout, Pricing Table, Profile Menu, Share Dialog, Cookie Consent, Chat/Messaging, Multi-step Checkout, Notification Preferences

## Per-component spec template

Every shipped component gets this spec. "Complete" means every cell filled or marked N/A.

```markdown
## <Component>

**Anatomy**: parts + internal padding, gaps, icon sizes (all values from the spacing/sizing scales)
**Element/ARIA**: what it renders as (`<button>`, `role=...`), required ARIA wiring
**Sizes**: sm / md / lg → height, padding-x, type style, icon size
**Variants**: e.g. primary / secondary / tertiary / ghost / danger
**Tokens**: component tokens it defines, each referencing semantic tokens
**States** (per variant): default, hover, focus-visible, active, disabled,
  loading, error (where applicable) — bg / text / border / shadow per state
**Motion**: which properties transition, duration+easing tokens
**Content rules**: label casing, truncation, min/max lengths
**Do / Don't**: 2–4 usage rules
```

Example (abbreviated) — Button/primary/md:
height 40, padding-x 16, gap 8, radius md, type `label-md`;
default `button-primary-bg` / hover `-hover-bg` / focus-visible ring spec / active `-active-bg`
/ disabled opacity token + `:not(:disabled)` guards / loading: spinner 16, label kept for width stability.
