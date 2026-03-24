# Sidebar Layout Reference

Complete code examples for the sidebar layout transformation.

## Table of Contents

1. [AppLayout.vue — The Shell](#applayout-vue)
2. [AppSidebar.vue — The Sidebar Component](#appsidebar-vue)
3. [Navigation Config — Router Integration](#navigation-config)
4. [Router Updates](#router-updates)
5. [Mobile Responsive Behavior](#mobile-responsive)

---

## AppLayout.vue

The layout shell wraps all authenticated pages. It provides the sidebar + content area structure.

```vue
<script setup lang="ts">
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import AppSidebar from "@/components/AppSidebar.vue";
import { Separator } from "@/components/ui/separator";
import { useRoute } from "vue-router";
import { computed } from "vue";

const route = useRoute();

const pageTitle = computed(() => {
  return (route.meta?.title as string) || (route.name as string) || "";
});
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header
        class="flex h-14 shrink-0 items-center gap-2 border-b bg-background px-6"
      >
        <SidebarTrigger class="-ml-2 h-8 w-8" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <h1 class="text-sm font-medium">{{ pageTitle }}</h1>
      </header>
      <main class="flex-1 overflow-auto p-6">
        <router-view />
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
```

### Key details

- `SidebarProvider` manages collapsed/expanded state and persists it
- `SidebarInset` is the content area that adjusts its width when the sidebar collapses
- The header bar is thin (h-14 = 56px) — it holds just the collapse trigger and breadcrumbs/page title
- Main content area has consistent `p-6` padding

---

## AppSidebar.vue

The main sidebar component. This is the most complex piece — it reads navigation config and renders everything.

```vue
<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  mainNavItems,
  secondaryNavItems,
  type NavItem,
} from "@/config/navigation";
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";
import {
  ChevronRight,
  ChevronsUpDown,
  LogOut,
  Settings,
  User,
} from "lucide-vue-next";

const route = useRoute();
const router = useRouter();

function isActive(item: NavItem): boolean {
  if (route.path === item.path) return true;
  if (item.children?.some((child) => route.path === child.path)) return true;
  return false;
}

function navigate(path: string) {
  router.push(path);
}
</script>

<template>
  <Sidebar collapsible="icon">
    <!-- Header: App branding -->
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <router-link to="/">
              <div
                class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
              >
                <!-- Replace with your app icon/logo -->
                <span class="text-sm font-bold">A</span>
              </div>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-semibold">App Name</span>
                <span class="truncate text-xs text-sidebar-foreground/60"
                  >Workspace</span
                >
              </div>
            </router-link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <!-- Main navigation -->
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Navigation</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <template v-for="item in mainNavItems" :key="item.path">
              <!-- Items with children: collapsible -->
              <Collapsible
                v-if="item.children?.length"
                as-child
                :default-open="isActive(item)"
              >
                <SidebarMenuItem>
                  <CollapsibleTrigger as-child>
                    <SidebarMenuButton :tooltip="item.title">
                      <component :is="item.icon" class="size-4" />
                      <span>{{ item.title }}</span>
                      <ChevronRight
                        class="ml-auto size-4 transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
                      />
                    </SidebarMenuButton>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <SidebarMenuSub>
                      <SidebarMenuSubItem
                        v-for="child in item.children"
                        :key="child.path"
                      >
                        <SidebarMenuSubButton
                          :is-active="route.path === child.path"
                          @click="navigate(child.path)"
                        >
                          <span>{{ child.title }}</span>
                          <Badge
                            v-if="child.badge"
                            variant="secondary"
                            class="ml-auto text-xs"
                          >
                            {{ child.badge }}
                          </Badge>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    </SidebarMenuSub>
                  </CollapsibleContent>
                </SidebarMenuItem>
              </Collapsible>

              <!-- Leaf items: direct navigation -->
              <SidebarMenuItem v-else>
                <SidebarMenuButton
                  :is-active="isActive(item)"
                  :tooltip="item.title"
                  @click="navigate(item.path)"
                >
                  <component :is="item.icon" class="size-4" />
                  <span>{{ item.title }}</span>
                  <Badge
                    v-if="item.badge"
                    variant="secondary"
                    class="ml-auto text-xs"
                  >
                    {{ item.badge }}
                  </Badge>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </template>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Secondary navigation (e.g., support, docs) -->
      <SidebarGroup v-if="secondaryNavItems.length" class="mt-auto">
        <SidebarGroupLabel>Support</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in secondaryNavItems" :key="item.path">
              <SidebarMenuButton
                :is-active="isActive(item)"
                :tooltip="item.title"
                @click="navigate(item.path)"
              >
                <component :is="item.icon" class="size-4" />
                <span>{{ item.title }}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <!-- Footer: User menu -->
    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <SidebarMenuButton
                size="lg"
                class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <Avatar class="h-8 w-8 rounded-lg">
                  <AvatarImage src="/avatar.jpg" alt="User" />
                  <AvatarFallback class="rounded-lg">U</AvatarFallback>
                </Avatar>
                <div class="grid flex-1 text-left text-sm leading-tight">
                  <span class="truncate font-semibold">User Name</span>
                  <span class="truncate text-xs">user@example.com</span>
                </div>
                <ChevronsUpDown class="ml-auto size-4" />
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              class="w-[--reka-dropdown-menu-trigger-width] min-w-56 rounded-lg"
              side="bottom"
              align="end"
              :side-offset="4"
            >
              <DropdownMenuItem @click="navigate('/profile')">
                <User class="mr-2 size-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem @click="navigate('/settings')">
                <Settings class="mr-2 size-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <LogOut class="mr-2 size-4" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
  </Sidebar>
</template>
```

---

## Navigation Config

`src/config/navigation.ts` — Derive nav items from vue-router config.

```typescript
import type { Component } from "vue";
import { routes } from "@/router";
import {
  LayoutDashboard,
  FolderKanban,
  Users,
  BarChart3,
  Settings,
  HelpCircle,
  FileText,
  Mail,
  Bell,
  Shield,
} from "lucide-vue-next";

export interface NavItem {
  title: string;
  path: string;
  icon: Component;
  badge?: string | number;
  children?: NavItem[];
}

// Map icon names (from route meta) to actual components
const iconMap: Record<string, Component> = {
  LayoutDashboard,
  FolderKanban,
  Users,
  BarChart3,
  Settings,
  HelpCircle,
  FileText,
  Mail,
  Bell,
  Shield,
};

/**
 * Build nav items from route records.
 *
 * Routes opt in to navigation via meta:
 *   meta: { nav: true, title: 'Dashboard', icon: 'LayoutDashboard', navGroup: 'main' }
 *
 * Routes with meta.nav = false or no meta.nav are excluded.
 * Nested route children become sub-items automatically.
 */
function buildNavItems(routeRecords: typeof routes, group: string): NavItem[] {
  const items: NavItem[] = [];

  for (const route of routeRecords) {
    const meta = route.meta as Record<string, any> | undefined;
    if (!meta?.nav || meta.navGroup !== group) continue;

    const item: NavItem = {
      title: meta.title || (route.name as string) || route.path,
      path: route.path,
      icon: iconMap[meta.icon] || LayoutDashboard,
      badge: meta.badge,
    };

    // Build children from nested routes
    if (route.children?.length) {
      const childItems = route.children
        .filter((child) => {
          const childMeta = child.meta as Record<string, any> | undefined;
          return childMeta?.nav !== false && child.path !== "";
        })
        .map((child) => {
          const childMeta = child.meta as Record<string, any> | undefined;
          return {
            title: childMeta?.title || (child.name as string) || child.path,
            path: `${route.path}/${child.path}`.replace(/\/+/g, "/"),
            icon: iconMap[childMeta?.icon || ""] || LayoutDashboard,
            badge: childMeta?.badge,
          };
        });

      if (childItems.length) {
        item.children = childItems;
      }
    }

    items.push(item);
  }

  return items;
}

export const mainNavItems = buildNavItems(routes, "main");
export const secondaryNavItems = buildNavItems(routes, "secondary");
```

### Route meta convention

Add meta to your routes to control sidebar rendering:

```typescript
// src/router/index.ts
const routes = [
  {
    path: "/",
    component: () => import("@/layouts/AppLayout.vue"),
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: {
          nav: true,
          navGroup: "main",
          title: "Dashboard",
          icon: "LayoutDashboard",
        },
      },
      {
        path: "projects",
        name: "Projects",
        component: () => import("@/views/Projects.vue"),
        meta: {
          nav: true,
          navGroup: "main",
          title: "Projects",
          icon: "FolderKanban",
          badge: 3, // Shows count badge
        },
        children: [
          {
            path: "active",
            name: "ActiveProjects",
            component: () => import("@/views/projects/Active.vue"),
            meta: { nav: true, title: "Active" },
          },
          {
            path: "archived",
            name: "ArchivedProjects",
            component: () => import("@/views/projects/Archived.vue"),
            meta: { nav: true, title: "Archived" },
          },
        ],
      },
      {
        path: "settings",
        name: "Settings",
        component: () => import("@/views/Settings.vue"),
        meta: {
          nav: true,
          navGroup: "secondary",
          title: "Settings",
          icon: "Settings",
        },
      },
    ],
  },
  // Auth routes — outside the layout, no sidebar
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
  },
];
```

---

## Router Updates

### Before (typical top-nav setup)

```typescript
// Old: flat routes, no layout wrapper
const routes = [
  { path: "/dashboard", component: Dashboard },
  { path: "/projects", component: Projects },
  { path: "/settings", component: Settings },
  { path: "/login", component: Login },
];
```

### After (layout-wrapped)

```typescript
// New: authenticated routes wrapped in AppLayout
const routes = [
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      // All sidebar-navigable routes go here
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { ... } },
      { path: 'projects', component: () => import('@/views/Projects.vue'), meta: { ... } },
      { path: 'settings', component: () => import('@/views/Settings.vue'), meta: { ... } },
    ],
  },
  // Routes that should NOT have sidebar
  { path: '/login', component: () => import('@/views/auth/Login.vue') },
  { path: '/register', component: () => import('@/views/auth/Register.vue') },
]
```

Key change: authenticated routes become `children` of a layout route. This is what makes `<router-view />` inside AppLayout work — it renders the matched child route.

---

## Mobile Responsive

shadcn-vue's Sidebar component handles mobile automatically:

- Below `md` breakpoint (768px), the sidebar becomes a **Sheet** (slide-out drawer)
- The `SidebarTrigger` becomes a hamburger menu button
- Clicking a nav item closes the sheet automatically
- The main content area takes full width

No extra code needed — this is built into the `Sidebar` component. Just make sure:

1. The viewport meta tag is set: `<meta name="viewport" content="width=device-width, initial-scale=1">`
2. You're not overriding the sidebar width with fixed CSS that prevents it from hiding
3. Content inside `SidebarInset` uses responsive Tailwind classes (e.g., `grid grid-cols-1 md:grid-cols-2`)
