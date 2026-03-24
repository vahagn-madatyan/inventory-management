import { ref, computed, onMounted } from "vue";
import { api } from "../api";
import { useAuth } from "./useAuth";

// Module-level state (singleton pattern like useFilters.js)
const showProfileDetails = ref(false);
const showTasks = ref(false);
const apiTasks = ref([]);
let initialized = false;

export function useModals() {
  const { currentUser } = useAuth();

  const tasks = computed(() => {
    return [...currentUser.value.tasks, ...apiTasks.value];
  });

  const loadTasks = async () => {
    try {
      apiTasks.value = await api.getTasks();
    } catch (err) {
      console.error("Failed to load tasks:", err);
    }
  };

  const addTask = async (taskData) => {
    try {
      const newTask = await api.createTask(taskData);
      apiTasks.value.unshift(newTask);
    } catch (err) {
      console.error("Failed to add task:", err);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      const isMockTask = currentUser.value.tasks.some((t) => t.id === taskId);

      if (isMockTask) {
        const index = currentUser.value.tasks.findIndex(
          (t) => t.id === taskId,
        );
        if (index !== -1) {
          currentUser.value.tasks.splice(index, 1);
        }
      } else {
        await api.deleteTask(taskId);
        apiTasks.value = apiTasks.value.filter((t) => t.id !== taskId);
      }
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  const toggleTask = async (taskId) => {
    try {
      const mockTask = currentUser.value.tasks.find((t) => t.id === taskId);

      if (mockTask) {
        mockTask.status =
          mockTask.status === "pending" ? "completed" : "pending";
      } else {
        const updatedTask = await api.toggleTask(taskId);
        const index = apiTasks.value.findIndex((t) => t.id === taskId);
        if (index !== -1) {
          apiTasks.value[index] = updatedTask;
        }
      }
    } catch (err) {
      console.error("Failed to toggle task:", err);
    }
  };

  // Auto-load tasks on first use
  if (!initialized) {
    initialized = true;
    loadTasks();
  }

  return {
    showProfileDetails,
    showTasks,
    tasks,
    addTask,
    deleteTask,
    toggleTask,
    loadTasks,
  };
}
