<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">{{ t('inventory.title') }}</h1>
        <p class="text-sm text-muted-foreground">{{ t('inventory.description') }}</p>
      </div>
    </div>

    <div v-if="loading" class="py-8 text-center text-muted-foreground">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="py-8 text-center text-destructive">{{ error }}</div>

    <Card v-else>
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle class="text-base font-semibold">
          {{ t('inventory.stockLevels') }} ({{ filteredItems.length }}
          {{ t('inventory.skus') }})
        </CardTitle>
        <div class="relative flex items-center min-w-[300px]">
          <Search class="absolute left-3 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            v-model="searchQuery"
            type="text"
            :placeholder="t('inventory.searchPlaceholder')"
            class="pl-9 pr-9"
          />
          <Button
            v-if="searchQuery"
            variant="ghost"
            size="icon"
            class="absolute right-0 h-full rounded-l-none text-muted-foreground hover:text-foreground"
            :title="t('inventory.clearSearch')"
            @click="searchQuery = ''"
          >
            <X class="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div class="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{{ t('inventory.table.sku') }}</TableHead>
                <TableHead>{{ t('inventory.table.itemName') }}</TableHead>
                <TableHead>{{ t('inventory.table.category') }}</TableHead>
                <TableHead>{{ t('inventory.table.quantityOnHand') }}</TableHead>
                <TableHead>{{ t('inventory.table.reorderPoint') }}</TableHead>
                <TableHead>{{ t('inventory.table.unitCost') }}</TableHead>
                <TableHead>{{ t('inventory.table.totalValue') }}</TableHead>
                <TableHead>{{ t('inventory.table.location') }}</TableHead>
                <TableHead>{{ t('inventory.table.status') }}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="item in filteredItems"
                :key="item.id"
                class="cursor-pointer transition-colors hover:bg-accent/50"
                @click="showItemDetail(item)"
              >
                <TableCell class="font-semibold">{{ item.sku }}</TableCell>
                <TableCell>{{ translateProductName(item.name) }}</TableCell>
                <TableCell>{{ translateCategory(item.category) }}</TableCell>
                <TableCell class="font-semibold">{{ item.quantity_on_hand }}</TableCell>
                <TableCell>{{ item.reorder_point }}</TableCell>
                <TableCell>{{ currencySymbol }}{{ item.unit_cost.toFixed(2) }}</TableCell>
                <TableCell class="font-semibold">
                  {{ currencySymbol }}{{ (item.quantity_on_hand * item.unit_cost).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </TableCell>
                <TableCell>{{ translateWarehouse(item.location) }}</TableCell>
                <TableCell>
                  <Badge
                    v-if="getStockStatusClass(item) === 'success'"
                    class="bg-emerald-500/10 text-emerald-500"
                  >
                    {{ getStockStatus(item) }}
                  </Badge>
                  <Badge
                    v-else-if="getStockStatusClass(item) === 'warning'"
                    variant="secondary"
                    class="text-amber-500"
                  >
                    {{ getStockStatus(item) }}
                  </Badge>
                  <Badge
                    v-else
                    variant="destructive"
                  >
                    {{ getStockStatus(item) }}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <InventoryDetailModal
      :is-open="showItemModal"
      :inventory-item="selectedItem"
      @close="showItemModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import InventoryDetailModal from '../components/InventoryDetailModal.vue'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search, X } from 'lucide-vue-next'

const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '\u00A5' : '$'
})

const loading = ref(true)
const error = ref(null)
const items = ref([])
const searchQuery = ref('')

// Modal state
const showItemModal = ref(false)
const selectedItem = ref(null)

// Use shared filters
const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

// Stock status order for sorting (using status keys)
const STATUS_ORDER = { lowStock: 0, adequate: 1, inStock: 2 }

// Get stock status key (for sorting and translation)
const getStockStatusKey = (item) => {
  if (item.quantity_on_hand <= item.reorder_point) {
    return 'lowStock'
  } else if (item.quantity_on_hand <= item.reorder_point * 1.5) {
    return 'adequate'
  } else {
    return 'inStock'
  }
}

// Computed property to filter items by search query and sort by stock status
const filteredItems = computed(() => {
  let filtered = items.value

  // Apply search filter if query exists
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter((item) =>
      item.name.toLowerCase().includes(query)
    )
  }

  // Sort by stock status: Low Stock first, then Adequate, then In Stock
  // Always create a copy to avoid mutating the original array
  return filtered.slice().sort((a, b) => {
    const statusA = getStockStatusKey(a)
    const statusB = getStockStatusKey(b)
    return STATUS_ORDER[statusA] - STATUS_ORDER[statusB]
  })
})

const loadInventory = async () => {
  try {
    loading.value = true
    const filters = getCurrentFilters()
    // Inventory doesn't support month/status filters, only warehouse and category
    items.value = await api.getInventory({
      warehouse: filters.warehouse,
      category: filters.category,
    })
  } catch (err) {
    error.value = 'Failed to load inventory: ' + err.message
  } finally {
    loading.value = false
  }
}

// Watch for filter changes and reload data
watch([selectedLocation, selectedCategory], () => {
  loadInventory()
})

const getStockStatus = (item) => {
  const key = getStockStatusKey(item)
  return t(`status.${key}`)
}

const getStockStatusClass = (item) => {
  if (item.quantity_on_hand <= item.reorder_point) {
    return 'danger'
  } else if (item.quantity_on_hand <= item.reorder_point * 1.5) {
    return 'warning'
  } else {
    return 'success'
  }
}

const translateCategory = (category) => {
  const categoryMap = {
    'Circuit Boards': t('categories.circuitBoards'),
    Sensors: t('categories.sensors'),
    Actuators: t('categories.actuators'),
    Controllers: t('categories.controllers'),
    'Power Supplies': t('categories.powerSupplies'),
    'Mechanical Parts': t('categories.mechanicalParts'),
  }
  return categoryMap[category] || category
}

const showItemDetail = (item) => {
  selectedItem.value = item
  showItemModal.value = true
}

onMounted(loadInventory)
</script>
