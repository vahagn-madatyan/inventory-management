<script setup>
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'
import AppSidebar from '@/components/AppSidebar.vue'
import FilterBar from '@/components/FilterBar.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import ProfileDetailsModal from '@/components/ProfileDetailsModal.vue'
import TasksModal from '@/components/TasksModal.vue'
import { useModals } from '@/composables/useModals'

const { showProfileDetails, showTasks, tasks, addTask, deleteTask, toggleTask } = useModals()
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4">
        <SidebarTrigger class="-ml-2 h-8 w-8" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <div class="flex-1">
          <FilterBar />
        </div>
        <LanguageSwitcher />
      </header>
      <main class="flex-1 overflow-auto p-6">
        <router-view />
      </main>
    </SidebarInset>
  </SidebarProvider>

  <ProfileDetailsModal
    :is-open="showProfileDetails"
    @close="showProfileDetails = false"
  />

  <TasksModal
    :is-open="showTasks"
    :tasks="tasks"
    @close="showTasks = false"
    @add-task="addTask"
    @delete-task="deleteTask"
    @toggle-task="toggleTask"
  />
</template>
