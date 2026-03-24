---
name: vue-saas-redesign
description: Redesigns a Vue 3 application's UI into a modern SaaS-style interface with a vertical navigation sidebar, consistent spacing, and polished professional design using shadcn-vue and Tailwind CSS. Use this skill whenever the user wants to modernize a Vue app's layout, replace a top navigation bar with a sidebar, apply SaaS dashboard styling, improve UI consistency, add a professional design system, or give their Vue 3 app a polished look. Also applies when users mention "dashboard layout", "admin panel UI", "sidebar navigation", "redesign my Vue app", or want to move from a basic/ugly UI to a production-grade SaaS aesthetic. Use it even for partial requests like "make it look more professional" or "clean up the UI" on a Vue 3 app.
---

# Vue 3 SaaS UI Redesign

Transform a Vue 3 application from its current layout into a modern SaaS-style interface with a collapsible vertical sidebar, consistent design tokens, and professional polish using **shadcn-vue** and **Tailwind CSS**.

## Why this skill exists

Most Vue 3 apps start with a basic top navbar and inconsistent styling. SaaS products universally use a sidebar layout because it scales better with growing navigation, keeps the main content area wide, and looks professional. This skill automates the entire transformation — from layout restructuring to component restyling to testing — so the result is cohesive rather than piecemeal.

Without this skill, Claude tends to build functional sidebar UIs but misses key conventions: proper shadcn-vue component naming (`AppSidebar.vue`, `AppLayout.vue`), design token CSS variables (`--sidebar-*`), router-derived navigation config, and comprehensive e2e test coverage. This skill ensures a consistent, production-grade result every time.

## Prerequisites

Before starting, verify the project has:

- Vue 3 (Composition API / `<script setup>`)
- Vite as the build tool
- vue-router 4.x

If any are missing, stop and tell the user what needs to be added first.

## Important Conventions

These naming and structural conventions are non-negotiable — they ensure consistency across projects and make the output immediately recognizable as a professional SaaS app:

- Layout wrapper: always `src/layouts/AppLayout.vue` (not `SidebarLayout`, `DashboardLayout`, etc.)
- Sidebar component: always `src/components/AppSidebar.vue` (not `TheSidebar`, `NavigationSidebar`, etc.)
- Navigation config: always `src/config/navigation.ts` (or `.js`) derived from the router
- Design tokens: always use `--sidebar-*` CSS variables for sidebar theming
- Icons: always use `lucide-vue-next` — every nav item must have an icon
- App.vue: must be stripped to just `<router-view />` after redesign
- Match the project's language: if the project uses JavaScript, write `.js` files; if TypeScript, write `.ts`

## Phase 1: Analyze the Existing App

Understand what you're working with before changing anything.

### 1.1 Scan project structure

```bash
# Get the lay of the land
find src -type f -name '*.vue' -o -name '*.ts' -o -name '*.js' | head -50
cat src/router/index.ts  # or index.js
cat src/App.vue
```

Identify:

- **Router config location** and all route definitions (path, name, component, children, meta)
- **Existing navigation** — top navbar component, any drawer/sidebar already present
- **Layout components** — any wrapper/layout components
- **Component library** currently in use (Vuetify, Element Plus, PrimeVue, or vanilla)
- **CSS approach** — Tailwind already present? SCSS? CSS modules?

### 1.2 Map the navigation tree

Read the router config and build a mental model of the nav hierarchy:

```
Route path → Display name → Icon → Parent group
/dashboard  → Dashboard    → LayoutDashboard → (top-level)
/projects   → Projects     → FolderKanban    → (top-level)
/settings   → Settings     → Settings        → (bottom, footer)
```

Routes with `meta.hidden: true` or redirect-only routes should be excluded from the sidebar. Nested routes (children) become sub-items under a collapsible group.

## Phase 2: Install Dependencies

### 2.1 Install shadcn-vue (if not already present)

```bash
npx shadcn-vue@latest init
```

When prompted, choose:

- TypeScript: Yes (if the project uses TS, otherwise No)
- Framework: Vite
- Style: Default
- Base color: Zinc (professional neutral — can adjust later)
- CSS variables: Yes

### 2.2 Add required shadcn-vue components

```bash
npx shadcn-vue@latest add sidebar
npx shadcn-vue@latest add button
npx shadcn-vue@latest add separator
npx shadcn-vue@latest add tooltip
npx shadcn-vue@latest add sheet
npx shadcn-vue@latest add avatar
npx shadcn-vue@latest add dropdown-menu
npx shadcn-vue@latest add collapsible
npx shadcn-vue@latest add badge
```

### 2.3 Install Lucide icons

```bash
npm install lucide-vue-next
```

Lucide is the icon set shadcn-vue uses. Every sidebar nav item needs an icon — it's not optional for professional SaaS feel.

## Phase 3: Set Up Design Tokens

A cohesive design system prevents the "inconsistent spacing and random colors" problem.

Read `references/design-tokens.md` for the complete token definitions. The key points:

### 3.1 CSS variables in `src/assets/index.css` (or main CSS file)

Set up the shadcn-vue CSS variable system with a professional SaaS palette. The sidebar gets its own color scope (`--sidebar-*` variables) so it can have a dark/branded appearance independent of the main content area.

### 3.2 Tailwind config

Extend `tailwind.config.js` to map the CSS variables to Tailwind utilities. This is how shadcn-vue's theming works — CSS variables define the values, Tailwind config maps them to class names.

### 3.3 Spacing scale

Use Tailwind's default spacing scale consistently:

- **Page padding**: `p-6` (24px)
- **Card padding**: `p-4` to `p-6`
- **Between sections**: `space-y-6`
- **Between related items**: `space-y-2` or `gap-2`
- **Sidebar item padding**: `px-3 py-2`

Never use arbitrary pixel values (`p-[13px]`). Stick to the scale.

## Phase 4: Build the Sidebar Layout

This is the core transformation. Read `references/sidebar-layout.md` for complete code examples.

### 4.1 Create `src/layouts/AppLayout.vue`

This is the shell that wraps every authenticated page:

```vue
<script setup lang="ts">
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar.vue";
import { Separator } from "@/components/ui/separator";
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-14 items-center gap-2 border-b px-6">
        <SidebarTrigger class="-ml-2" />
        <Separator orientation="vertical" class="h-4" />
        <slot name="header" />
      </header>
      <main class="flex-1 overflow-auto p-6">
        <router-view />
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
```

### 4.2 Create `src/components/AppSidebar.vue`

The sidebar reads from a navigation config (derived from vue-router) and renders items with icons, labels, badges, and collapsible groups.

Key structure:

- **SidebarHeader** — App logo/name + optional workspace switcher
- **SidebarContent** — Navigation groups (main nav, secondary nav)
- **SidebarFooter** — User avatar + dropdown menu (settings, logout)

The sidebar must:

- Be collapsible (icon-only mode) via `collapsible="icon"` prop
- Highlight the active route using `useRoute()` comparison
- Support keyboard shortcut (Ctrl/Cmd + B) to toggle
- Persist collapsed state (shadcn-vue handles this via cookie/localStorage)

### 4.3 Create `src/config/navigation.ts`

Generate this from the router config. Don't hardcode nav items separately from routes — that leads to drift.

```typescript
import { type RouteRecordRaw } from "vue-router";
import { routes } from "@/router";
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  Settings,
  // ... import icons per route
} from "lucide-vue-next";

export interface NavItem {
  title: string;
  path: string;
  icon: Component;
  badge?: string | number;
  children?: NavItem[];
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

// Map route meta to nav items
// Routes with meta.nav = false are excluded
// Routes with meta.navGroup define which group they belong to
// Routes with children become collapsible groups
```

### 4.4 Update `src/App.vue`

Strip the old top navbar. App.vue becomes minimal:

```vue
<template>
  <router-view />
</template>
```

### 4.5 Update router to use layout

Wrap routes that need the sidebar in a layout route:

```typescript
{
  path: '/',
  component: () => import('@/layouts/AppLayout.vue'),
  children: [
    { path: 'dashboard', component: Dashboard, meta: { nav: true, icon: 'LayoutDashboard' } },
    { path: 'projects', component: Projects, meta: { nav: true, icon: 'FolderKanban' } },
    // ...
  ]
}
```

Auth routes (login, register) stay outside the layout wrapper.

## Phase 5: Restyle Components

Read `references/component-patterns.md` for specific before/after patterns.

### General approach

1. **Replace existing component library usage** with shadcn-vue equivalents
2. **Apply consistent Tailwind classes** for spacing, typography, and colors
3. **Use the design token CSS variables** — never hardcode colors

### Priority order for restyling

1. **Buttons** — Replace all buttons with shadcn-vue `Button` variants (default, secondary, outline, ghost, destructive)
2. **Cards** — Wrap content sections in shadcn-vue `Card` with consistent padding
3. **Tables** — Use shadcn-vue `Table` with proper header styling and row hover states
4. **Forms** — Use shadcn-vue form components (Input, Select, Checkbox, etc.) with consistent label spacing
5. **Dialogs/Modals** — Replace with shadcn-vue `Dialog`
6. **Badges/Tags** — Use shadcn-vue `Badge` for status indicators
7. **Typography** — Apply consistent heading sizes: h1 = `text-2xl font-semibold tracking-tight`, h2 = `text-xl font-semibold`, h3 = `text-lg font-medium`

### Page layout pattern

Every page should follow this structure for consistency:

```vue
<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">Page Title</h1>
        <p class="text-sm text-muted-foreground">Description of this page</p>
      </div>
      <Button>Primary Action</Button>
    </div>

    <!-- Content -->
    <Card>
      <CardHeader>
        <CardTitle>Section</CardTitle>
        <CardDescription>Details</CardDescription>
      </CardHeader>
      <CardContent>
        <!-- ... -->
      </CardContent>
    </Card>
  </div>
</template>
```

## Phase 6: Add Tests

Testing ensures the redesign doesn't break functionality and the new layout works correctly.

### 6.1 Vitest — Unit/Component Tests

Create `src/components/__tests__/AppSidebar.test.ts`:

- Test that sidebar renders all expected nav items from router config
- Test that active route is highlighted correctly
- Test that collapsible groups expand/collapse
- Test that hidden routes (meta.nav = false) are excluded
- Test that the sidebar emits collapse/expand events

Create `src/layouts/__tests__/AppLayout.test.ts`:

- Test that layout renders sidebar + main content area
- Test that router-view slot receives content

### 6.2 Playwright — E2E Tests

Create `e2e/sidebar-navigation.spec.ts`:

```typescript
import { test, expect } from "@playwright/test";

test.describe("Sidebar Navigation", () => {
  test("sidebar is visible and contains nav items", async ({ page }) => {
    await page.goto("/");
    const sidebar = page.locator('[data-sidebar="sidebar"]');
    await expect(sidebar).toBeVisible();
  });

  test("clicking nav item navigates to correct route", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Dashboard");
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test("sidebar collapses and expands", async ({ page }) => {
    await page.goto("/");
    const trigger = page.locator('[data-sidebar="trigger"]');
    await trigger.click();
    // Verify collapsed state
    const sidebar = page.locator('[data-sidebar="sidebar"]');
    await expect(sidebar).toHaveAttribute("data-state", "collapsed");
  });

  test("keyboard shortcut toggles sidebar", async ({ page }) => {
    await page.goto("/");
    await page.keyboard.press("Control+b");
    const sidebar = page.locator('[data-sidebar="sidebar"]');
    await expect(sidebar).toHaveAttribute("data-state", "collapsed");
  });

  test("active route is highlighted in sidebar", async ({ page }) => {
    await page.goto("/dashboard");
    const activeItem = page.locator(
      '[data-sidebar="menu-button"][data-active="true"]',
    );
    await expect(activeItem).toBeVisible();
  });
});
```

Create `e2e/responsive-layout.spec.ts`:

- Test that sidebar becomes a sheet/drawer on mobile viewport
- Test that main content area takes full width when sidebar is collapsed
- Test that the layout is usable at 375px, 768px, and 1440px widths

## Phase 7: Verify and Polish

After all changes:

1. Run `npm run dev` and visually inspect every page
2. Run `npx vitest run` — all tests should pass
3. Run `npx playwright test` — all e2e tests should pass
4. Check for:
   - Consistent spacing (no rogue `margin-top: 17px` or `p-[13px]`)
   - All colors using CSS variables (no hardcoded hex values)
   - Sidebar active state matches current route on every page
   - Mobile responsiveness — sidebar becomes sheet below `md` breakpoint
   - Dark mode works if the app supports it (shadcn-vue tokens handle this automatically)
   - No leftover old navbar code or unused CSS

## Checklist

Before declaring the redesign complete:

- [ ] Old top navbar removed entirely
- [ ] Sidebar renders all navigable routes from vue-router config
- [ ] Sidebar collapses to icon-only mode
- [ ] Active route highlighted in sidebar
- [ ] Keyboard shortcut (Cmd/Ctrl + B) toggles sidebar
- [ ] App logo in sidebar header
- [ ] User menu in sidebar footer (avatar + dropdown)
- [ ] All pages follow consistent page layout pattern
- [ ] All components restyled with shadcn-vue
- [ ] Design tokens (CSS variables) used everywhere — no hardcoded colors
- [ ] Consistent spacing using Tailwind scale
- [ ] Vitest component tests passing
- [ ] Playwright e2e tests passing
- [ ] Mobile responsive (sidebar → sheet on small screens)
