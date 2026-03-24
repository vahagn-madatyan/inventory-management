<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t("restocking.title") }}</h2>
      <p>{{ t("restocking.description") }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t("common.loading") }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="submitted && submittedOrder" class="success-container">
      <div class="card success-card">
        <div class="success-icon">&#10003;</div>
        <h3 class="success-title">{{ t("restocking.orderSuccess") }}</h3>
        <div class="success-details">
          <div class="success-detail">
            <span class="detail-label">{{ t("restocking.orderNumber") }}</span>
            <span class="detail-value">{{ submittedOrder.order_number }}</span>
          </div>
          <div class="success-detail">
            <span class="detail-label">{{
              t("restocking.expectedDelivery")
            }}</span>
            <span class="detail-value">{{
              formatDate(submittedOrder.expected_delivery)
            }}</span>
          </div>
          <div class="success-detail">
            <span class="detail-label">{{ t("restocking.orderTotal") }}</span>
            <span class="detail-value">{{
              formatCurrency(submittedOrder.total_cost, currentCurrency)
            }}</span>
          </div>
        </div>
        <button class="btn btn-primary" @click="resetForm">
          {{ t("restocking.placeAnother") }}
        </button>
      </div>
    </div>
    <div v-else>
      <!-- Budget Control -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t("restocking.budgetControl") }}</h3>
          <span class="budget-display">{{
            formatCurrency(budget, currentCurrency)
          }}</span>
        </div>
        <p class="budget-description">{{ t("restocking.setBudget") }}</p>
        <div class="budget-controls">
          <input
            type="range"
            class="budget-slider"
            :value="budget"
            @input="budget = Number($event.target.value)"
            min="0"
            max="50000"
            step="500"
          />
          <input
            type="number"
            class="budget-input"
            :value="budget"
            @input="budget = Number($event.target.value)"
            min="0"
            max="50000"
            step="500"
          />
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t("restocking.recommendedItems") }}</div>
          <div class="stat-value">{{ recommendations.length }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t("restocking.selectedItems") }}</div>
          <div class="stat-value">{{ selectedList.length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t("restocking.estimatedCost") }}</div>
          <div class="stat-value">
            {{ formatCurrency(runningTotal, currentCurrency) }}
          </div>
        </div>
        <div :class="['stat-card', isOverBudget ? 'danger' : 'success']">
          <div class="stat-label">{{ t("restocking.budgetRemaining") }}</div>
          <div class="stat-value">
            {{ formatCurrency(budgetRemaining, currentCurrency) }}
          </div>
        </div>
      </div>

      <!-- Recommendations Table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t("restocking.recommendedItems") }} ({{
              recommendations.length
            }})
          </h3>
          <div class="table-actions">
            <button class="btn btn-sm btn-outline" @click="selectAll">
              {{ t("restocking.selectAll") }}
            </button>
            <button class="btn btn-sm btn-outline" @click="deselectAll">
              {{ t("restocking.deselectAll") }}
            </button>
          </div>
        </div>
        <div v-if="recommendations.length === 0" class="empty-state">
          {{ t("restocking.noRecommendations") }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t("restocking.table.select") }}</th>
                <th>{{ t("restocking.table.name") }}</th>
                <th>{{ t("restocking.table.sku") }}</th>
                <th>{{ t("restocking.table.source") }}</th>
                <th>{{ t("restocking.table.quantity") }}</th>
                <th>{{ t("restocking.table.unitCost") }}</th>
                <th>{{ t("restocking.table.lineTotal") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in recommendations" :key="rec.sku">
                <td>
                  <input
                    type="checkbox"
                    :checked="selectedItems[rec.sku]?.selected"
                    @change="toggleItem(rec.sku)"
                    class="item-checkbox"
                  />
                </td>
                <td>{{ translateProductName(rec.name) }}</td>
                <td>
                  <strong>{{ rec.sku }}</strong>
                </td>
                <td>
                  <span :class="['badge', getSourceClass(rec.source)]">
                    {{ t("restocking.sources." + rec.source) }}
                  </span>
                </td>
                <td>
                  <input
                    type="number"
                    class="quantity-input"
                    :value="selectedItems[rec.sku]?.quantity"
                    @input="updateQuantity(rec.sku, $event.target.value)"
                    min="1"
                    :disabled="!selectedItems[rec.sku]?.selected"
                  />
                </td>
                <td>{{ formatCurrency(rec.unit_cost, currentCurrency) }}</td>
                <td>
                  <strong>{{
                    formatCurrency(getLineTotal(rec), currentCurrency)
                  }}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Budget Progress Bar -->
      <div class="card progress-card">
        <div class="progress-header">
          <span class="progress-label">{{ t("restocking.budget") }}</span>
          <span :class="['progress-value', { 'over-budget': isOverBudget }]">
            {{ formatCurrency(runningTotal, currentCurrency) }} /
            {{ formatCurrency(budget, currentCurrency) }}
          </span>
        </div>
        <div class="progress-bar-track">
          <div
            class="progress-bar-fill"
            :style="{ width: Math.min(spendRatio, 100) + '%' }"
            :class="progressBarClass"
          ></div>
        </div>
        <div v-if="isOverBudget" class="over-budget-warning">
          {{ t("restocking.overBudget") }}:
          {{ formatCurrency(Math.abs(budgetRemaining), currentCurrency) }}
        </div>
      </div>

      <!-- Footer -->
      <div class="order-footer">
        <div class="footer-summary">
          <span class="footer-total">
            {{ formatCurrency(runningTotal, currentCurrency) }} /
            {{ formatCurrency(budget, currentCurrency) }}
          </span>
          <span v-if="isOverBudget" class="footer-warning">{{
            t("restocking.overBudget")
          }}</span>
        </div>
        <button
          class="btn btn-primary btn-lg"
          :disabled="!canSubmit"
          @click="submitOrder"
        >
          {{
            submitting ? t("restocking.submitting") : t("restocking.placeOrder")
          }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import { api } from "../api";
import { formatCurrency } from "../utils/currency";
import { useI18n } from "../composables/useI18n";

export default {
  name: "Restocking",
  setup() {
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
        selectedList.value.length > 0 &&
        !isOverBudget.value &&
        !submitting.value,
    );
    const spendRatio = computed(() =>
      budget.value > 0 ? (runningTotal.value / budget.value) * 100 : 0,
    );

    const progressBarClass = computed(() => {
      if (spendRatio.value > 100) return "bar-danger";
      if (spendRatio.value >= 80) return "bar-warning";
      return "bar-success";
    });

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
        { demand: "info", low_stock: "danger", both: "warning" }[source] ||
        "info"
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

    return {
      t,
      currentCurrency,
      translateProductName,
      formatCurrency,
      budget,
      recommendations,
      selectedItems,
      loading,
      error,
      submitting,
      submitted,
      submittedOrder,
      selectedList,
      runningTotal,
      budgetRemaining,
      isOverBudget,
      canSubmit,
      spendRatio,
      progressBarClass,
      getLineTotal,
      updateQuantity,
      toggleItem,
      selectAll,
      deselectAll,
      resetForm,
      getSourceClass,
      formatDate,
      submitOrder,
    };
  },
};
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
}

.page-header h2 {
  margin-bottom: 0.25rem;
}

.page-header p {
  color: #64748b;
  font-size: 0.875rem;
}

/* Budget Card */
.budget-card {
  margin-bottom: 1.5rem;
}

.budget-display {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3b82f6;
}

.budget-description {
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.budget-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.budget-slider {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 3px solid #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 3px solid #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.budget-input {
  width: 120px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  text-align: right;
  background: #f8fafc;
  transition: all 0.2s;
}

.budget-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Table Actions */
.table-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-size: 0.875rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn-lg {
  padding: 0.75rem 2rem;
  font-size: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 0.625rem 1.25rem;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  padding: 0.375rem 0.75rem;
}

.btn-outline:hover {
  background: #f8fafc;
  color: #0f172a;
  border-color: #cbd5e1;
}

/* Checkbox */
.item-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #3b82f6;
}

/* Quantity Input */
.quantity-input {
  width: 80px;
  padding: 0.375rem 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #0f172a;
  text-align: center;
  background: #f8fafc;
  transition: all 0.2s;
}

.quantity-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.quantity-input:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
  font-size: 0.938rem;
}

/* Progress Card */
.progress-card {
  margin-bottom: 1.25rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.progress-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
}

.progress-value.over-budget {
  color: #ef4444;
}

.progress-bar-track {
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 5px;
  transition:
    width 0.3s ease,
    background-color 0.3s ease;
}

.bar-success {
  background: #10b981;
}

.bar-warning {
  background: #f59e0b;
}

.bar-danger {
  background: #ef4444;
}

.over-budget-warning {
  margin-top: 0.5rem;
  font-size: 0.813rem;
  font-weight: 600;
  color: #ef4444;
}

/* Order Footer */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  margin-bottom: 1.25rem;
}

.footer-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.footer-total {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.footer-warning {
  font-size: 0.813rem;
  font-weight: 600;
  color: #ef4444;
}

/* Success Card */
.success-container {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

.success-card {
  max-width: 480px;
  text-align: center;
  padding: 2.5rem;
}

.success-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #d1fae5;
  color: #059669;
  font-size: 2rem;
  font-weight: 700;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
}

.success-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 1.5rem;
}

.success-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.success-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.detail-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 0.875rem;
  color: #0f172a;
  font-weight: 700;
}

/* Loading and Error */
.loading,
.error {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.error {
  color: #ef4444;
}
</style>
