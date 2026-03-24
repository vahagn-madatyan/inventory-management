# Design Tokens Reference

Complete CSS variable definitions and Tailwind configuration for the SaaS redesign.

## Table of Contents

1. [CSS Variables — Light Theme](#css-variables--light-theme)
2. [CSS Variables — Dark Theme](#css-variables--dark-theme)
3. [Sidebar-Specific Variables](#sidebar-specific-variables)
4. [Tailwind Config Extension](#tailwind-config-extension)
5. [Typography Scale](#typography-scale)
6. [Spacing Guidelines](#spacing-guidelines)

---

## CSS Variables — Light Theme

Add these to your main CSS file (e.g., `src/assets/index.css`) inside `@layer base`:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;

    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;

    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;

    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;

    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;

    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;

    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 240 5.9% 10%;

    --radius: 0.5rem;

    /* Sidebar — dark sidebar on light theme (branded feel) */
    --sidebar-background: 240 5.9% 10%;
    --sidebar-foreground: 240 4.8% 95.9%;
    --sidebar-primary: 224.3 76.3% 48%;
    --sidebar-primary-foreground: 0 0% 100%;
    --sidebar-accent: 240 3.7% 15.9%;
    --sidebar-accent-foreground: 240 4.8% 95.9%;
    --sidebar-border: 240 3.7% 15.9%;
    --sidebar-ring: 224.3 76.3% 48%;
  }
}
```

## CSS Variables — Dark Theme

```css
@layer base {
  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;

    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;

    --popover: 240 10% 3.9%;
    --popover-foreground: 0 0% 98%;

    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;

    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;

    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;

    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;

    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;

    /* Sidebar — slightly lighter than bg in dark mode */
    --sidebar-background: 240 5.9% 10%;
    --sidebar-foreground: 240 4.8% 95.9%;
    --sidebar-primary: 224.3 76.3% 48%;
    --sidebar-primary-foreground: 0 0% 100%;
    --sidebar-accent: 240 3.7% 15.9%;
    --sidebar-accent-foreground: 240 4.8% 95.9%;
    --sidebar-border: 240 3.7% 15.9%;
    --sidebar-ring: 224.3 76.3% 48%;
  }
}
```

## Sidebar-Specific Variables

The `--sidebar-*` variables scope the sidebar's colors independently from the main content area. This is how SaaS apps achieve the "dark sidebar, light content" pattern.

| Variable | Purpose | Typical value (light theme) |
|----------|---------|----------------------------|
| `--sidebar-background` | Sidebar background | Dark zinc (240 5.9% 10%) |
| `--sidebar-foreground` | Text/icons in sidebar | Light gray (240 4.8% 95.9%) |
| `--sidebar-primary` | Active item highlight | Brand blue (224.3 76.3% 48%) |
| `--sidebar-primary-foreground` | Text on active item | White |
| `--sidebar-accent` | Hover state background | Slightly lighter zinc |
| `--sidebar-accent-foreground` | Hover state text | Light gray |
| `--sidebar-border` | Dividers inside sidebar | Subtle dark line |
| `--sidebar-ring` | Focus ring inside sidebar | Brand blue |

## Tailwind Config Extension

In `tailwind.config.js` (or `tailwind.config.ts`):

```javascript
const { fontFamily } = require("tailwindcss/defaultTheme")

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## Typography Scale

Consistent heading and body text sizing:

| Element | Classes | When to use |
|---------|---------|-------------|
| Page title | `text-2xl font-semibold tracking-tight` | Top of each page, one per page |
| Page subtitle | `text-sm text-muted-foreground` | Below page title |
| Section heading | `text-xl font-semibold` | Card titles, major sections |
| Subsection | `text-lg font-medium` | Within cards, form section labels |
| Body text | `text-sm` | Default content, table cells |
| Small text | `text-xs text-muted-foreground` | Timestamps, helper text, badges |
| Sidebar nav item | `text-sm font-medium` | Navigation labels |
| Sidebar group label | `text-xs font-semibold uppercase tracking-wider text-sidebar-foreground/50` | Group headings in sidebar |

## Spacing Guidelines

Use Tailwind's spacing scale. Never use arbitrary values.

### Page-level spacing

```
┌─────────────────────────────────────────────┐
│ Sidebar │  Header (h-14, px-6)              │
│         │──────────────────────────────────  │
│  w-64   │  Main content (p-6)               │
│  (256px)│                                    │
│         │  ┌─Card (p-4 to p-6)────────────┐ │
│         │  │                               │ │
│         │  │  space-y-4 between items      │ │
│         │  │                               │ │
│         │  └───────────────────────────────┘ │
│         │                                    │
│         │  gap-6 between cards               │
│         │                                    │
│         │  ┌─Card────────────────────────┐  │
│         │  │                             │  │
│         │  └─────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Common spacing patterns

| Context | Spacing class | Pixels |
|---------|--------------|--------|
| Page padding | `p-6` | 24px |
| Between page sections | `space-y-6` | 24px |
| Card inner padding | `p-4` or `p-6` | 16px or 24px |
| Between form fields | `space-y-4` | 16px |
| Between related items | `space-y-2` or `gap-2` | 8px |
| Button group gap | `gap-2` | 8px |
| Icon + text gap | `gap-2` | 8px |
| Table cell padding | `px-4 py-3` | 16px / 12px |
| Sidebar item padding | `px-3 py-2` | 12px / 8px |
| Sidebar group gap | `space-y-1` | 4px |
