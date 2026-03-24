<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight">
        {{ t("finance.title") }}
      </h1>
      <p class="text-sm text-muted-foreground">
        {{ t("finance.description") }}
      </p>
    </div>

    <div v-if="loading" class="py-8 text-center text-muted-foreground">
      {{ t("common.loading") }}
    </div>
    <div v-else-if="error" class="py-8 text-center text-destructive">
      {{ error }}
    </div>
    <div v-else class="space-y-6">
      <!-- Revenue & Financial KPIs -->
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card class="border-l-4 border-l-slate-900">
          <CardHeader class="pb-2">
            <CardDescription>{{ t("finance.totalRevenue") }}</CardDescription>
            <CardTitle class="text-2xl">{{
              formatCurrency(revenueMetrics.totalRevenue)
            }}</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="mt-1 flex items-center gap-1 text-sm text-emerald-600">
              <span class="text-base font-bold">↑</span>
              {{
                t("finance.fromOrders", { count: revenueMetrics.orderCount })
              }}
            </p>
          </CardContent>
        </Card>

        <Card class="border-l-4 border-l-red-500">
          <CardHeader class="pb-2">
            <CardDescription>{{ t("finance.totalCosts") }}</CardDescription>
            <CardTitle class="text-2xl">{{
              formatCurrency(totalCosts)
            }}</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="mt-1 text-xs text-muted-foreground">
              {{ t("finance.costBreakdown") }}
            </p>
          </CardContent>
        </Card>

        <Card class="border-l-4 border-l-blue-500">
          <CardHeader class="pb-2">
            <CardDescription>{{ t("finance.netProfit") }}</CardDescription>
            <CardTitle class="text-2xl">{{
              formatCurrency(netProfit)
            }}</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="mt-1 text-xs text-muted-foreground">
              {{ profitMargin }}% {{ t("finance.margin") }}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardDescription>{{ t("finance.avgOrderValue") }}</CardDescription>
            <CardTitle class="text-2xl">{{
              formatCurrency(revenueMetrics.avgOrderValue)
            }}</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="mt-1 text-xs text-muted-foreground">
              {{ t("finance.perOrderRevenue") }}
            </p>
          </CardContent>
        </Card>
      </div>

      <!-- Monthly Revenue vs Cost Chart -->
      <Card>
        <CardHeader
          class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
          <CardTitle class="text-base font-semibold">{{
            t("finance.revenueVsCosts.title")
          }}</CardTitle>
          <div class="flex gap-4 text-sm">
            <span class="flex items-center gap-2 text-muted-foreground">
              <span class="inline-block h-3 w-3 rounded-sm bg-slate-900"></span>
              {{ t("finance.revenueVsCosts.revenue") }}
            </span>
            <span class="flex items-center gap-2 text-muted-foreground">
              <span class="inline-block h-3 w-3 rounded-sm bg-red-500"></span>
              {{ t("finance.revenueVsCosts.costs") }}
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <div class="py-4">
            <div class="flex gap-6 h-[350px]">
              <div
                class="flex flex-col justify-between pr-4 text-xs text-slate-400 border-r border-slate-200"
              >
                <span>{{ currencySymbol }}{{ maxRevenueValue }}K</span>
                <span
                  >{{ currencySymbol
                  }}{{ Math.round(maxRevenueValue * 0.75) }}K</span
                >
                <span
                  >{{ currencySymbol
                  }}{{ Math.round(maxRevenueValue * 0.5) }}K</span
                >
                <span
                  >{{ currencySymbol
                  }}{{ Math.round(maxRevenueValue * 0.25) }}K</span
                >
                <span>{{ currencySymbol }}0</span>
              </div>
              <div class="flex flex-1 items-end justify-around gap-2">
                <div
                  v-for="month in monthlyRevenue"
                  :key="month.month"
                  class="flex flex-col items-center flex-1 h-full"
                >
                  <div
                    class="flex w-full max-w-[80px] gap-1.5 justify-center items-end h-full pb-8"
                  >
                    <div
                      class="w-1/2 max-w-[30px] rounded-t-md bg-slate-900 transition-all duration-300 cursor-pointer min-h-[4px] hover:opacity-80 hover:scale-y-105"
                      :style="{
                        height: getRevenueBarHeight(month.revenue) + '%',
                      }"
                      :title="`Revenue: ${currencySymbol}${month.revenue.toLocaleString()}`"
                    ></div>
                    <div
                      class="w-1/2 max-w-[30px] rounded-t-md bg-red-500 transition-all duration-300 cursor-pointer min-h-[4px] hover:opacity-80 hover:scale-y-105"
                      :style="{
                        height: getRevenueBarHeight(month.costs) + '%',
                      }"
                      :title="`Costs: ${currencySymbol}${month.costs.toLocaleString()}`"
                    ></div>
                  </div>
                  <span
                    class="mt-2 text-xs font-semibold text-muted-foreground"
                    >{{ translateMonth(month.month) }}</span
                  >
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Monthly Cost Flow Chart -->
      <Card>
        <CardHeader
          class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
          <CardTitle class="text-base font-semibold">{{
            t("finance.monthlyCostFlow.title")
          }}</CardTitle>
          <div class="flex gap-4 text-sm">
            <span class="flex items-center gap-2 text-muted-foreground">
              <span class="inline-block h-3 w-3 rounded-sm bg-blue-500"></span>
              {{ t("finance.monthlyCostFlow.procurement") }}
            </span>
            <span class="flex items-center gap-2 text-muted-foreground">
              <span
                class="inline-block h-3 w-3 rounded-sm bg-violet-500"
              ></span>
              {{ t("finance.monthlyCostFlow.operational") }}
            </span>
            <span class="flex items-center gap-2 text-muted-foreground">
              <span
                class="inline-block h-3 w-3 rounded-sm bg-emerald-500"
              ></span>
              {{ t("finance.monthlyCostFlow.labor") }}
            </span>
            <span class="flex items-center gap-2 text-muted-foreground">
              <span class="inline-block h-3 w-3 rounded-sm bg-amber-500"></span>
              {{ t("finance.monthlyCostFlow.overhead") }}
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <div class="py-4">
            <div class="flex gap-6 h-[350px]">
              <div
                class="flex flex-col justify-between pr-4 text-xs text-slate-400 border-r border-slate-200"
              >
                <span>{{ currencySymbol }}25K</span>
                <span>{{ currencySymbol }}20K</span>
                <span>{{ currencySymbol }}15K</span>
                <span>{{ currencySymbol }}10K</span>
                <span>{{ currencySymbol }}5K</span>
                <span>{{ currencySymbol }}0</span>
              </div>
              <div class="flex flex-1 items-end justify-around gap-2">
                <div
                  v-for="month in monthlySpending"
                  :key="month.month"
                  class="flex flex-col items-center flex-1 h-full"
                >
                  <div
                    class="flex w-full max-w-[60px] flex-col-reverse items-stretch h-full pb-8 cursor-pointer transition-opacity duration-200 hover:opacity-85"
                    @click="showCostDetail(month)"
                  >
                    <div
                      class="w-full rounded-b-md bg-blue-500 transition-all duration-300 cursor-pointer"
                      :style="{ height: getBarHeight(month.procurement) + '%' }"
                      :title="`Procurement: ${currencySymbol}${month.procurement.toLocaleString()}`"
                    ></div>
                    <div
                      class="w-full bg-violet-500 transition-all duration-300 cursor-pointer"
                      :style="{ height: getBarHeight(month.operational) + '%' }"
                      :title="`Operational: ${currencySymbol}${month.operational.toLocaleString()}`"
                    ></div>
                    <div
                      class="w-full bg-emerald-500 transition-all duration-300 cursor-pointer"
                      :style="{ height: getBarHeight(month.labor) + '%' }"
                      :title="`Labor: ${currencySymbol}${month.labor.toLocaleString()}`"
                    ></div>
                    <div
                      class="w-full rounded-t-md bg-amber-500 transition-all duration-300 cursor-pointer"
                      :style="{ height: getBarHeight(month.overhead) + '%' }"
                      :title="`Overhead: ${currencySymbol}${month.overhead.toLocaleString()}`"
                    ></div>
                  </div>
                  <span
                    class="mt-2 text-xs font-semibold text-muted-foreground"
                    >{{ translateMonth(month.month) }}</span
                  >
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div class="grid gap-6 lg:grid-cols-2">
        <!-- Category Spending Breakdown -->
        <Card>
          <CardHeader>
            <CardTitle class="text-base font-semibold">{{
              t("finance.categorySpending.title")
            }}</CardTitle>
          </CardHeader>
          <CardContent class="space-y-5">
            <div
              v-for="category in categorySpending"
              :key="category.category"
              class="space-y-2"
            >
              <div class="flex items-center justify-between">
                <span class="font-semibold text-slate-900">{{
                  translateCategory(category.category)
                }}</span>
                <span class="text-lg font-bold text-blue-600"
                  >{{ currencySymbol
                  }}{{ category.amount.toLocaleString() }}</span
                >
              </div>
              <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
                  :style="{ width: category.percentage + '%' }"
                ></div>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-muted-foreground"
                  >{{ category.percentage }}%
                  {{ t("finance.categorySpending.ofTotal") }}</span
                >
                <span
                  class="font-semibold"
                  :class="{
                    'text-emerald-600': category.change > 0,
                    'text-red-600': category.change < 0,
                  }"
                >
                  {{ category.change > 0 ? "+" : "" }}{{ category.change }}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Recent Transactions -->
        <Card class="flex flex-col">
          <CardHeader>
            <CardTitle class="text-base font-semibold">{{
              t("finance.transactions.title")
            }}</CardTitle>
          </CardHeader>
          <CardContent class="overflow-y-auto max-h-[400px]">
            <div class="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{{ t("finance.transactions.id") }}</TableHead>
                    <TableHead>{{
                      t("finance.transactions.description")
                    }}</TableHead>
                    <TableHead>{{
                      t("finance.transactions.vendor")
                    }}</TableHead>
                    <TableHead>{{ t("finance.transactions.date") }}</TableHead>
                    <TableHead class="text-right">{{
                      t("finance.transactions.amount")
                    }}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow
                    v-for="transaction in recentTransactions"
                    :key="transaction.id"
                    class="cursor-pointer transition-colors hover:bg-blue-50"
                    @click="handleTransactionClick(transaction)"
                  >
                    <TableCell class="font-mono text-xs text-muted-foreground">
                      {{ transaction.id.toString().padStart(3, "0") }}
                    </TableCell>
                    <TableCell class="font-medium text-slate-900">
                      {{ transaction.description }}
                    </TableCell>
                    <TableCell class="text-muted-foreground">{{
                      transaction.vendor
                    }}</TableCell>
                    <TableCell class="text-xs text-muted-foreground">
                      {{ formatDateShort(transaction.date) }}
                    </TableCell>
                    <TableCell class="text-right font-bold text-slate-900">
                      {{ currencySymbol
                      }}{{ transaction.amount.toLocaleString() }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <CostDetailModal
      :is-open="showCostModal"
      :cost-data="selectedCostData"
      @close="showCostModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";
import { formatCurrency as formatCurrencyUtil } from "../utils/currency";
import CostDetailModal from "../components/CostDetailModal.vue";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const { t, currentCurrency } = useI18n();
const loading = ref(true);
const error = ref(null);
const allMonthlySpending = ref([]);
const allCategorySpending = ref([]);
const allTransactions = ref([]);
const summaryData = ref({});
const allOrders = ref([]);

// Modal state
const showCostModal = ref(false);
const selectedCostData = ref(null);

// Use shared filters
const { selectedPeriod, getCurrentFilters } = useFilters();

// Monthly spending chart always shows all months (not filtered)
const monthlySpending = computed(() => {
  return allMonthlySpending.value;
});

// Filtered monthly spending for summary calculations only
const filteredMonthlySpending = computed(() => {
  if (selectedPeriod.value === "all") {
    return allMonthlySpending.value;
  }

  // Extract month name from YYYY-MM format
  const monthMap = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
  };
  const selectedMonth = monthMap[selectedPeriod.value.split("-")[1]];
  return allMonthlySpending.value.filter((m) => m.month === selectedMonth);
});

const categorySpending = computed(() => {
  return allCategorySpending.value;
});

const recentTransactions = computed(() => {
  if (selectedPeriod.value === "all") {
    return allTransactions.value;
  }
  // Filter transactions by selected month
  return allTransactions.value.filter((t) => {
    const transactionMonth = new Date(t.date).toISOString().slice(0, 7);
    return transactionMonth === selectedPeriod.value;
  });
});

const summary = computed(() => {
  // Recalculate summary based on filteredMonthlySpending (not the chart data)
  if (filteredMonthlySpending.value.length === 0) {
    return summaryData.value;
  }

  const totals = filteredMonthlySpending.value.reduce(
    (acc, month) => ({
      procurement: acc.procurement + month.procurement,
      operational: acc.operational + month.operational,
      labor: acc.labor + month.labor,
      overhead: acc.overhead + month.overhead,
    }),
    { procurement: 0, operational: 0, labor: 0, overhead: 0 },
  );

  return {
    total_procurement_cost: totals.procurement,
    total_operational_cost: totals.operational,
    total_labor_cost: totals.labor,
    total_overhead: totals.overhead,
    procurement_change: summaryData.value.procurement_change || 0,
    operational_change: summaryData.value.operational_change || 0,
    labor_change: summaryData.value.labor_change || 0,
    overhead_change: summaryData.value.overhead_change || 0,
  };
});

// Filtered orders based on selected period
const filteredOrders = computed(() => {
  if (selectedPeriod.value === "all") {
    return allOrders.value;
  }

  // Filter orders by selected month
  return allOrders.value.filter((order) => {
    const orderMonth = new Date(order.order_date).toISOString().slice(0, 7);
    return orderMonth === selectedPeriod.value;
  });
});

// Revenue metrics from filtered orders
const revenueMetrics = computed(() => {
  const totalRevenue = filteredOrders.value.reduce(
    (sum, order) => sum + (order.total_value || 0),
    0,
  );
  const orderCount = filteredOrders.value.length;
  const avgOrderValue = orderCount > 0 ? totalRevenue / orderCount : 0;

  return {
    totalRevenue,
    orderCount,
    avgOrderValue,
    revenueGrowth: 15.3, // Placeholder - could calculate from historical data
  };
});

// Total costs from summary
const totalCosts = computed(() => {
  return (
    summary.value.total_procurement_cost +
    summary.value.total_operational_cost +
    summary.value.total_labor_cost +
    summary.value.total_overhead
  );
});

// Net profit
const netProfit = computed(() => {
  return revenueMetrics.value.totalRevenue - totalCosts.value;
});

// Profit margin percentage
const profitMargin = computed(() => {
  if (revenueMetrics.value.totalRevenue === 0) return 0;
  return ((netProfit.value / revenueMetrics.value.totalRevenue) * 100).toFixed(
    1,
  );
});

// Monthly revenue data for chart
const monthlyRevenue = computed(() => {
  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  // Initialize all months
  const revenueByMonth = monthNames.map((month) => ({
    month,
    revenue: 0,
    costs: 0,
  }));

  // Calculate revenue from orders
  allOrders.value.forEach((order) => {
    const orderDate = new Date(order.order_date);
    const monthIndex = orderDate.getMonth();
    if (monthIndex >= 0 && monthIndex < 12) {
      revenueByMonth[monthIndex].revenue += order.total_value || 0;
    }
  });

  // Add costs from spending data
  allMonthlySpending.value.forEach((spending) => {
    const monthIndex = monthNames.indexOf(spending.month);
    if (monthIndex >= 0) {
      revenueByMonth[monthIndex].costs =
        spending.procurement +
        spending.operational +
        spending.labor +
        spending.overhead;
    }
  });

  return revenueByMonth;
});

// Max value for chart scaling
const maxRevenueValue = computed(() => {
  const maxRevenue = Math.max(...monthlyRevenue.value.map((m) => m.revenue));
  const maxCost = Math.max(...monthlyRevenue.value.map((m) => m.costs));
  const max = Math.max(maxRevenue, maxCost);
  return Math.ceil(max / 1000); // Return in K
});

const loadData = async () => {
  try {
    loading.value = true;
    const [summaryRes, monthlyRes, categoryRes, transactionsRes, ordersRes] =
      await Promise.all([
        api.getSpendingSummary(),
        api.getMonthlySpending(),
        api.getCategorySpending(),
        api.getTransactions(),
        api.getOrders(),
      ]);

    summaryData.value = summaryRes;
    allMonthlySpending.value = monthlyRes;
    allCategorySpending.value = categoryRes;
    allTransactions.value = transactionsRes;
    allOrders.value = ordersRes;
  } catch (err) {
    error.value = "Failed to load financial data: " + err.message;
  } finally {
    loading.value = false;
  }
};

// Watch for period filter changes
watch([selectedPeriod], () => {
  // Data will automatically update via computed properties
});

const formatCurrency = (value) => {
  return formatCurrencyUtil(value, currentCurrency.value);
};

const currencySymbol = computed(() => {
  return currentCurrency.value === "JPY" ? "\u00A5" : "$";
});

const getBarHeight = (value) => {
  const maxValue = 25000;
  return (value / maxValue) * 100;
};

const getRevenueBarHeight = (value) => {
  const maxValue = maxRevenueValue.value * 1000;
  return (value / maxValue) * 100;
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
};

const formatDateShort = (dateString) => {
  const date = new Date(dateString);
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const year = date.getFullYear().toString().slice(-2);
  return `${month}/${day}/${year}`;
};

const translateMonth = (month) => {
  const monthMap = {
    Jan: t("months.jan"),
    Feb: t("months.feb"),
    Mar: t("months.mar"),
    Apr: t("months.apr"),
    May: t("months.may"),
    Jun: t("months.jun"),
    Jul: t("months.jul"),
    Aug: t("months.aug"),
    Sep: t("months.sep"),
    Oct: t("months.oct"),
    Nov: t("months.nov"),
    Dec: t("months.dec"),
  };
  return monthMap[month] || month;
};

const translateCategory = (category) => {
  // First try spending categories
  const spendingCategoryMap = {
    "Raw Materials": t("spendingCategories.rawMaterials"),
    Components: t("spendingCategories.components"),
    Equipment: t("spendingCategories.equipment"),
    Consumables: t("spendingCategories.consumables"),
  };

  // Then try product categories
  const productCategoryMap = {
    "Circuit Boards": t("categories.circuitBoards"),
    Sensors: t("categories.sensors"),
    Actuators: t("categories.actuators"),
    Controllers: t("categories.controllers"),
    "Power Supplies": t("categories.powerSupplies"),
  };

  return (
    spendingCategoryMap[category] || productCategoryMap[category] || category
  );
};

const handleTransactionClick = (transaction) => {
  console.log("Transaction clicked:", transaction);
  alert(
    `Transaction Details:\n\nID: ${transaction.id}\nDescription: ${transaction.description}\nVendor: ${transaction.vendor}\nDate: ${formatDateShort(transaction.date)}\nAmount: $${transaction.amount.toLocaleString()}`,
  );
};

const showCostDetail = (monthData) => {
  selectedCostData.value = monthData;
  showCostModal.value = true;
};

onMounted(loadData);
</script>
