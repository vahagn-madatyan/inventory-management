<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold tracking-tight">{{ t("demand.title") }}</h2>
      <p class="text-muted-foreground">{{ t("demand.description") }}</p>
    </div>

    <div
      v-if="loading"
      class="flex items-center justify-center py-12 text-muted-foreground"
    >
      {{ t("common.loading") }}
    </div>
    <div
      v-else-if="error"
      class="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive"
    >
      {{ error }}
    </div>
    <template v-else>
      <div class="grid gap-6 md:grid-cols-3">
        <!-- Increasing Demand Card -->
        <Card class="border-l-4 border-l-emerald-500">
          <CardHeader class="pb-3">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10"
              >
                <TrendingUp class="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <CardTitle
                  class="text-sm font-semibold uppercase tracking-wide text-muted-foreground"
                >
                  {{ t("demand.increasingDemand") }}
                </CardTitle>
                <p class="text-xl font-bold">
                  {{
                    t("demand.itemsCount", {
                      count: getForecastsByTrend("increasing").length,
                    })
                  }}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent class="space-y-2">
            <div
              v-for="item in getForecastsByTrend('increasing').slice(0, 5)"
              :key="item.id"
              class="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 hover:bg-muted"
            >
              <span class="mr-4 truncate text-sm font-medium">{{
                item.item_name
              }}</span>
              <Badge class="shrink-0 bg-emerald-500/10 text-emerald-600">
                +{{ getChangePercent(item) }}%
              </Badge>
            </div>
            <p
              v-if="getForecastsByTrend('increasing').length > 5"
              class="pt-1 text-center text-xs italic text-muted-foreground"
            >
              +{{ getForecastsByTrend("increasing").length - 5 }}
              {{ t("demand.more") }}
            </p>
          </CardContent>
        </Card>

        <!-- Stable Demand Card -->
        <Card class="border-l-4 border-l-blue-500">
          <CardHeader class="pb-3">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-500/10"
              >
                <Minus class="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <CardTitle
                  class="text-sm font-semibold uppercase tracking-wide text-muted-foreground"
                >
                  {{ t("demand.stableDemand") }}
                </CardTitle>
                <p class="text-xl font-bold">
                  {{
                    t("demand.itemsCount", {
                      count: getForecastsByTrend("stable").length,
                    })
                  }}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent class="space-y-2">
            <div
              v-for="item in getForecastsByTrend('stable').slice(0, 5)"
              :key="item.id"
              class="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 hover:bg-muted"
            >
              <span class="mr-4 truncate text-sm font-medium">{{
                item.item_name
              }}</span>
              <Badge class="shrink-0 bg-blue-500/10 text-blue-500">
                {{ getChangePercent(item) }}%
              </Badge>
            </div>
            <p
              v-if="getForecastsByTrend('stable').length > 5"
              class="pt-1 text-center text-xs italic text-muted-foreground"
            >
              +{{ getForecastsByTrend("stable").length - 5 }}
              {{ t("demand.more") }}
            </p>
          </CardContent>
        </Card>

        <!-- Decreasing Demand Card -->
        <Card class="border-l-4 border-l-red-500">
          <CardHeader class="pb-3">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-red-500/10"
              >
                <TrendingDown class="h-5 w-5 text-red-500" />
              </div>
              <div>
                <CardTitle
                  class="text-sm font-semibold uppercase tracking-wide text-muted-foreground"
                >
                  {{ t("demand.decreasingDemand") }}
                </CardTitle>
                <p class="text-xl font-bold">
                  {{
                    t("demand.itemsCount", {
                      count: getForecastsByTrend("decreasing").length,
                    })
                  }}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent class="space-y-2">
            <div
              v-for="item in getForecastsByTrend('decreasing').slice(0, 5)"
              :key="item.id"
              class="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 hover:bg-muted"
            >
              <span class="mr-4 truncate text-sm font-medium">{{
                item.item_name
              }}</span>
              <Badge class="shrink-0 bg-red-500/10 text-red-500">
                {{ getChangePercent(item) }}%
              </Badge>
            </div>
            <p
              v-if="getForecastsByTrend('decreasing').length > 5"
              class="pt-1 text-center text-xs italic text-muted-foreground"
            >
              +{{ getForecastsByTrend("decreasing").length - 5 }}
              {{ t("demand.more") }}
            </p>
          </CardContent>
        </Card>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-vue-next";

const { t } = useI18n();
const loading = ref(true);
const error = ref(null);
const allForecasts = ref([]);
const inventoryItems = ref([]);

// Use shared filters
const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters();

// Filter forecasts based on inventory filters
const forecasts = computed(() => {
  if (selectedLocation.value === "all" && selectedCategory.value === "all") {
    return allForecasts.value;
  }

  // Get SKUs of items that match the filters
  const validSkus = new Set(inventoryItems.value.map((item) => item.sku));
  return allForecasts.value.filter((f) => validSkus.has(f.item_sku));
});

const loadForecasts = async () => {
  try {
    loading.value = true;
    const filters = getCurrentFilters();

    const [forecastsData, inventoryData] = await Promise.all([
      api.getDemandForecasts(),
      api.getInventory({
        warehouse: filters.warehouse,
        category: filters.category,
      }),
    ]);

    allForecasts.value = forecastsData;
    inventoryItems.value = inventoryData;
  } catch (err) {
    error.value = "Failed to load demand forecasts: " + err.message;
  } finally {
    loading.value = false;
  }
};

// Watch for filter changes and reload data
watch([selectedLocation, selectedCategory], () => {
  loadForecasts();
});

const getForecastsByTrend = (trend) => {
  return forecasts.value.filter((f) => f.trend === trend);
};

const getChangePercent = (forecast) => {
  const change = (
    ((forecast.forecasted_demand - forecast.current_demand) /
      forecast.current_demand) *
    100
  ).toFixed(1);
  return change > 0 ? `+${change}` : change;
};

const getChangeColor = (forecast) => {
  const change = forecast.forecasted_demand - forecast.current_demand;
  const changePercent = Math.abs((change / forecast.current_demand) * 100);

  // If change is within +/-2%, consider it stable and show blue
  if (changePercent <= 2) {
    return "#3b82f6"; // Blue for stable
  }

  if (change > 0) return "#10b981"; // Green for increasing
  if (change < 0) return "#ef4444"; // Red for decreasing
  return "#3b82f6"; // Blue for no change
};

const translatePeriod = (period) => {
  // Period values like "Next 3 months", "Q1 2025", "30 days", etc.
  const { currentLocale } = useI18n();
  if (currentLocale.value === "ja") {
    return period
      .replace(/Next\s+/i, "次の")
      .replace(/\s+months/i, "か月")
      .replace(/\s+month/i, "か月")
      .replace(/\s+days/i, "日間")
      .replace(/\s+day/i, "日")
      .replace("Q1", "第1四半期")
      .replace("Q2", "第2四半期")
      .replace("Q3", "第3四半期")
      .replace("Q4", "第4四半期");
  }
  return period;
};

onMounted(loadForecasts);
</script>
