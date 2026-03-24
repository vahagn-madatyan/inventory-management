<template>
  <Dialog
    :open="isOpen"
    @update:open="
      (val) => {
        if (!val) emit('close');
      }
    "
  >
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Product Details</DialogTitle>
        <DialogDescription>
          Overview of product performance and stock information.
        </DialogDescription>
      </DialogHeader>

      <template v-if="product">
        <!-- Product header -->
        <div class="flex items-center gap-4 pb-4 border-b border-border">
          <div
            class="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white"
          >
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect
                x="8"
                y="12"
                width="32"
                height="28"
                rx="2"
                stroke="currentColor"
                stroke-width="2.5"
              />
              <path
                d="M16 8V16M32 8V16M8 20H40"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
              />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-2xl font-bold text-foreground leading-tight">
              {{ product.name }}
            </h4>
            <p class="text-sm text-muted-foreground font-mono mt-1">
              SKU: {{ product.sku }}
            </p>
          </div>
          <Badge :class="getStockBadgeClasses(product.stockLevel)">
            {{ product.stockLevel }}
          </Badge>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              Category
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ product.category }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              Warehouse
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ product.warehouse }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              Units Ordered
            </span>
            <span class="text-sm font-medium text-foreground">
              {{ product.unitsOrdered }}
            </span>
          </div>

          <div class="flex flex-col gap-1">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              Total Revenue
            </span>
            <span class="text-sm font-bold text-blue-600">
              {{ currencySymbol }}{{ product.revenue.toLocaleString() }}
            </span>
          </div>

          <Card class="md:col-span-2 border-2 border-muted">
            <CardContent class="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="flex flex-col gap-1">
                <span
                  class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                >
                  Current Stock
                </span>
                <span class="text-sm font-medium text-foreground">
                  {{ product.quantityOnHand }} units
                </span>
              </div>
              <div class="flex flex-col gap-1">
                <span
                  class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                >
                  Reorder Point
                </span>
                <span class="text-sm font-medium text-foreground">
                  {{ product.reorderPoint }} units
                </span>
              </div>
              <div class="flex flex-col gap-1">
                <span
                  class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                >
                  First Order Date
                </span>
                <span class="text-sm font-medium text-foreground">
                  {{ formatDate(product.firstOrderDate) }}
                </span>
              </div>
              <div class="flex flex-col gap-1">
                <span
                  class="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                >
                  Stock Status
                </span>
                <span>
                  <Badge :class="getStockBadgeClasses(product.stockLevel)">
                    {{ product.stockLevel }}
                  </Badge>
                </span>
              </div>
            </CardContent>
          </Card>
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

const { currentCurrency } = useI18n();

const currencySymbol = computed(() => {
  return currentCurrency.value === "JPY" ? "\u00a5" : "$";
});

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  product: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close"]);

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const getStockBadgeClasses = (stockLevel) => {
  if (stockLevel === "In Stock")
    return "border-transparent bg-emerald-100 text-emerald-800 hover:bg-emerald-100";
  if (stockLevel === "Low Stock")
    return "border-transparent bg-amber-100 text-amber-800 hover:bg-amber-100";
  if (stockLevel === "Out of Stock")
    return "border-transparent bg-red-100 text-red-800 hover:bg-red-100";
  return "border-transparent bg-blue-100 text-blue-800 hover:bg-blue-100";
};
</script>
