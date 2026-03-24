<template>
  <Dialog
    :open="isOpen"
    @update:open="(val) => { if (!val) emit('close') }"
  >
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Inventory Item Details</DialogTitle>
        <DialogDescription>
          Detailed stock and value information for this inventory item.
        </DialogDescription>
      </DialogHeader>

      <template v-if="inventoryItem">
        <!-- Item header -->
        <div class="flex items-center gap-4 pb-4 border-b border-border">
          <div
            class="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl text-white"
            :class="stockIconBgClass"
          >
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect
                x="8" y="12" width="32" height="28" rx="2"
                stroke="currentColor" stroke-width="2.5"
              />
              <path
                d="M16 8V16M32 8V16M8 20H40"
                stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
              />
              <path
                d="M16 28H32M16 34H24"
                stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
              />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-2xl font-bold text-foreground leading-tight">
              {{ translateProductName(inventoryItem.name) }}
            </h4>
            <p class="text-sm text-muted-foreground font-mono mt-1">
              SKU: {{ inventoryItem.sku }}
            </p>
          </div>
          <Badge :class="stockBadgeClass">
            {{ stockStatus }}
          </Badge>
        </div>

        <!-- Summary cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card class="border-2 border-blue-200 bg-blue-50">
            <CardContent class="p-4">
              <p class="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                Quantity on Hand
              </p>
              <p class="text-3xl font-bold text-foreground">
                {{ inventoryItem.quantity_on_hand }} units
              </p>
            </CardContent>
          </Card>
          <Card :class="summaryCardClass">
            <CardContent class="p-4">
              <p class="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                Stock Level
              </p>
              <p class="text-3xl font-bold text-foreground">
                {{ stockPercentage }}%
              </p>
              <p class="text-xs text-muted-foreground mt-0.5">vs. reorder point</p>
            </CardContent>
          </Card>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Category
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ inventoryItem.category }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Location
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ inventoryItem.location }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Reorder Point
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ inventoryItem.reorder_point }} units
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Units Remaining
            </span>
            <span
              class="text-sm font-medium"
              :class="inventoryItem.quantity_on_hand <= inventoryItem.reorder_point ? 'text-destructive' : 'text-emerald-600'"
            >
              {{ inventoryItem.quantity_on_hand - inventoryItem.reorder_point }} units
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Unit Cost
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ currencySymbol }}{{ inventoryItem.unit_cost.toFixed(2) }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Total Value
            </span>
            <span class="text-sm font-bold text-blue-600">
              {{ currencySymbol }}{{ totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Warehouse
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ translateWarehouse(inventoryItem.location) }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Status
            </span>
            <span>
              <Badge :class="stockBadgeClass">
                {{ stockStatus }}
              </Badge>
            </span>
          </div>
        </div>
      </template>

      <DialogFooter>
        <Button variant="outline" @click="emit('close')">Close</Button>
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
import { Button } from "@/components/ui/button";

const { currentCurrency, translateProductName, translateWarehouse } = useI18n();

const currencySymbol = computed(() => {
  return currentCurrency.value === "JPY" ? "\u00a5" : "$";
});

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  inventoryItem: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close"]);

const totalValue = computed(() => {
  if (!props.inventoryItem) return 0;
  return props.inventoryItem.quantity_on_hand * props.inventoryItem.unit_cost;
});

const stockPercentage = computed(() => {
  if (!props.inventoryItem || props.inventoryItem.reorder_point === 0) return 0;
  return Math.round(
    (props.inventoryItem.quantity_on_hand / props.inventoryItem.reorder_point) *
      100,
  );
});

const stockStatus = computed(() => {
  if (!props.inventoryItem) return "Unknown";
  if (
    props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point
  ) {
    return "Low Stock";
  } else if (
    props.inventoryItem.quantity_on_hand <=
    props.inventoryItem.reorder_point * 1.5
  ) {
    return "Adequate";
  } else {
    return "In Stock";
  }
});

const stockBadgeClass = computed(() => {
  const status = stockStatus.value;
  if (status === "Low Stock")
    return "border-transparent bg-red-100 text-red-800 hover:bg-red-100";
  if (status === "Adequate")
    return "border-transparent bg-amber-100 text-amber-800 hover:bg-amber-100";
  return "border-transparent bg-emerald-100 text-emerald-800 hover:bg-emerald-100";
});

const stockIconBgClass = computed(() => {
  const status = stockStatus.value;
  if (status === "Low Stock") return "bg-gradient-to-br from-red-500 to-red-600";
  if (status === "Adequate") return "bg-gradient-to-br from-amber-500 to-amber-600";
  return "bg-gradient-to-br from-emerald-500 to-emerald-600";
});

const summaryCardClass = computed(() => {
  const status = stockStatus.value;
  if (status === "Low Stock") return "border-2 border-red-200 bg-red-50";
  if (status === "Adequate") return "border-2 border-amber-200 bg-amber-50";
  return "border-2 border-emerald-200 bg-emerald-50";
});
</script>
