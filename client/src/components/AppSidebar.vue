<script setup>
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "@/composables/useI18n";
import { useAuth } from "@/composables/useAuth";
import { useModals } from "@/composables/useModals";
import { mainNavItems, secondaryNavItems } from "@/config/navigation.js";
import { ChevronsUpDown, LogOut, User, ListTodo } from "lucide-vue-next";

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
} from "@/components/ui/sidebar";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const { currentUser } = useAuth();
const { showProfileDetails, showTasks } = useModals();

function getTitle(item) {
  return item.titleKey ? t(item.titleKey) : item.fallbackTitle;
}

function isActive(path) {
  if (path === "/") {
    return route.path === "/";
  }
  return route.path === path || route.path.startsWith(path + "/");
}

function getInitials() {
  const name = currentUser.value.name;
  if (!name) return "";
  const parts = name.split(" ");
  if (parts.length >= 2) {
    return parts[0][0] + parts[parts.length - 1][0];
  }
  return parts[0][0];
}

function logout() {
  alert("Logged out");
}
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as="router-link" to="/">
            <div
              class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
            >
              CC
            </div>
            <div class="grid flex-1 text-left text-sm leading-tight">
              <span class="truncate font-semibold">{{
                t("nav.companyName") || "Catalyst Components"
              }}</span>
              <span class="truncate text-xs">{{
                t("nav.subtitle") || "Inventory Management"
              }}</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <SidebarContent>
      <!-- Main navigation group -->
      <SidebarGroup>
        <SidebarGroupLabel>Navigation</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in mainNavItems" :key="item.path">
              <SidebarMenuButton
                :is-active="isActive(item.path)"
                :tooltip="getTitle(item)"
                @click="router.push(item.path)"
              >
                <component :is="item.icon" class="size-4" />
                <span>{{ getTitle(item) }}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Secondary navigation group -->
      <SidebarGroup v-if="secondaryNavItems.length" class="mt-auto">
        <SidebarGroupLabel>Other</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in secondaryNavItems" :key="item.path">
              <SidebarMenuButton
                :is-active="isActive(item.path)"
                :tooltip="getTitle(item)"
                @click="router.push(item.path)"
              >
                <component :is="item.icon" class="size-4" />
                <span>{{ getTitle(item) }}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

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
                  <AvatarFallback class="rounded-lg">{{
                    getInitials()
                  }}</AvatarFallback>
                </Avatar>
                <div class="grid flex-1 text-left text-sm leading-tight">
                  <span class="truncate font-semibold">{{
                    currentUser.name
                  }}</span>
                  <span class="truncate text-xs">{{ currentUser.email }}</span>
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
              <DropdownMenuItem @click="showProfileDetails = true">
                <User class="mr-2 size-4" />
                Profile Details
              </DropdownMenuItem>
              <DropdownMenuItem @click="showTasks = true">
                <ListTodo class="mr-2 size-4" />
                My Tasks
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="logout">
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
