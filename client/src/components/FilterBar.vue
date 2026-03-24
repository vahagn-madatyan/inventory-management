<template>
  <div class="flex items-center gap-3 flex-wrap">
    <div class="flex items-center gap-1.5">
      <label class="text-xs font-medium text-muted-foreground whitespace-nowrap">{{ t("filters.timePeriod") }}</label>
      <select
        v-model="selectedPeriod"
        class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
      >
        <option value="all">{{ t("filters.allMonths") }}</option>
        <option value="2025-01">{{ t("months.january") }}</option>
        <option value="2025-02">{{ t("months.february") }}</option>
        <option value="2025-03">{{ t("months.march") }}</option>
        <option value="2025-04">{{ t("months.april") }}</option>
        <option value="2025-05">{{ t("months.may") }}</option>
        <option value="2025-06">{{ t("months.june") }}</option>
        <option value="2025-07">{{ t("months.july") }}</option>
        <option value="2025-08">{{ t("months.august") }}</option>
        <option value="2025-09">{{ t("months.september") }}</option>
        <option value="2025-10">{{ t("months.october") }}</option>
        <option value="2025-11">{{ t("months.november") }}</option>
        <option value="2025-12">{{ t("months.december") }}</option>
      </select>
    </div>

    <div class="flex items-center gap-1.5">
      <label class="text-xs font-medium text-muted-foreground whitespace-nowrap">{{ t("filters.location") }}</label>
      <select
        v-model="selectedLocation"
        class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
      >
        <option value="all">{{ t("filters.all") }}</option>
        <option value="San Francisco">{{ t("warehouses.sanFrancisco") }}</option>
        <option value="London">{{ t("warehouses.london") }}</option>
        <option value="Tokyo">{{ t("warehouses.tokyo") }}</option>
      </select>
    </div>

    <div class="flex items-center gap-1.5">
      <label class="text-xs font-medium text-muted-foreground whitespace-nowrap">{{ t("filters.category") }}</label>
      <select
        v-model="selectedCategory"
        class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
      >
        <option value="all">{{ t("filters.all") }}</option>
        <option value="circuit boards">{{ t("categories.circuitBoards") }}</option>
        <option value="sensors">{{ t("categories.sensors") }}</option>
        <option value="actuators">{{ t("categories.actuators") }}</option>
        <option value="controllers">{{ t("categories.controllers") }}</option>
        <option value="power supplies">{{ t("categories.powerSupplies") }}</option>
        <option value="mechanical parts">{{ t("categories.mechanicalParts") }}</option>
      </select>
    </div>

    <div class="flex items-center gap-1.5">
      <label class="text-xs font-medium text-muted-foreground whitespace-nowrap">{{ t("filters.orderStatus") }}</label>
      <select
        v-model="selectedStatus"
        class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
      >
        <option value="all">{{ t("filters.all") }}</option>
        <option value="delivered">{{ t("status.delivered") }}</option>
        <option value="shipped">{{ t("status.shipped") }}</option>
        <option value="processing">{{ t("status.processing") }}</option>
        <option value="backordered">{{ t("status.backordered") }}</option>
      </select>
    </div>

    <Button
      v-if="hasActiveFilters"
      variant="ghost"
      size="sm"
      title="Reset all filters"
      @click="resetFilters"
    >
      <RotateCcw class="h-4 w-4" />
    </Button>
  </div>
</template>

<script setup>
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-vue-next";

const {
  selectedPeriod,
  selectedLocation,
  selectedCategory,
  selectedStatus,
  hasActiveFilters,
  resetFilters,
} = useFilters();

const { t } = useI18n();
</script>
