import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  DollarSign,
  TrendingUp,
  RefreshCw,
  BarChart3,
  AlertTriangle,
} from "lucide-vue-next";

export const mainNavItems = [
  {
    titleKey: "nav.overview",
    fallbackTitle: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    titleKey: "nav.inventory",
    fallbackTitle: "Inventory",
    path: "/inventory",
    icon: Package,
  },
  {
    titleKey: "nav.orders",
    fallbackTitle: "Orders",
    path: "/orders",
    icon: ShoppingCart,
  },
  {
    titleKey: "nav.finance",
    fallbackTitle: "Spending",
    path: "/spending",
    icon: DollarSign,
  },
  {
    titleKey: "nav.demandForecast",
    fallbackTitle: "Demand",
    path: "/demand",
    icon: TrendingUp,
  },
  {
    titleKey: "nav.restocking",
    fallbackTitle: "Restocking",
    path: "/restocking",
    icon: RefreshCw,
  },
  {
    titleKey: null,
    fallbackTitle: "Reports",
    path: "/reports",
    icon: BarChart3,
  },
];

export const secondaryNavItems = [
  {
    titleKey: null,
    fallbackTitle: "Backlog",
    path: "/backlog",
    icon: AlertTriangle,
  },
];
