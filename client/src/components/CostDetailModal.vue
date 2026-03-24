<template>
  <Dialog
    :open="isOpen"
    @update:open="
      (val) => {
        if (!val) emit('close');
      }
    "
  >
    <DialogContent class="max-w-xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ costData?.month }} Cost Breakdown</DialogTitle>
        <DialogDescription>
          Detailed cost analysis for the selected period.
        </DialogDescription>
      </DialogHeader>

      <template v-if="costData">
        <!-- Total cost summary -->
        <Card
          class="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0"
        >
          <CardContent class="p-6 text-center">
            <div
              class="text-sm font-semibold uppercase tracking-widest opacity-90 mb-2"
            >
              Total Costs
            </div>
            <div class="text-4xl font-bold">
              {{ currencySymbol }}{{ totalCosts.toLocaleString() }}
            </div>
          </CardContent>
        </Card>

        <!-- Cost breakdown items -->
        <div class="flex flex-col gap-4">
          <!-- Procurement -->
          <Card class="border-2 border-blue-200 bg-blue-50">
            <CardContent class="p-5">
              <div class="flex items-center gap-4 mb-3">
                <div
                  class="flex-shrink-0 w-12 h-12 rounded-xl bg-blue-500 text-white flex items-center justify-center"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect
                      x="4"
                      y="6"
                      width="16"
                      height="14"
                      rx="2"
                      stroke="currentColor"
                      stroke-width="2"
                    />
                    <path
                      d="M8 6V4M16 6V4M4 10H20"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="font-semibold text-foreground">Procurement</div>
                  <div class="text-2xl font-bold text-foreground">
                    {{ currencySymbol
                    }}{{ costData.procurement.toLocaleString() }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div
                  class="flex-1 h-2 bg-blue-200 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full bg-blue-500 rounded-full transition-all duration-500"
                    :style="{ width: getProcurementPercentage() + '%' }"
                  />
                </div>
                <span
                  class="text-sm text-muted-foreground font-medium whitespace-nowrap"
                >
                  {{ getProcurementPercentage() }}% of total
                </span>
              </div>
            </CardContent>
          </Card>

          <!-- Operational -->
          <Card class="border-2 border-violet-200 bg-violet-50">
            <CardContent class="p-5">
              <div class="flex items-center gap-4 mb-3">
                <div
                  class="flex-shrink-0 w-12 h-12 rounded-xl bg-violet-500 text-white flex items-center justify-center"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle
                      cx="12"
                      cy="12"
                      r="8"
                      stroke="currentColor"
                      stroke-width="2"
                    />
                    <path
                      d="M12 8V12L15 15"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="font-semibold text-foreground">Operational</div>
                  <div class="text-2xl font-bold text-foreground">
                    {{ currencySymbol
                    }}{{ costData.operational.toLocaleString() }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div
                  class="flex-1 h-2 bg-violet-200 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full bg-violet-500 rounded-full transition-all duration-500"
                    :style="{ width: getOperationalPercentage() + '%' }"
                  />
                </div>
                <span
                  class="text-sm text-muted-foreground font-medium whitespace-nowrap"
                >
                  {{ getOperationalPercentage() }}% of total
                </span>
              </div>
            </CardContent>
          </Card>

          <!-- Labor -->
          <Card class="border-2 border-green-200 bg-green-50">
            <CardContent class="p-5">
              <div class="flex items-center gap-4 mb-3">
                <div
                  class="flex-shrink-0 w-12 h-12 rounded-xl bg-emerald-500 text-white flex items-center justify-center"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle
                      cx="12"
                      cy="8"
                      r="4"
                      stroke="currentColor"
                      stroke-width="2"
                    />
                    <path
                      d="M6 20C6 16.6863 8.68629 14 12 14C15.3137 14 18 16.6863 18 20"
                      stroke="currentColor"
                      stroke-width="2"
                    />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="font-semibold text-foreground">Labor</div>
                  <div class="text-2xl font-bold text-foreground">
                    {{ currencySymbol }}{{ costData.labor.toLocaleString() }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div
                  class="flex-1 h-2 bg-green-200 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full bg-emerald-500 rounded-full transition-all duration-500"
                    :style="{ width: getLaborPercentage() + '%' }"
                  />
                </div>
                <span
                  class="text-sm text-muted-foreground font-medium whitespace-nowrap"
                >
                  {{ getLaborPercentage() }}% of total
                </span>
              </div>
            </CardContent>
          </Card>

          <!-- Overhead -->
          <Card class="border-2 border-yellow-200 bg-amber-50">
            <CardContent class="p-5">
              <div class="flex items-center gap-4 mb-3">
                <div
                  class="flex-shrink-0 w-12 h-12 rounded-xl bg-amber-500 text-white flex items-center justify-center"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9 21 9 18 9 16C9 14 10 14 12 14C14 14 15 14 15 16C15 18 15 21 15 21M9 21H15"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="font-semibold text-foreground">Overhead</div>
                  <div class="text-2xl font-bold text-foreground">
                    {{ currencySymbol }}{{ costData.overhead.toLocaleString() }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div
                  class="flex-1 h-2 bg-yellow-200 rounded-full overflow-hidden"
                >
                  <div
                    class="h-full bg-amber-500 rounded-full transition-all duration-500"
                    :style="{ width: getOverheadPercentage() + '%' }"
                  />
                </div>
                <span
                  class="text-sm text-muted-foreground font-medium whitespace-nowrap"
                >
                  {{ getOverheadPercentage() }}% of total
                </span>
              </div>
            </CardContent>
          </Card>
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
import { Card, CardContent } from "@/components/ui/card";

const { currentCurrency } = useI18n();

const currencySymbol = computed(() => {
  return currentCurrency.value === "JPY" ? "\u00A5" : "$";
});

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  costData: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close"]);

const totalCosts = computed(() => {
  if (!props.costData) return 0;
  return (
    props.costData.procurement +
    props.costData.operational +
    props.costData.labor +
    props.costData.overhead
  );
});

const getProcurementPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0;
  return ((props.costData.procurement / totalCosts.value) * 100).toFixed(1);
};

const getOperationalPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0;
  return ((props.costData.operational / totalCosts.value) * 100).toFixed(1);
};

const getLaborPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0;
  return ((props.costData.labor / totalCosts.value) * 100).toFixed(1);
};

const getOverheadPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0;
  return ((props.costData.overhead / totalCosts.value) * 100).toFixed(1);
};
</script>
