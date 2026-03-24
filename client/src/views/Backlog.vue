<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold tracking-tight">Backlog Management</h2>
      <p class="text-muted-foreground">Track and resolve inventory shortages</p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12 text-muted-foreground">
      Loading backlog...
    </div>
    <div v-else-if="error" class="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive">
      {{ error }}
    </div>
    <template v-else>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">High Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold text-destructive">
              {{ getBacklogByPriority("high").length }}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Medium Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold text-amber-500">
              {{ getBacklogByPriority("medium").length }}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Low Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold text-blue-500">
              {{ getBacklogByPriority("low").length }}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">Total Backlog Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {{ backlogItems.length }}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Backlog Items</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            v-if="backlogItems.length === 0"
            class="flex items-center justify-center py-12"
          >
            <p class="text-lg font-semibold text-emerald-500">
              No backlog items - all orders can be fulfilled!
            </p>
          </div>
          <Table v-else>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Item Name</TableHead>
                <TableHead>Quantity Needed</TableHead>
                <TableHead>Quantity Available</TableHead>
                <TableHead>Shortage</TableHead>
                <TableHead>Days Delayed</TableHead>
                <TableHead>Priority</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="item in backlogItems" :key="item.id">
                <TableCell class="font-semibold">{{ item.order_id }}</TableCell>
                <TableCell class="font-semibold">{{ item.item_sku }}</TableCell>
                <TableCell>{{ item.item_name }}</TableCell>
                <TableCell>{{ item.quantity_needed }}</TableCell>
                <TableCell>{{ item.quantity_available }}</TableCell>
                <TableCell>
                  <Badge variant="destructive">
                    {{ item.quantity_needed - item.quantity_available }} units short
                  </Badge>
                </TableCell>
                <TableCell>
                  <span :class="item.days_delayed > 7 ? 'text-destructive' : 'text-amber-500'">
                    {{ item.days_delayed }} days
                  </span>
                </TableCell>
                <TableCell>
                  <Badge
                    v-if="item.priority === 'high'"
                    variant="destructive"
                  >
                    {{ item.priority }}
                  </Badge>
                  <Badge
                    v-else-if="item.priority === 'medium'"
                    variant="secondary"
                    class="text-amber-500"
                  >
                    {{ item.priority }}
                  </Badge>
                  <Badge
                    v-else
                    class="bg-blue-500/10 text-blue-500"
                  >
                    {{ item.priority }}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const loading = ref(true);
const error = ref(null);
const allBacklogItems = ref([]);
const inventoryItems = ref([]);

// Use shared filters
const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters();

// Filter backlog based on inventory filters
const backlogItems = computed(() => {
  if (
    selectedLocation.value === "all" &&
    selectedCategory.value === "all"
  ) {
    return allBacklogItems.value;
  }

  // Get SKUs of items that match the filters
  const validSkus = new Set(inventoryItems.value.map((item) => item.sku));
  return allBacklogItems.value.filter((b) => validSkus.has(b.item_sku));
});

const loadBacklog = async () => {
  try {
    loading.value = true;
    const filters = getCurrentFilters();

    const [backlogData, inventoryData] = await Promise.all([
      api.getBacklog(),
      api.getInventory({
        warehouse: filters.warehouse,
        category: filters.category,
      }),
    ]);

    allBacklogItems.value = backlogData;
    inventoryItems.value = inventoryData;
  } catch (err) {
    error.value = "Failed to load backlog: " + err.message;
  } finally {
    loading.value = false;
  }
};

const getBacklogByPriority = (priority) => {
  return backlogItems.value.filter((item) => item.priority === priority);
};

// Watch for filter changes and reload data
watch([selectedLocation, selectedCategory], () => {
  loadBacklog();
});

onMounted(loadBacklog);
</script>
