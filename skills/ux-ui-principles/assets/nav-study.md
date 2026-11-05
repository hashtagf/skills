# Navigation study (navigation grouping evidence)

Collected **2026-11-04** from public pages only: docs, help centres, public
demos, open-source code and logged-out marketing navs. Signed-in dashboards
were not opened, so app structures come from documentation and may lag the
live product. Used by [navigation grouping](../references/navigation-grouping.md).
Groups separated by " / "; item counts in brackets.

Not available publicly: Tailwind UI app shells (login), Attio help (404),
full tab bars of SCB EASY, Krungthai NEXT, LINE MAN, Grab; K PLUS partial.
Instagram tab order from third-party reporting only.

## App sidebars (14)

| Product | Structure | Source |
|---|---|---|
| Linear | switcher + Search + New issue / Pulse, Inbox, My issues, Reviews [4] / Workspace: Initiatives, Projects, More / Favorites / Your teams; reorderable, hide to More | linear.app; linear.app/changelog/2024-12-18-personalized-sidebar |
| Notion | Shortcuts (Search, Home, AI, Meetings, Library, new page) / Favorites, Teamspaces, Shared, Private; bottom: Settings, Templates, Trash, workspace | notion.com/help/navigate-with-the-sidebar |
| Stripe Dashboard | Home, Balances, Transactions, Customers, Product catalog [5] / Shortcuts / Products: Connect, Payments, Billing, Reporting + More [8] | docs.stripe.com/dashboard/basics |
| Shopify admin | Orders, Products, Customers, Analytics, Marketing, Discounts / Sales channels / Apps / Settings; staff roles hide areas | help.shopify.com/en/manual/shopify-admin/shopify-admin-overview |
| Vercel | team switcher; team and project levels each with own nav and Settings; universal search | vercel.com/academy/…/tour-the-dashboard |
| GitHub repo | Code, Issues, Pull requests, Discussions, Actions, Security and quality, Insights [7]; Settings only for admins | github.com/vercel/next.js |
| Supabase Studio | Overview / Tools: Table Editor, SQL Editor [2] / Products: Database, Auth, Storage, Edge Functions, Realtime [5] / Other: Advisors, Observability, Logs, Integrations [4] / Project Settings; org: Projects, Team, Integrations, Usage, Billing (flagged), Settings | github.com/supabase/supabase (NavigationBar.utils.tsx, Sidebar.tsx) |
| Figma file browser | team switcher / Search / Recents / Community / Drafts / team folders / Starred / Trash; Admin only for admins | help.figma.com/hc/en-us/articles/14381406380183 |
| Slack | Home, DMs, Activity, Files + More (user-chosen); personal custom sections | slack.com/help/articles/360043207674 |
| Jira (new nav) | For you, Recent, Starred, Apps / Spaces / Dashboards / Assets, Goals / More → Customize; top bar Create, Search | support.atlassian.com/…/what-is-the-new-navigation-in-jira/ |
| HubSpot | Home, Bookmarks (≤10), CRM, Marketing, Content, Sales, Revenue, Service, Data management, Automations, Reporting, Breeze, Development, Partners [14]; collapsed, pin to keep open; permission- and plan-dependent | knowledge.hubspot.com/help-and-resources/a-guide-to-hubspots-navigation |
| shadcn-admin demo | General [5] / Pages [3] / Other: Settings, Help [2]; Settings duplicated in header | shadcn-admin.netlify.app |
| shadcn dashboard-01 | Quick Create, Inbox / 5 items / Documents [3 + More] / Settings, Get Help, Search | ui.shadcn.com/view/new-york-v4/dashboard-01 |
| shadcn sidebar-07 | Platform [4, 3 levels] / Projects [3 + More]; "Settings" at two levels | ui.shadcn.com/view/new-york-v4/sidebar-07 |

## Marketing navs (5)

| Site | Top level | Mega-menu columns |
|---|---|---|
| Stripe | Products, Solutions, Developers, Resources, Pricing · Sign in · Contact sales | Products: Payments [7] / Revenue [8] / Money Management / Embedded Finance / More [5], name + descriptor; Solutions: By stage / By use case [10, A–Z] / By industry [11, A–Z] / Ecosystem |
| Vercel | Products, Resources, Enterprise, Pricing · Get a Demo · Log In · Sign Up | Agent Stack [6] / Core Platform [6] / Tools [6]; external ↗ |
| Shopify | Why Shopify, Products, Pricing, Enterprise, Editions · Log in · Start for free | task headers: Build your website / Sell anywhere / Marketing & analytics / Run your business / Get paid / Customize & extend |
| Atlassian | Products, Solutions, Why Atlassian, Resources, Enterprise · Search · Sign in | Featured apps / outcome collections / Rovo |
| Linear | Product, Resources, Customers, Pricing, Now, Contact · Log in · Sign up | — |

## Settings (7)

Stripe: Personal / Account / Product settings · Linear: Account / Features /
Administration / Your teams · GitHub repo: General / Access / Code and
automation / Security and quality / Integrations (partly from docs) · Google
Account: 7 concern-based items · Vercel: Team vs Project settings · Supabase:
Project vs Organization, roles Owner/Admin/Developer/Read-only/No-access ·
shadcn-admin: Profile, Account, Appearance, Notifications, Display.

## Mobile

LINE Thailand replaced VOOM with OpenChat in the bottom bar (2026-09-28; varies
by region) — help.line.me · Instagram: Home, Reels, Messages, Search, Profile,
Create moved top-left (third-party reports) · Shopee and Grab: account tab
rightmost, Help inside it · K PLUS: Scan on home page · Linear mobile: reorderable
toolbar · Material 3 navigation bar guidelines [S94] · Apple HIG tab bars [S95].

## Counts (apps, N=14)

Personal hub first 12 · object grouping 9 · product/module 4 · task/tool 3 ·
user-curated section 8 · scope grouping 6 · permission hiding 7 · department
grouping 0 · switcher top-left 8 · Settings last in sidebar 6 · user reorder 7 ·
icon + label 14 · labels 1–2 words 13 · two-level depth 11.
