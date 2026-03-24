import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import "./assets/index.css";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("./layouts/AppLayout.vue"),
      children: [
        {
          path: "",
          component: () => import("./views/Dashboard.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "nav.overview",
            icon: "LayoutDashboard",
          },
        },
        {
          path: "inventory",
          component: () => import("./views/Inventory.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "nav.inventory",
            icon: "Package",
          },
        },
        {
          path: "orders",
          component: () => import("./views/Orders.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "nav.orders",
            icon: "ShoppingCart",
          },
        },
        {
          path: "spending",
          component: () => import("./views/Spending.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "nav.finance",
            icon: "DollarSign",
          },
        },
        {
          path: "demand",
          component: () => import("./views/Demand.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "nav.demandForecast",
            icon: "TrendingUp",
          },
        },
        {
          path: "restocking",
          component: () => import("./views/Restocking.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "nav.restocking",
            icon: "RefreshCw",
          },
        },
        {
          path: "reports",
          component: () => import("./views/Reports.vue"),
          meta: {
            nav: true,
            navGroup: "main",
            title: "Reports",
            icon: "BarChart3",
          },
        },
        {
          path: "backlog",
          component: () => import("./views/Backlog.vue"),
          meta: {
            nav: true,
            navGroup: "secondary",
            title: "Backlog",
            icon: "AlertTriangle",
          },
        },
      ],
    },
  ],
});

const app = createApp(App);
app.use(router);
app.mount("#app");
