# Nuxt Focused Components Reference

Use this reference when deciding whether Nuxt or Vue components should be split
by responsibility.

## Rule

Keep page-level orchestration separate from reusable presentation components
when the component is doing too much.

Page or container concerns:

- Route/query state
- `useFetch` or `useAsyncData`
- Loading, error, and empty-state branching
- Mutations that refresh server data
- Permission checks and page layout

Presentation component concerns:

- Render props
- Emit typed events
- Own small local UI state only when it is specific to that component

## Bad: Mixed Concerns

This is bad because one component owns route state, server data, mutation logic,
loading/error branches, and item rendering:

```vue
<script setup lang="ts">
const route = useRoute();
const page = computed(() => Number(route.query.page ?? 1));
const { data: tasks, status, error, refresh } = await useFetch('/api/tasks', {
  query: { page },
});

async function deleteTask(taskId: string) {
  await $fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
  await refresh();
}
</script>

<template>
  <TaskListSkeleton v-if="status === 'pending'" />
  <ErrorState v-else-if="error" message="Failed to load tasks" @retry="refresh" />
  <EmptyState v-else-if="!tasks?.length" message="No tasks yet" />
  <ul v-else>
    <li v-for="task in tasks" :key="task.id">
      {{ task.title }}
      <button type="button" @click="deleteTask(task.id)">Delete</button>
    </li>
  </ul>
</template>
```

## Good: Page and Presentation Split

This is good because the page owns route state, data fetching, and mutation
orchestration:

```vue
<!-- app/pages/tasks.vue -->
<script setup lang="ts">
const route = useRoute();
const page = computed(() => Number(route.query.page ?? 1));
const { data: tasks, status, error, refresh } = await useFetch('/api/tasks', {
  query: { page },
});

async function deleteTask(taskId: string) {
  await $fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
  await refresh();
}
</script>

<template>
  <TaskListSkeleton v-if="status === 'pending'" />
  <ErrorState v-else-if="error" message="Failed to load tasks" @retry="refresh" />
  <EmptyState v-else-if="!tasks?.length" message="No tasks yet" />
  <TaskList v-else :tasks="tasks ?? []" @delete="deleteTask" />
</template>
```

This is good because the reusable component only renders props and emits typed
events:

```vue
<!-- app/components/TaskList.vue -->
<script setup lang="ts">
type Task = {
  id: string;
  title: string;
};

defineProps<{
  tasks: Task[];
}>();

const emit = defineEmits<{
  delete: [taskId: string];
}>();
</script>

<template>
  <ul>
    <li v-for="task in tasks" :key="task.id">
      {{ task.title }}
      <button type="button" @click="emit('delete', task.id)">Delete</button>
    </li>
  </ul>
</template>
```
