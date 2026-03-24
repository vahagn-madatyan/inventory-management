<template>
  <Dialog
    :open="isOpen"
    @update:open="(val) => { if (!val) emit('close') }"
  >
    <DialogContent class="sm:max-w-[900px] max-h-[85vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>{{ t("tasks.title") }}</DialogTitle>
        <DialogDescription class="sr-only">
          {{ t("tasks.title") }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto space-y-6">
        <!-- Add Task Form -->
        <div class="rounded-lg border border-border bg-muted/50 p-4 space-y-4">
          <div class="space-y-2">
            <Label for="task-title">{{ t("tasks.taskTitle") }}</Label>
            <Input
              id="task-title"
              v-model="newTask.title"
              type="text"
              :placeholder="t('tasks.taskTitlePlaceholder')"
              @keyup.enter="handleAddTask"
            />
          </div>

          <div class="flex flex-col sm:flex-row gap-3 items-end">
            <div class="flex-1 space-y-2">
              <Label for="task-priority">{{ t("tasks.priority") }}</Label>
              <select
                id="task-priority"
                v-model="newTask.priority"
                class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <option value="high">{{ t("priority.high") }}</option>
                <option value="medium">{{ t("priority.medium") }}</option>
                <option value="low">{{ t("priority.low") }}</option>
              </select>
            </div>

            <div class="flex-1 space-y-2">
              <Label for="task-due-date">{{ t("tasks.dueDate") }}</Label>
              <Input
                id="task-due-date"
                v-model="newTask.dueDate"
                type="date"
              />
            </div>

            <Button
              @click="handleAddTask"
              :disabled="!newTask.title.trim() || !newTask.dueDate"
              class="shrink-0"
            >
              <Plus class="h-4 w-4" />
              {{ t("tasks.addTask") }}
            </Button>
          </div>
        </div>

        <!-- Divider -->
        <div class="border-t border-border" />

        <!-- Tasks List -->
        <div v-if="sortedTasks.length === 0" class="text-center py-12 text-muted-foreground text-base italic">
          {{ t("tasks.noTasks") }}
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="task in sortedTasks"
            :key="task.id"
            class="flex flex-col gap-2 rounded-lg border p-3 transition-colors hover:bg-muted/50"
            :class="{
              'border-l-4 border-l-red-500': task.priority === 'high',
              'border-l-4 border-l-amber-500': task.priority === 'medium',
              'border-l-4 border-l-blue-500': task.priority === 'low',
              'opacity-60': task.status === 'completed',
            }"
          >
            <!-- Task header row -->
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <button
                  @click="emit('toggle-task', task.id)"
                  class="shrink-0 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Check
                    v-if="task.status === 'completed'"
                    class="h-5 w-5 text-green-600"
                  />
                  <Circle v-else class="h-5 w-5" />
                </button>
                <span
                  class="text-sm font-semibold cursor-pointer select-none truncate"
                  :class="{
                    'line-through text-muted-foreground': task.status === 'completed',
                    'text-foreground': task.status !== 'completed',
                  }"
                  @click="emit('toggle-task', task.id)"
                >
                  {{ task.title }}
                </span>
              </div>
              <Button
                variant="destructive"
                size="icon-sm"
                @click="emit('delete-task', task.id)"
              >
                <Trash2 class="h-4 w-4" />
              </Button>
            </div>

            <!-- Task footer row -->
            <div class="flex items-center gap-2 pl-8">
              <Badge
                :class="{
                  'bg-red-100 text-red-800 border-red-200 hover:bg-red-100': task.priority === 'high',
                  'bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-100': task.priority === 'medium',
                  'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-100': task.priority === 'low',
                }"
                variant="outline"
              >
                {{ translatePriority(task.priority) }}
              </Badge>

              <span class="flex items-center gap-1 text-xs text-muted-foreground">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="text-muted-foreground/60">
                  <rect x="2" y="3" width="10" height="9" rx="1" stroke="currentColor" stroke-width="1.2" />
                  <path d="M4.5 1.5V4.5M9.5 1.5V4.5M2 6H12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
                </svg>
                {{ formatDueDate(task.dueDate) }}
              </span>

              <Badge
                class="ml-auto"
                :class="{
                  'bg-red-100 text-red-800 border-red-200 hover:bg-red-100': getStatusClass(task.dueDate, task.status) === 'overdue',
                  'bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-100': getStatusClass(task.dueDate, task.status) === 'urgent',
                  'bg-blue-100 text-blue-800 border-blue-200 hover:bg-blue-100': getStatusClass(task.dueDate, task.status) === 'upcoming',
                  'bg-green-100 text-green-800 border-green-200 hover:bg-green-100': getStatusClass(task.dueDate, task.status) === 'completed',
                }"
                variant="outline"
              >
                {{ getStatusText(task.dueDate, task.status) }}
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div class="flex justify-end pt-2 border-t border-border">
        <Button variant="secondary" @click="emit('close')">
          {{ t("profileDetails.close") }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

<script setup>
import { ref, computed } from "vue";
import { useI18n } from "../composables/useI18n";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2, Check, Circle } from "lucide-vue-next";

const { t, currentLocale } = useI18n();

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  tasks: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["close", "add-task", "delete-task", "toggle-task"]);

const newTask = ref({
  title: "",
  priority: "medium",
  dueDate: "",
});

const sortedTasks = computed(() => {
  return [...props.tasks];
});

const handleAddTask = () => {
  if (newTask.value.title.trim() && newTask.value.dueDate) {
    emit("add-task", {
      title: newTask.value.title.trim(),
      priority: newTask.value.priority,
      dueDate: newTask.value.dueDate,
    });
    newTask.value = {
      title: "",
      priority: "medium",
      dueDate: "",
    };
  }
};

const formatDueDate = (dateString) => {
  const date = new Date(dateString);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dueDate = new Date(date);
  dueDate.setHours(0, 0, 0, 0);

  const diffTime = dueDate - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  const isJapanese = currentLocale.value === "ja";

  if (diffDays === 0) return isJapanese ? "\u4ECA\u65E5" : "today";
  if (diffDays === 1) return isJapanese ? "\u660E\u65E5" : "tomorrow";
  if (diffDays === -1) return isJapanese ? "\u6628\u65E5" : "yesterday";
  if (diffDays < 0)
    return isJapanese
      ? `${Math.abs(diffDays)}\u65E5\u524D`
      : `${Math.abs(diffDays)} days ago`;
  if (diffDays < 7)
    return isJapanese ? `${diffDays}\u65E5\u5F8C` : `in ${diffDays} days`;

  const locale = isJapanese ? "ja-JP" : "en-US";
  return date.toLocaleDateString(locale, {
    month: "short",
    day: "numeric",
    year:
      date.getFullYear() !== today.getFullYear() ? "numeric" : undefined,
  });
};

const getStatusClass = (dueDate, status) => {
  if (status === "completed") return "completed";

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);

  const diffTime = due - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return "overdue";
  if (diffDays <= 1) return "urgent";
  return "upcoming";
};

const getStatusText = (dueDate, status) => {
  const isJapanese = currentLocale.value === "ja";

  if (status === "completed") return isJapanese ? "\u5B8C\u4E86" : "Completed";

  const statusClass = getStatusClass(dueDate, status);
  if (statusClass === "overdue") return isJapanese ? "\u671F\u9650\u8D85\u904E" : "Overdue";
  if (statusClass === "urgent")
    return isJapanese ? "\u3082\u3046\u3059\u3050\u671F\u9650" : "Due Soon";
  return isJapanese ? "\u4E88\u5B9A" : "Upcoming";
};

const translatePriority = (priority) => {
  const priorityMap = {
    high: t("priority.high"),
    medium: t("priority.medium"),
    low: t("priority.low"),
  };
  return priorityMap[priority] || priority;
};
</script>
