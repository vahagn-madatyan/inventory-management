<template>
  <Dialog
    :open="isOpen"
    @update:open="
      (val) => {
        if (!val) emit('close');
      }
    "
  >
    <DialogContent class="sm:max-w-[600px]">
      <DialogHeader>
        <DialogTitle>{{ t("profileDetails.title") }}</DialogTitle>
        <DialogDescription class="sr-only">
          {{ t("profileDetails.title") }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col gap-6">
        <!-- Avatar section -->
        <div
          class="flex flex-col items-center gap-3 pb-6 border-b border-border"
        >
          <Avatar
            size="lg"
            shape="circle"
            class="bg-gradient-to-br from-blue-600 to-blue-800 text-white font-bold shadow-md"
          >
            <AvatarFallback
              class="bg-transparent text-white text-3xl font-bold"
            >
              {{ getInitials(currentUser.name) }}
            </AvatarFallback>
          </Avatar>
          <h4 class="text-2xl font-bold text-foreground">
            {{ currentUser.name }}
          </h4>
          <p class="text-sm text-muted-foreground">
            {{ currentUser.jobTitle }}
          </p>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {{ t("profileDetails.email") }}
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ currentUser.email }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {{ t("profileDetails.department") }}
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ currentUser.department }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {{ t("profileDetails.location") }}
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ currentUser.location }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {{ t("profileDetails.phone") }}
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ currentUser.phone }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {{ t("profileDetails.joinDate") }}
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ formatDate(currentUser.joinDate) }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              {{ t("profileDetails.employeeId") }}
            </span>
            <span class="text-sm font-medium text-foreground">
              CC-{{ currentUser.id.toString().padStart(5, "0") }}
            </span>
          </div>
        </div>
      </div>

      <div class="flex justify-end pt-2">
        <Button variant="secondary" @click="emit('close')">
          {{ t("profileDetails.close") }}
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

<script setup>
import { useAuth } from "../composables/useAuth";
import { useI18n } from "../composables/useI18n";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";

const { currentUser, getInitials } = useAuth();
const { t, currentLocale } = useI18n();

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close"]);

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const locale = currentLocale.value === "ja" ? "ja-JP" : "en-US";
  return date.toLocaleDateString(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};
</script>
