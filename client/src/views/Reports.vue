<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight">
        {{ t("reports.title") }}
      </h1>
      <p class="text-sm text-muted-foreground">
        {{ t("reports.description") }}
      </p>
    </div>

    <div v-if="loading" class="py-8 text-center text-muted-foreground">
      {{ t("common.loading") }}
    </div>
    <div v-else-if="error" class="py-8 text-center text-destructive">
      {{ error }}
    </div>

    <template v-else>
      <!-- Quarterly Performance -->
      <Card>
        <CardHeader>
          <CardTitle class="text-base font-semibold">{{
            t("reports.quarterly.title")
          }}</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{{ t("reports.quarterly.quarter") }}</TableHead>
                  <TableHead>{{
                    t("reports.quarterly.totalOrders")
                  }}</TableHead>
                  <TableHead>{{
                    t("reports.quarterly.totalRevenue")
                  }}</TableHead>
                  <TableHead>{{
                    t("reports.quarterly.avgOrderValue")
                  }}</TableHead>
                  <TableHead>{{
                    t("reports.quarterly.fulfillmentRate")
                  }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="q in quarterlyData" :key="q.quarter">
                  <TableCell class="font-semibold">{{ q.quarter }}</TableCell>
                  <TableCell>{{ q.total_orders }}</TableCell>
                  <TableCell>{{
                    formatCurrencyWithDecimals(q.total_revenue, currentCurrency)
                  }}</TableCell>
                  <TableCell>{{
                    formatCurrencyWithDecimals(
                      q.avg_order_value,
                      currentCurrency,
                    )
                  }}</TableCell>
                  <TableCell>
                    <Badge
                      v-if="q.fulfillment_rate >= 90"
                      class="bg-emerald-500/10 text-emerald-500"
                    >
                      {{ q.fulfillment_rate }}%
                    </Badge>
                    <Badge
                      v-else-if="q.fulfillment_rate >= 75"
                      class="bg-amber-500/10 text-amber-500"
                    >
                      {{ q.fulfillment_rate }}%
                    </Badge>
                    <Badge v-else class="bg-destructive/10 text-destructive">
                      {{ q.fulfillment_rate }}%
                    </Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <!-- Monthly Trends Chart -->
      <Card>
        <CardHeader>
          <CardTitle class="text-base font-semibold">{{
            t("reports.monthlyTrend.title")
          }}</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="px-4 py-8 min-h-[300px]">
            <div class="flex items-end justify-around h-[250px] gap-2">
              <div
                v-for="month in monthlyData"
                :key="month.month"
                class="flex flex-col items-center flex-1 max-w-[80px]"
              >
                <div class="h-[200px] flex items-end w-full">
                  <div
                    class="w-full rounded-t bg-gradient-to-t from-blue-500 to-blue-400 transition-all duration-300 cursor-pointer hover:from-blue-600 hover:to-blue-500"
                    :style="{ height: getBarHeight(month.revenue) + 'px' }"
                    :title="
                      formatCurrencyWithDecimals(month.revenue, currentCurrency)
                    "
                  ></div>
                </div>
                <div
                  class="text-xs text-muted-foreground text-center -rotate-45 whitespace-nowrap mt-6"
                >
                  {{ formatMonth(month.month) }}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Month-over-Month Comparison -->
      <Card>
        <CardHeader>
          <CardTitle class="text-base font-semibold">{{
            t("reports.monthOverMonth.title")
          }}</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{{ t("reports.monthOverMonth.month") }}</TableHead>
                  <TableHead>{{
                    t("reports.monthOverMonth.orders")
                  }}</TableHead>
                  <TableHead>{{
                    t("reports.monthOverMonth.revenue")
                  }}</TableHead>
                  <TableHead>{{
                    t("reports.monthOverMonth.change")
                  }}</TableHead>
                  <TableHead>{{
                    t("reports.monthOverMonth.growthRate")
                  }}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow
                  v-for="(month, index) in monthlyData"
                  :key="month.month"
                >
                  <TableCell class="font-semibold">{{
                    formatMonth(month.month)
                  }}</TableCell>
                  <TableCell>{{ month.order_count }}</TableCell>
                  <TableCell>{{
                    formatCurrencyWithDecimals(month.revenue, currentCurrency)
                  }}</TableCell>
                  <TableCell>
                    <span
                      v-if="index > 0"
                      :class="
                        getChangeClass(
                          month.revenue,
                          monthlyData[index - 1].revenue,
                        )
                      "
                    >
                      {{
                        getChangeValue(
                          month.revenue,
                          monthlyData[index - 1].revenue,
                        )
                      }}
                    </span>
                    <span v-else class="text-muted-foreground">-</span>
                  </TableCell>
                  <TableCell>
                    <span
                      v-if="index > 0"
                      :class="
                        getChangeClass(
                          month.revenue,
                          monthlyData[index - 1].revenue,
                        )
                      "
                    >
                      {{
                        getGrowthRate(
                          month.revenue,
                          monthlyData[index - 1].revenue,
                        )
                      }}
                    </span>
                    <span v-else class="text-muted-foreground">-</span>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <!-- Summary Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("reports.summary.totalRevenueYTD") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1">
              {{ formatCurrencyWithDecimals(totalRevenue, currentCurrency) }}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("reports.summary.avgMonthlyRevenue") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1">
              {{
                formatCurrencyWithDecimals(avgMonthlyRevenue, currentCurrency)
              }}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("reports.summary.totalOrdersYTD") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1">
              {{ totalOrders }}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <p class="text-sm text-muted-foreground">
              {{ t("reports.summary.bestQuarter") }}
            </p>
            <p class="text-2xl font-bold tracking-tight mt-1">
              {{ bestQuarter }}
            </p>
          </CardContent>
        </Card>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";
import { formatCurrencyWithDecimals } from "../utils/currency";
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

const { t, currentCurrency, currentLocale } = useI18n();
const {
  selectedPeriod,
  selectedLocation,
  selectedCategory,
  selectedStatus,
  getCurrentFilters,
} = useFilters();

const loading = ref(true);
const error = ref(null);
const quarterlyData = ref([]);
const monthlyData = ref([]);

// Computed: max revenue for bar chart scaling
const maxRevenue = computed(() => {
  return monthlyData.value.reduce((max, m) => Math.max(max, m.revenue), 0);
});

// Computed summary stats
const totalRevenue = computed(() => {
  return monthlyData.value.reduce((sum, m) => sum + m.revenue, 0);
});

const avgMonthlyRevenue = computed(() => {
  if (monthlyData.value.length === 0) return 0;
  return totalRevenue.value / monthlyData.value.length;
});

const totalOrders = computed(() => {
  return monthlyData.value.reduce((sum, m) => sum + m.order_count, 0);
});

const bestQuarter = computed(() => {
  if (quarterlyData.value.length === 0) return "";
  return quarterlyData.value.reduce((best, q) => {
    return q.total_revenue > best.total_revenue ? q : best;
  }, quarterlyData.value[0]).quarter;
});

const loadData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const filters = getCurrentFilters();
    const [quarterly, monthly] = await Promise.all([
      api.getQuarterlyReports(filters),
      api.getMonthlyTrends(filters),
    ]);
    quarterlyData.value = quarterly;
    monthlyData.value = monthly;
  } catch (err) {
    console.error("Failed to load reports:", err);
    error.value = "Failed to load reports: " + err.message;
  } finally {
    loading.value = false;
  }
};

// Locale-aware month formatting
const formatMonth = (monthStr) => {
  const [year, month] = monthStr.split("-");
  const date = new Date(parseInt(year), parseInt(month) - 1);
  if (isNaN(date.getTime())) return monthStr;
  const locale = currentLocale.value === "ja" ? "ja-JP" : "en-US";
  return date.toLocaleDateString(locale, { month: "short", year: "numeric" });
};

const formatNumber = (num) => {
  return num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

// Bar height uses the computed maxRevenue
const getBarHeight = (revenue) => {
  if (maxRevenue.value === 0) return 0;
  return (revenue / maxRevenue.value) * 200;
};

const getChangeValue = (current, previous) => {
  const change = current - previous;
  const symbol = currentLocale.value === "ja" ? "\u00A5" : "$";
  if (change > 0) {
    return "+" + symbol + formatNumber(Math.abs(change));
  } else if (change < 0) {
    return "-" + symbol + formatNumber(Math.abs(change));
  }
  return symbol + "0.00";
};

const getChangeClass = (current, previous) => {
  const change = current - previous;
  if (change > 0) return "text-emerald-600 font-semibold";
  if (change < 0) return "text-destructive font-semibold";
  return "";
};

const getGrowthRate = (current, previous) => {
  if (previous === 0) return "N/A";
  const rate = ((current - previous) / previous) * 100;
  const sign = rate > 0 ? "+" : "";
  return sign + rate.toFixed(1) + "%";
};

// Reload data whenever any filter changes
watch(
  [selectedPeriod, selectedLocation, selectedCategory, selectedStatus],
  () => {
    loadData();
  },
);

onMounted(() => {
  loadData();
});
</script>
