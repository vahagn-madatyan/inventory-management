# Vue SaaS UI Redesign Plan

## Context

The inventory management app (`client/`) uses Vue 3 + Composition API with a horizontal top navbar, vanilla CSS (486 lines of global styles in App.vue), and no component library. The goal is to transform it into a modern SaaS-style interface with a collapsible vertical sidebar, shadcn-vue components, Tailwind CSS design tokens, and consistent styling — following the `vue-saas-redesign` skill.

**Current state:** 7 views, 9 components, 3 composables, pure JavaScript, no Tailwind, no tests, no `@/` path alias.

**CLAUDE.md rule:** All `.vue` file creation/modification MUST be delegated to the `vue-expert` subagent.

---

## Phase 0: Foundation (No Visual Changes)

### 0.1 Add `@/` path alias to `vite.config.js`

Required for shadcn-vue imports.

```js
resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } }
```

### 0.2 Install Tailwind CSS + PostCSS

```bash
cd client
npm install -D tailwindcss postcss autoprefixer tailwindcss-animate
npx tailwindcss init -p
```

### 0.3 Create design tokens CSS

**New file:** `src/assets/index.css`

- Tailwind directives (`@tailwind base/components/utilities`)
- CSS variables from `references/design-tokens.md` (light + dark themes)
- `--sidebar-*` variables for sidebar theming

### 0.4 Configure Tailwind

**File:** `tailwind.config.js`

- Content paths: `["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"]`
- Full color extension mapping CSS variables to Tailwind utilities (from `references/design-tokens.md`)
- `tailwindcss-animate` plugin

### 0.5 Import CSS in `main.js`

Add `import './assets/index.css'` before app creation.

### 0.6 Install shadcn-vue

```bash
npx shadcn-vue@latest init
```

Options: No TypeScript, Vite, Default style, Zinc base color, CSS variables: Yes

### 0.7 Add shadcn-vue components

```bash
npx shadcn-vue@latest add sidebar button separator tooltip sheet avatar dropdown-menu collapsible badge card table dialog input label select
```

### 0.8 Install Lucide icons

```bash
npm install lucide-vue-next
```

**Checkpoint:** `npm run dev` works, app looks identical (no components changed yet).

---

## Phase 1: Layout Shell (Sidebar Replaces Top Nav)

### 1.1 Extract global CSS from App.vue

Move the `<style>` block (486 lines) from `App.vue` to **new file** `src/assets/global-legacy.css`. Import it in `main.js`. This preserves existing styles during the transition.

### 1.2 Create `useModals.js` composable

**New file:** `src/composables/useModals.js`

Extract from `App.vue` (lines 83-162): `showProfileDetails`, `showTasks`, `tasks` computed, `addTask`, `deleteTask`, `toggleTask`, `loadTasks`. Singleton pattern (like `useFilters.js`).

### 1.3 Create navigation config

**New file:** `src/config/navigation.js`

Standalone data file mapping routes to sidebar items with i18n keys and Lucide icons:

| Path          | i18n Key             | Icon              | Group     |
| ------------- | -------------------- | ----------------- | --------- |
| `/`           | `nav.overview`       | `LayoutDashboard` | main      |
| `/inventory`  | `nav.inventory`      | `Package`         | main      |
| `/orders`     | `nav.orders`         | `ShoppingCart`    | main      |
| `/spending`   | `nav.finance`        | `DollarSign`      | main      |
| `/demand`     | `nav.demandForecast` | `TrendingUp`      | main      |
| `/restocking` | `nav.restocking`     | `RefreshCw`       | main      |
| `/reports`    | Reports              | `BarChart3`       | main      |
| `/backlog`    | Backlog              | `AlertTriangle`   | secondary |

### 1.4 Create `AppSidebar.vue`

**New file:** `src/components/AppSidebar.vue`

Per `references/sidebar-layout.md`, adapted to JS + i18n:

- **Header:** Logo ("CC") + company name via `t('nav.companyName')`
- **Content:** Main nav group + secondary nav group from navigation config
- **Footer:** User avatar + dropdown (Profile Details, My Tasks, Logout) — replaces current `ProfileMenu.vue`
- `collapsible="icon"` for collapse mode
- Active route detection via `useRoute()`

### 1.5 Create `AppLayout.vue`

**New file:** `src/layouts/AppLayout.vue`

- `SidebarProvider` > `AppSidebar` + `SidebarInset`
- Header bar: `SidebarTrigger` | `Separator` | `FilterBar` (flex-1) | `LanguageSwitcher`
- Main: `<router-view />` with `p-6`
- Renders `ProfileDetailsModal` and `TasksModal` (using `useModals` composable)

### 1.6 Restructure router in `main.js`

- Switch from eager imports to lazy imports (`() => import(...)`)
- Wrap all routes as children of `AppLayout` parent route
- Add `meta` to each route (`nav`, `navGroup`, `title`, `icon`)
- Add `/backlog` route (currently missing from router)

### 1.7 Strip `App.vue`

Reduce to just `<template><router-view /></template>`. All logic moved to `useModals.js` and `AppLayout.vue`.

**Checkpoint:** Sidebar visible, all routes navigable, FilterBar in header, ProfileMenu in sidebar footer, modals work, i18n works. Views still use legacy CSS.

---

## Phase 2: Restyle Views & Components

Work one view at a time. General pattern per view:

1. Replace custom CSS classes with Tailwind utilities
2. Replace HTML elements with shadcn-vue components (Card, Table, Badge, Button)
3. Wrap SVG charts in Card containers (keep chart code as-is)
4. Remove scoped `<style>` blocks
5. Follow page layout pattern from skill (space-y-6 wrapper, page header, Card sections)

### 2.1 FilterBar.vue

Replace custom selects with shadcn-vue `Select`, reset button with `Button variant="ghost"`. Remove sticky positioning.

### 2.2 Dashboard.vue (1271 lines — largest)

- KPI cards → shadcn-vue `Card` with `grid gap-4 md:grid-cols-2 lg:grid-cols-4`
- SVG charts → wrap in `Card`, keep SVG untouched
- Tables → shadcn-vue `Table`
- Badges → shadcn-vue `Badge`

### 2.3 Inventory.vue

Search input → shadcn-vue `Input`. Table → shadcn-vue `Table`. Status badges → `Badge`.

### 2.4 Orders.vue

Stat cards → `Card` grid. Table → `Table`. Status badges → `Badge`.

### 2.5 Spending.vue (852 lines)

KPI cards → `Card`. SVG charts → wrap in `Card`. Transaction table → `Table`.

### 2.6 Demand.vue

Trend cards → `Card` with colored accents. Item lists → Tailwind utilities.

### 2.7 Reports.vue

Quarterly table → `Table`. SVG charts → wrap in `Card`.

### 2.8 Backlog.vue

Priority stat cards → `Card`. Table → `Table`. Priority badges → `Badge`.

### 2.9 Restocking.vue

Bring up to shadcn-vue standard matching other views.

### 2.10 Restyle all modals (6 total)

Replace `Teleport + custom overlay` with shadcn-vue `Dialog`. For each:

- `ProfileDetailsModal.vue` → Dialog with user info grid
- `TasksModal.vue` → Dialog with task form (Input, Select, Button) and task list
- `InventoryDetailModal.vue` → Dialog with item details
- `ProductDetailModal.vue` → Dialog with product details
- `BacklogDetailModal.vue` → Dialog with backlog details
- `CostDetailModal.vue` → Dialog with cost breakdown

### 2.11 Delete legacy CSS

Remove `src/assets/global-legacy.css` and its import from `main.js`.

**Checkpoint:** All pages use Tailwind + shadcn-vue. No hardcoded hex colors. Consistent spacing.

---

## Phase 3: Polish

- Verify i18n on all sidebar labels; add missing keys for Reports/Backlog
- Restyle `LanguageSwitcher.vue` with shadcn-vue `DropdownMenu`
- Test responsive behavior: sidebar → sheet below `md` breakpoint
- Remove old `ProfileMenu.vue` if fully absorbed into `AppSidebar`
- Clean up unused imports/files

---

## Phase 4: Tests

### 4.1 Setup

- Add `vitest` config to `vite.config.js` (environment: jsdom)
- Add test scripts to `package.json`
- Create `playwright.config.js`
- Install: `vitest @vue/test-utils jsdom @playwright/test`

### 4.2 Component tests (Vitest)

- `src/components/__tests__/AppSidebar.test.js` — renders nav items, active state, collapse
- `src/layouts/__tests__/AppLayout.test.js` — renders sidebar + content

### 4.3 E2E tests (Playwright)

- `e2e/sidebar-navigation.spec.js` — sidebar visible, nav clicks route correctly, collapse/expand, keyboard shortcut
- `e2e/responsive-layout.spec.js` — sidebar → sheet on mobile, 375/768/1440px widths

---

## Key Files to Modify

| File                                   | Action                                            |
| -------------------------------------- | ------------------------------------------------- |
| `client/vite.config.js`                | Add `@/` alias, vitest config                     |
| `client/src/main.js`                   | Restructure router, add CSS imports, lazy imports |
| `client/src/App.vue`                   | Strip to `<router-view />`                        |
| `client/src/assets/index.css`          | **New** — design tokens CSS                       |
| `client/src/assets/global-legacy.css`  | **New** (temporary) — extracted global CSS        |
| `client/src/layouts/AppLayout.vue`     | **New** — sidebar layout shell                    |
| `client/src/components/AppSidebar.vue` | **New** — sidebar component                       |
| `client/src/config/navigation.js`      | **New** — router-derived nav config               |
| `client/src/composables/useModals.js`  | **New** — extracted modal/task logic              |
| `client/tailwind.config.js`            | **New** — Tailwind with design tokens             |
| `client/src/views/*.vue` (all 8)       | Restyle with shadcn-vue + Tailwind                |
| `client/src/components/*.vue` (all 9)  | Restyle modals + FilterBar + LanguageSwitcher     |

## Existing Code to Reuse

- `src/composables/useFilters.js` — filter state (keep as-is, FilterBar moves to layout header)
- `src/composables/useAuth.js` — user data for sidebar footer avatar/name
- `src/composables/useI18n.js` — `t()` function for sidebar nav labels (keys already exist: `nav.overview`, `nav.inventory`, etc.)
- `src/api.js` — all API methods unchanged
- `src/locales/en.js` + `ja.js` — existing i18n translations
- All SVG chart code in Dashboard/Spending/Reports — keep as-is, just wrap in Cards

## Verification

1. `npm run dev` — all 8 routes render correctly with sidebar
2. Sidebar: collapses/expands, active route highlighted, keyboard shortcut (Ctrl+B)
3. FilterBar works in new header position
4. All modals open/close from sidebar footer and view row clicks
5. i18n switching (en/ja) works for nav labels
6. Responsive: sidebar becomes sheet below 768px
7. No hardcoded hex colors remaining (grep for `#[0-9a-f]{3,6}`)
8. `npx vitest run` — component tests pass
9. `npx playwright test` — E2E tests pass
