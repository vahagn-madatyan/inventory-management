<template>
  <Dialog
    :open="isOpen"
    @update:open="(val) => { if (!val) emit('close') }"
  >
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Inventory Shortage Details</DialogTitle>
        <DialogDescription>
          Detailed breakdown of the inventory shortage for this backlog item.
        </DialogDescription>
      </DialogHeader>

      <template v-if="backlogItem">
        <!-- Shortage header -->
        <div class="flex items-center gap-5 pb-4 border-b border-border">
          <div
            class="flex-shrink-0 w-16 h-16 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center text-white"
          >
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <path
                d="M24 8L24 28M24 34L24 36"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="round"
              />
              <circle
                cx="24"
                cy="24"
                r="18"
                stroke="currentColor"
                stroke-width="3"
              />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-2xl font-bold text-foreground truncate">
              {{ translateProductName(backlogItem.item_name) }}
            </h4>
            <div class="text-sm text-muted-foreground font-mono">
              SKU: {{ backlogItem.item_sku }}
            </div>
          </div>
          <Badge :variant="priorityVariant" class="flex-shrink-0 uppercase tracking-wide">
            {{ backlogItem.priority }} Priority
          </Badge>
        </div>

        <!-- Summary cards -->
        <div class="grid grid-cols-2 gap-4">
          <Card class="border-2 border-red-200 bg-red-50">
            <CardContent class="p-5">
              <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
                Shortage Amount
              </div>
              <div class="text-3xl font-bold text-red-600">
                {{ shortage }} units
              </div>
            </CardContent>
          </Card>
          <Card class="border-2 border-orange-200 bg-amber-50">
            <CardContent class="p-5">
              <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
                Days Delayed
              </div>
              <div class="text-3xl font-bold text-amber-500">
                {{ backlogItem.days_delayed }} days
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Order ID
            </div>
            <div class="text-sm font-medium font-mono text-blue-600">
              {{ backlogItem.order_id }}
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Item SKU
            </div>
            <div class="text-sm font-medium font-mono text-blue-600">
              {{ backlogItem.item_sku }}
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Quantity Needed
            </div>
            <div class="text-sm font-medium text-foreground">
              {{ backlogItem.quantity_needed }} units
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Quantity Available
            </div>
            <div class="text-sm font-medium text-foreground">
              {{ backlogItem.quantity_available }} units
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Expected Date
            </div>
            <div class="text-sm font-medium text-foreground">
              {{ formatDate(backlogItem.expected_date) }}
            </div>
          </div>

          <div class="flex flex-col gap-1">
            <div class="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Status
            </div>
            <div>
              <Badge variant="destructive">Backordered</Badge>
            </div>
          </div>
        </div>
      </template>

      <DialogFooter>
        <button
          class="px-5 py-2 bg-secondary text-secondary-foreground border border-border rounded-lg text-sm font-medium hover:bg-accent transition-colors"
          @click="emit('close')"
        >
          Close
        </button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "../composables/useI18n";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const { translateProductName } = useI18n();

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  backlogItem: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close"]);

const shortage = computed(() => {
  if (!props.backlogItem) return 0;
  return (
    props.backlogItem.quantity_needed - props.backlogItem.quantity_available
  );
});

const priorityVariant = computed(() => {
  if (!props.backlogItem) return "outline";
  switch (props.backlogItem.priority) {
    case "high":
      return "destructive";
    case "medium":
      return "secondary";
    case "low":
      return "outline";
    default:
      return "outline";
  }
});

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};
</script>
