# Component Restyling Patterns

Before/after patterns for transforming common Vue components into shadcn-vue equivalents.

## Table of Contents

1. [Buttons](#buttons)
2. [Cards](#cards)
3. [Tables](#tables)
4. [Forms](#forms)
5. [Dialogs](#dialogs)
6. [Badges and Status](#badges-and-status)
7. [Page Layout Pattern](#page-layout-pattern)
8. [Empty States](#empty-states)

---

## Buttons

### Before (plain HTML / other library)

```vue
<button class="btn btn-primary" @click="save">Save</button>
<button class="btn btn-danger" @click="remove">Delete</button>
<a href="/docs" class="btn btn-link">Docs</a>
```

### After (shadcn-vue)

```vue
<script setup>
import { Button } from "@/components/ui/button";
import { Save, Trash2, ExternalLink } from "lucide-vue-next";
</script>

<template>
  <div class="flex items-center gap-2">
    <Button @click="save">
      <Save class="mr-2 size-4" />
      Save
    </Button>
    <Button variant="destructive" @click="remove">
      <Trash2 class="mr-2 size-4" />
      Delete
    </Button>
    <Button variant="ghost" as-child>
      <router-link to="/docs">
        <ExternalLink class="mr-2 size-4" />
        Docs
      </router-link>
    </Button>
  </div>
</template>
```

### Button variants cheat sheet

| Variant       | Use case                                 |
| ------------- | ---------------------------------------- |
| `default`     | Primary actions (Save, Create, Submit)   |
| `secondary`   | Less prominent actions                   |
| `outline`     | Cancel, secondary choices                |
| `ghost`       | Toolbar buttons, inline actions          |
| `destructive` | Delete, Remove, Revoke                   |
| `link`        | Inline text links that look like buttons |

---

## Cards

### Before

```vue
<div class="panel">
  <div class="panel-header">
    <h3>Users</h3>
  </div>
  <div class="panel-body">
    <!-- content -->
  </div>
</div>
```

### After

```vue
<script setup>
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Users</CardTitle>
      <CardDescription
        >Manage your team members and their roles</CardDescription
      >
    </CardHeader>
    <CardContent>
      <!-- content -->
    </CardContent>
  </Card>
</template>
```

### Card with actions in header

```vue
<Card>
  <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
    <div class="space-y-1">
      <CardTitle>Users</CardTitle>
      <CardDescription>Manage team members</CardDescription>
    </div>
    <Button size="sm">
      <Plus class="mr-2 size-4" />
      Add User
    </Button>
  </CardHeader>
  <CardContent>
    <!-- content -->
  </CardContent>
</Card>
```

---

## Tables

### Before

```vue
<table class="table table-striped">
  <thead>
    <tr>
      <th>Name</th>
      <th>Email</th>
      <th>Role</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="user in users" :key="user.id">
      <td>{{ user.name }}</td>
      <td>{{ user.email }}</td>
      <td>{{ user.role }}</td>
    </tr>
  </tbody>
</table>
```

### After

```vue
<script setup>
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
</script>

<template>
  <div class="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead class="w-[250px]">Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Role</TableHead>
          <TableHead class="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="user in users" :key="user.id">
          <TableCell class="font-medium">
            <div class="flex items-center gap-3">
              <Avatar class="h-8 w-8">
                <AvatarImage :src="user.avatar" />
                <AvatarFallback>{{ user.initials }}</AvatarFallback>
              </Avatar>
              {{ user.name }}
            </div>
          </TableCell>
          <TableCell class="text-muted-foreground">{{ user.email }}</TableCell>
          <TableCell>
            <Badge variant="secondary">{{ user.role }}</Badge>
          </TableCell>
          <TableCell class="text-right">
            <Button variant="ghost" size="sm">Edit</Button>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>
```

---

## Forms

### Before

```vue
<form @submit.prevent="onSubmit">
  <div class="form-group">
    <label>Name</label>
    <input v-model="form.name" type="text" class="form-control" />
  </div>
  <div class="form-group">
    <label>Email</label>
    <input v-model="form.email" type="email" class="form-control" />
  </div>
  <button type="submit" class="btn btn-primary">Save</button>
</form>
```

### After

```vue
<script setup>
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <div class="space-y-2">
      <Label for="name">Name</Label>
      <Input
        id="name"
        v-model="form.name"
        type="text"
        placeholder="Enter your name"
      />
    </div>
    <div class="space-y-2">
      <Label for="email">Email</Label>
      <Input
        id="email"
        v-model="form.email"
        type="email"
        placeholder="name@example.com"
      />
      <p class="text-xs text-muted-foreground">We'll never share your email.</p>
    </div>
    <div class="flex justify-end gap-2">
      <Button type="button" variant="outline" @click="cancel">Cancel</Button>
      <Button type="submit">Save Changes</Button>
    </div>
  </form>
</template>
```

### Form layout patterns

| Pattern       | Use case               | Layout                                  |
| ------------- | ---------------------- | --------------------------------------- |
| Single column | Simple forms, settings | `space-y-4`                             |
| Two column    | Profile, address forms | `grid grid-cols-1 md:grid-cols-2 gap-4` |
| Inline        | Search, filters        | `flex items-center gap-2`               |

---

## Dialogs

### Before

```vue
<div v-if="showModal" class="modal">
  <div class="modal-content">
    <h3>Confirm Delete</h3>
    <p>Are you sure?</p>
    <button @click="confirm">Yes</button>
    <button @click="showModal = false">Cancel</button>
  </div>
</div>
```

### After

```vue
<script setup>
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
</script>

<template>
  <Dialog v-model:open="showModal">
    <DialogTrigger as-child>
      <Button variant="destructive">Delete</Button>
    </DialogTrigger>
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogDescription>
          This action cannot be undone. This will permanently delete the item.
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="showModal = false">Cancel</Button>
        <Button variant="destructive" @click="confirm">Delete</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
```

---

## Badges and Status

### Before

```vue
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-danger">Error</span>
```

### After

```vue
<script setup>
import { Badge } from "@/components/ui/badge";
</script>

<template>
  <!-- Use variants + custom colors via class -->
  <Badge class="bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20"
    >Active</Badge
  >
  <Badge variant="secondary" class="text-amber-500">Pending</Badge>
  <Badge variant="destructive">Error</Badge>
</template>
```

### Status indicator with dot

```vue
<div class="flex items-center gap-2">
  <span class="h-2 w-2 rounded-full bg-emerald-500" />
  <span class="text-sm">Active</span>
</div>
```

---

## Page Layout Pattern

Every page in the app should follow this consistent structure:

```vue
<script setup>
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-vue-next";
</script>

<template>
  <div class="space-y-6">
    <!-- Page header: title + primary action -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">Projects</h1>
        <p class="text-sm text-muted-foreground">
          Manage and track all your active projects
        </p>
      </div>
      <Button>
        <Plus class="mr-2 size-4" />
        New Project
      </Button>
    </div>

    <!-- Stats row (optional) -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card v-for="stat in stats" :key="stat.label">
        <CardHeader
          class="flex flex-row items-center justify-between space-y-0 pb-2"
        >
          <CardTitle class="text-sm font-medium">{{ stat.label }}</CardTitle>
          <component :is="stat.icon" class="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stat.value }}</div>
          <p class="text-xs text-muted-foreground">{{ stat.change }}</p>
        </CardContent>
      </Card>
    </div>

    <!-- Main content card -->
    <Card>
      <CardHeader>
        <CardTitle>All Projects</CardTitle>
        <CardDescription
          >A list of all projects in your organization</CardDescription
        >
      </CardHeader>
      <CardContent>
        <!-- Table, list, or grid content here -->
      </CardContent>
    </Card>
  </div>
</template>
```

---

## Empty States

When a section has no data, show a helpful empty state instead of a blank area:

```vue
<Card>
  <CardContent class="flex flex-col items-center justify-center py-12">
    <FolderKanban class="size-12 text-muted-foreground/40" />
    <h3 class="mt-4 text-lg font-medium">No projects yet</h3>
    <p class="mt-2 text-sm text-muted-foreground text-center max-w-sm">
      Get started by creating your first project. You can organize work, track progress, and collaborate with your team.
    </p>
    <Button class="mt-6">
      <Plus class="mr-2 size-4" />
      Create Project
    </Button>
  </CardContent>
</Card>
```
