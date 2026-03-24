<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight">
        {{ t("restocking.title") }}
      </h1>
      <p class="text-sm text-muted-foreground">
        {{ t("restocking.description") }}
      </p>
    </div>

    <div v-if="loading" class="py-8 text-center text-muted-foreground">
      {{ t("common.loading") }}
    </div>
    <div v-else-if="error" class="py-8 text-center text-destructive">
      {{ error }}
    </div>

    <!-- Success State -->
    <div
      v-else-if="submitted && submittedOrder"
      class="flex justify-center py-8"
    >
      <Card class="max-w-[480px] w-full text-center">
        <CardContent class="pt-8 pb-8 space-y-6">
          <div
            class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 text-3xl font-bold"
          >
            &#10003;
          </div>
          <h3 class="text-xl font-bold tracking-tight">
            {{ t("restocking.orderSuccess") }}
          </h3>
          <div class="space-y-3">
            <div
              class="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3"
            >
              <span class="text-sm text-muted-foreground">{{
                t("restocking.orderNumber")
              }}</span>
              <span class="text-sm font-bold">{{
                submittedOrder.order_number
              }}</span>
            </div>
            <div
              class="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3"
            >
              <span class="text-sm text-muted-foreground">{{
                t("restocking.expectedDelivery")
              }}</span>
              <span class="text-sm font-bold">{{
                formatDate(submittedOrder.expected_delivery)
              }}</span>
            </div>
            <div
              class="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3"
            >
              <span class="text-sm text-muted-foreground">{{
                t("restocking.orderTotal")
              }}</span>
              <span class="text-sm font-bold">{{
                formatCurrency(submittedOrder.total_cost, currentCurrency)
              }}</span>
            </div>
          </div>
          <Button @click="resetForm" class="mt-2">
            {{ t("restocking.placeAnother") }}
          </Button>
        </CardContent>
      </Card>
    </div>

    <template v-else>
      <!-- Budget Control -->
      <Card>
        <CardHeader
          class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
          <CardTitle class="text-base font-semibold">{{
            t("restocking.budgetControl")
          }}</CardTitle>
          <span class="text-xl font-bold text-primary">{{
            formatCurrency(budget, currentCurrency)
          }}</span>
        </CardHeader>
        <CardContent class="space-y-4">
          <p class="text-sm text-muted-foreground">
            {{ t("restocking.setBudget") }}
          </p>
          <div class="flex items-center gap-4">
            <input
              type="range"
              class="flex-1 h-1.5 appearance-none rounded-full bg-muted outline-none cursor-pointer accent-primary [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:border-[3px] [&::-webkit-slider-thumb]:border-white [&::-webkit-slider-thumb]:shadow [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:hover:scale-110"
              :value="budget"
              @input="budget = Number($event.target.value)"
              min="0"
              max="50000"
              step="500"
            />
            <input
              type="number"
              class="w-[120px] rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-right focus:outline-none focus:ring-2 focus:ring-ring focus:bg-background transition-all"
              :value="budget"
              @input="budget = Number($event.target.value)"
              min="0"
              max="50000"
              step="500"
            />
          </div>
        </CardContent>
      </Card>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("restocking.recommendedItems") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1">
              {{ recommendations.length }}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("restocking.selectedItems") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1">
              {{ selectedList.length }}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("restocking.estimatedCost") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1 text-amber-600">
              {{ formatCurrency(runningTotal, currentCurrency) }}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("restocking.budgetRemaining") }}
            </p>
            <p
              class="text-2xl font-bold tracking-tight mt-1"
              :class="isOverBudget ? 'text-destructive' : 'text-emerald-600'"
            >
              {{ formatCurrency(budgetRemaining, currentCurrency) }}
            </p>
          </CardContent>
        </Card>
      </div>

      <!-- Recommendations Table -->
      <Card>
        <CardHeader
          class="flex flex-row items-center justify-between space-y-0 pb-4"
        >
          <CardTitle class="text-base font-semibold">
            {{ t("restocking.recommendedItems") }} ({{
              recommendations.length
            }})
          </CardTitle>
          <div class="flex gap-2">
            <Button variant="outline" size="sm" @click="selectAll">
              {{ t("restocking.selectAll") }}
            </Button>
            <Button variant="outline" size="sm" @click="deselectAll">
              {{ t("restocking.deselectAll") }}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div
            v-if="recommendations.length === 0"
            class="py-12 text-center text-muted-foreground"
          >
            {{ t("restocking.noRecommendations") }}
          </div>
          <div v-else class="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead class="w-[50px]">{{
                    t("restocking.table.select")
                  }}</TableHead>
                  <TableHead>{{ t("restocking.table.name") }}</TableHead>
                  <TableHead>{{ t("restocking.table.sku") }}</TableHead>
                  <TableHead>{{ t("restocking.table.source") }}</TableHead>
                  <TableHead>{{ t("restocking.table.quantity") }}</TableHead>
                  <TableHead>{{ t("restocking.table.unitCost") }}</TableHead>
                  <TableHead>{{ t("restocking.table.lineTotal") }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="rec in recommendations" :key="rec.sku">
                  <TableCell>
                    <input
                      type="checkbox"
                      :checked="selectedItems[rec.sku]?.selected"
                      @change="toggleItem(rec.sku)"
                      class="h-4 w-4 cursor-pointer accent-primary"
                    />
                  </TableCell>
                  <TableCell>{{ translateProductName(rec.name) }}</TableCell>
                  <TableCell class="font-semibold">{{ rec.sku }}</TableCell>
                  <TableCell>
                    <Badge
                      v-if="getSourceClass(rec.source) === 'info'"
                      class="bg-blue-500/10 text-blue-600"
                    >
                      {{ t("restocking.sources." + rec.source) }}
                    </Badge>
                    <Badge
                      v-else-if="getSourceClass(rec.source) === 'danger'"
                      class="bg-destructive/10 text-destructive"
                    >
                      {{ t("restocking.sources." + rec.source) }}
                    </Badge>
                    <Badge v-else class="bg-amber-500/10 text-amber-600">
                      {{ t("restocking.sources." + rec.source) }}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <input
                      type="number"
                      class="w-20 rounded-md border border-input bg-muted/50 px-2 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-ring focus:bg-background transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                      :value="selectedItems[rec.sku]?.quantity"
                      @input="updateQuantity(rec.sku, $event.target.value)"
                      min="1"
                      :disabled="!selectedItems[rec.sku]?.selected"
                    />
                  </TableCell>
                  <TableCell>{{
                    formatCurrency(rec.unit_cost, currentCurrency)
                  }}</TableCell>
                  <TableCell class="font-semibold">{{
                    formatCurrency(getLineTotal(rec), currentCurrency)
                  }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <!-- Budget Progress Bar -->
      <Card>
        <CardContent class="pt-6 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm font-semibold">{{
              t("restocking.budget")
            }}</span>
            <span
              class="text-sm font-semibold"
              :class="
                isOverBudget ? 'text-destructive' : 'text-muted-foreground'
              "
            >
              {{ formatCurrency(runningTotal, currentCurrency) }} /
              {{ formatCurrency(budget, currentCurrency) }}
            </span>
          </div>
          <div class="h-2.5 rounded-full bg-muted overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-300"
              :style="{ width: Math.min(spendRatio, 100) + '%' }"
              :class="{
                'bg-emerald-500': spendRatio < 80,
                'bg-amber-500': spendRatio >= 80 && spendRatio <= 100,
                'bg-destructive': spendRatio > 100,
              }"
            ></div>
          </div>
          <p v-if="isOverBudget" class="text-xs font-semibold text-destructive">
            {{ t("restocking.overBudget") }}:
            {{ formatCurrency(Math.abs(budgetRemaining), currentCurrency) }}
          </p>
        </CardContent>
      </Card>

      <!-- Footer -->
      <Card>
        <CardContent class="flex items-center justify-between py-4">
          <div class="flex items-center gap-4">
            <span class="text-lg font-bold">
              {{ formatCurrency(runningTotal, currentCurrency) }} /
              {{ formatCurrency(budget, currentCurrency) }}
            </span>
            <span
              v-if="isOverBudget"
              class="text-xs font-semibold text-destructive"
            >
              {{ t("restocking.overBudget") }}
            </span>
          </div>
          <Button size="lg" :disabled="!canSubmit" @click="submitOrder">
            {{
              submitting
                ? t("restocking.submitting")
                : t("restocking.placeOrder")
            }}
          </Button>
        </CardContent>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { api } from "../api";
import { formatCurrency } from "../utils/currency";
import { useI18n } from "../composables/useI18n";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const { t, currentCurrency, translateProductName } = useI18n();

const budget = ref(10000);
const recommendations = ref([]);
const selectedItems = reactive({});
const loading = ref(true);
const error = ref(null);
const submitting = ref(false);
const submitted = ref(false);
const submittedOrder = ref(null);

// Helpers
const round = (n) => Math.round(n * 100) / 100;

const getLineTotal = (rec) => {
  if (selectedItems[rec.sku]?.selected) {
    return round(selectedItems[rec.sku].quantity * rec.unit_cost);
  }
  return 0;
};

// Computed
const selectedList = computed(() => {
  return recommendations.value
    .filter((rec) => selectedItems[rec.sku]?.selected)
    .map((rec) => ({
      ...rec,
      quantity: selectedItems[rec.sku].quantity,
      line_total: round(selectedItems[rec.sku].quantity * rec.unit_cost),
    }));
});

const runningTotal = computed(() =>
  selectedList.value.reduce((sum, item) => sum + item.line_total, 0),
);
const budgetRemaining = computed(() => budget.value - runningTotal.value);
const isOverBudget = computed(() => runningTotal.value > budget.value);
const canSubmit = computed(
  () =>
    selectedList.value.length > 0 && !isOverBudget.value && !submitting.value,
);
const spendRatio = computed(() =>
  budget.value > 0 ? (runningTotal.value / budget.value) * 100 : 0,
);

// Methods
const updateQuantity = (sku, newQty) => {
  if (selectedItems[sku]) {
    selectedItems[sku].quantity = Math.max(1, parseInt(newQty) || 1);
  }
};

const toggleItem = (sku) => {
  if (selectedItems[sku]) {
    selectedItems[sku].selected = !selectedItems[sku].selected;
  }
};

const selectAll = () => {
  Object.keys(selectedItems).forEach((sku) => {
    selectedItems[sku].selected = true;
  });
};

const deselectAll = () => {
  Object.keys(selectedItems).forEach((sku) => {
    selectedItems[sku].selected = false;
  });
};

const resetForm = () => {
  submitted.value = false;
  submittedOrder.value = null;
  loadRecommendations();
};

const getSourceClass = (source) => {
  return (
    { demand: "info", low_stock: "danger", both: "warning" }[source] || "info"
  );
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

// Data loading
const loadRecommendations = async () => {
  try {
    loading.value = true;
    error.value = null;
    recommendations.value = await api.getRestockingRecommendations();
    // Clear previous selections
    Object.keys(selectedItems).forEach((key) => delete selectedItems[key]);
    // Auto-select all items
    recommendations.value.forEach((rec) => {
      selectedItems[rec.sku] = { selected: true, quantity: rec.quantity };
    });
  } catch (err) {
    error.value = "Failed to load recommendations: " + err.message;
  } finally {
    loading.value = false;
  }
};

// Submit
const submitOrder = async () => {
  try {
    submitting.value = true;
    const orderData = {
      items: selectedList.value,
      total_cost: round(runningTotal.value),
      budget: budget.value,
    };
    submittedOrder.value = await api.submitRestockingOrder(orderData);
    submitted.value = true;
  } catch (err) {
    error.value = "Failed to submit order: " + err.message;
  } finally {
    submitting.value = false;
  }
};

onMounted(loadRecommendations);
</script>
