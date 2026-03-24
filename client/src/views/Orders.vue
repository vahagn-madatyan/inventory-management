<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h2 class="text-3xl font-bold tracking-tight">{{ t("orders.title") }}</h2>
      <p class="text-muted-foreground">{{ t("orders.description") }}</p>
    </div>

    <div v-if="loading" class="text-muted-foreground">{{ t("common.loading") }}</div>
    <div v-else-if="error" class="text-destructive">{{ error }}</div>
    <div v-else class="space-y-6">
      <!-- Stat Cards -->
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">{{ t("status.delivered") }}</CardTitle>
            <CheckCircle class="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ getOrdersByStatus("Delivered").length }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">{{ t("status.shipped") }}</CardTitle>
            <Truck class="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ getOrdersByStatus("Shipped").length }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">{{ t("status.processing") }}</CardTitle>
            <Clock class="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ getOrdersByStatus("Processing").length }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-sm font-medium">{{ t("status.backordered") }}</CardTitle>
            <AlertCircle class="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">{{ getOrdersByStatus("Backordered").length }}</div>
          </CardContent>
        </Card>
      </div>

      <!-- Orders Table -->
      <Card>
        <CardHeader>
          <CardTitle>{{ t("orders.allOrders") }} ({{ orders.length }})</CardTitle>
          <CardDescription>{{ t("orders.description") }}</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[130px]">{{ t("orders.table.orderNumber") }}</TableHead>
                <TableHead class="w-[180px]">{{ t("orders.table.customer") }}</TableHead>
                <TableHead class="w-[200px]">{{ t("orders.table.items") }}</TableHead>
                <TableHead class="w-[130px]">{{ t("orders.table.status") }}</TableHead>
                <TableHead class="w-[140px]">{{ t("orders.table.orderDate") }}</TableHead>
                <TableHead class="w-[140px]">{{ t("orders.table.expectedDelivery") }}</TableHead>
                <TableHead class="w-[120px] text-right">{{ t("orders.table.totalValue") }}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="order in orders" :key="order.id">
                <TableCell class="font-medium">{{ order.order_number }}</TableCell>
                <TableCell>{{ translateCustomerName(order.customer) }}</TableCell>
                <TableCell>
                  <details class="relative">
                    <summary class="cursor-pointer select-none list-none inline-flex items-center gap-1 text-blue-500 font-medium hover:text-blue-600 hover:underline">
                      <span class="text-xs transition-transform duration-200 details-marker">&#9654;</span>
                      {{ t("orders.itemsCount", { count: order.items.length }) }}
                    </summary>
                    <div class="absolute top-full left-0 mt-2 z-10 min-w-[300px] max-w-[400px] rounded-lg border bg-popover p-3 shadow-md">
                      <div
                        v-for="(item, idx) in order.items"
                        :key="idx"
                        class="flex flex-col gap-1 p-2 border-b border-border last:border-b-0"
                      >
                        <span class="text-sm font-medium text-foreground">{{ translateProductName(item.name) }}</span>
                        <span class="text-[0.813rem] text-muted-foreground">{{ t("orders.quantity") }}: {{ item.quantity }} @ {{ currencySymbol }}{{ item.unit_price }}</span>
                      </div>
                    </div>
                  </details>
                </TableCell>
                <TableCell>
                  <Badge
                    v-if="order.status === 'Delivered'"
                    variant="outline"
                    class="bg-emerald-500/10 text-emerald-500"
                  >
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </Badge>
                  <Badge
                    v-else-if="order.status === 'Shipped'"
                    variant="outline"
                    class="bg-blue-500/10 text-blue-500"
                  >
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </Badge>
                  <Badge
                    v-else-if="order.status === 'Processing'"
                    variant="secondary"
                    class="text-amber-500"
                  >
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </Badge>
                  <Badge
                    v-else-if="order.status === 'Backordered'"
                    variant="destructive"
                  >
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </Badge>
                  <Badge v-else variant="secondary">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </Badge>
                </TableCell>
                <TableCell>{{ formatDate(order.order_date) }}</TableCell>
                <TableCell>{{ formatDate(order.expected_delivery) }}</TableCell>
                <TableCell class="text-right font-medium">
                  {{ currencySymbol }}{{ order.total_value.toLocaleString() }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <!-- Submitted Restocking Orders -->
      <Card v-if="restockingOrders.length > 0">
        <CardHeader>
          <CardTitle>Submitted Restocking Orders ({{ restockingOrders.length }})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Items</TableHead>
                <TableHead>Total Cost</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Expected Delivery</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="order in restockingOrders" :key="order.id">
                <TableCell class="font-medium">{{ order.id }}</TableCell>
                <TableCell>{{ formatDate(order.order_date) }}</TableCell>
                <TableCell>
                  <details class="relative">
                    <summary class="cursor-pointer select-none list-none inline-flex items-center gap-1 text-blue-500 font-medium hover:text-blue-600 hover:underline">
                      <span class="text-xs transition-transform duration-200 details-marker">&#9654;</span>
                      {{ order.items.length }} items
                    </summary>
                    <div class="absolute top-full left-0 mt-2 z-10 min-w-[300px] max-w-[400px] rounded-lg border bg-popover p-3 shadow-md">
                      <div
                        v-for="(item, idx) in order.items"
                        :key="idx"
                        class="flex flex-col gap-1 p-2 border-b border-border last:border-b-0"
                      >
                        <span class="text-sm font-medium text-foreground">{{ item.name }}</span>
                        <span class="text-[0.813rem] text-muted-foreground">Qty: {{ item.quantity }} @ {{ currencySymbol }}{{ item.unit_cost }}</span>
                      </div>
                    </div>
                  </details>
                </TableCell>
                <TableCell class="font-medium">
                  {{ currencySymbol }}{{ order.total_cost.toLocaleString() }}
                </TableCell>
                <TableCell>
                  <Badge variant="outline" class="bg-emerald-500/10 text-emerald-500">
                    {{ order.status }}
                  </Badge>
                </TableCell>
                <TableCell>{{ formatDate(order.expected_delivery) }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Truck, Clock, AlertCircle } from "lucide-vue-next";

const { t, currentCurrency, translateProductName, translateCustomerName } = useI18n();

const currencySymbol = computed(() => {
  return currentCurrency.value === "JPY" ? "\u00A5" : "$";
});

const loading = ref(true);
const error = ref(null);
const orders = ref([]);
const restockingOrders = ref([]);

// Use shared filters
const {
  selectedPeriod,
  selectedLocation,
  selectedCategory,
  selectedStatus,
  getCurrentFilters,
} = useFilters();

const loadOrders = async () => {
  try {
    loading.value = true;
    const filters = getCurrentFilters();
    const fetchedOrders = await api.getOrders(filters);

    // Sort orders by order_date (earliest first)
    orders.value = fetchedOrders.sort((a, b) => {
      const dateA = new Date(a.order_date);
      const dateB = new Date(b.order_date);
      return dateA - dateB;
    });

    try {
      restockingOrders.value = await api.getRestockingOrders();
    } catch (e) {
      // Silently ignore - restocking orders are optional
    }
  } catch (err) {
    error.value = "Failed to load orders: " + err.message;
  } finally {
    loading.value = false;
  }
};

// Watch for filter changes and reload data
watch(
  [selectedPeriod, selectedLocation, selectedCategory, selectedStatus],
  () => {
    loadOrders();
  },
);

const getOrdersByStatus = (status) => {
  return orders.value.filter((order) => order.status === status);
};

const getOrderStatusClass = (status) => {
  const statusMap = {
    Delivered: "success",
    Shipped: "info",
    Processing: "warning",
    Backordered: "danger",
  };
  return statusMap[status] || "info";
};

const formatDate = (dateString) => {
  const { currentLocale } = useI18n();
  const locale = currentLocale.value === "ja" ? "ja-JP" : "en-US";
  return new Date(dateString).toLocaleDateString(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

onMounted(loadOrders);
</script>
