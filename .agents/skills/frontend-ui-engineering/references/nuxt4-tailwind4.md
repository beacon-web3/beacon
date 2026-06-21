# Nuxt 4 + Tailwind CSS 4 Reference

Use this reference when working in Nuxt 4, Vue single-file components, server routes, composables, layouts, pages, or Tailwind CSS 4.

## File Structure

Follow Nuxt 4 app directory conventions and keep server code outside UI components:

```
app/
  components/
    TaskList.vue
    TaskItem.vue
  composables/
    useTasks.ts
  layouts/
    default.vue
  pages/
    tasks.vue
server/
  api/
    tasks.get.ts
```

Preserve the existing project layout first. Do not move files solely to match this shape if the project already has an established Nuxt convention.

## Component Patterns

Prefer small Vue single-file components with `<script setup lang="ts">`, typed props, and explicit emitted events:

```vue
<script setup lang="ts">
type Task = {
  id: string;
  title: string;
  done: boolean;
};

defineProps<{
  task: Task;
}>();

const emit = defineEmits<{
  toggle: [taskId: string];
  delete: [taskId: string];
}>();
</script>

<template>
  <li class="flex items-center gap-3 rounded-lg border border-default p-3">
    <input
      type="checkbox"
      :checked="task.done"
      class="size-4 rounded border-default text-primary focus-visible:outline-2 focus-visible:outline-offset-2"
      :aria-label="`Mark ${task.title} as ${task.done ? 'incomplete' : 'complete'}`"
      @change="emit('toggle', task.id)"
    >
    <span :class="task.done ? 'text-muted line-through' : 'text-primary'">
      {{ task.title }}
    </span>
    <button
      type="button"
      class="ml-auto rounded-md px-2 py-1 text-sm text-muted hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2"
      @click="emit('delete', task.id)"
    >
      Delete
    </button>
  </li>
</template>
```

## Focused Components

Keep Vue components focused. If a component handles fetching, mutation, routing,
layout, local UI state, and reusable rendering at the same time, split page or
container concerns from presentation concerns.

Use `references/nuxt-focused-components.md` when you need explicit bad and
good examples for splitting page-level data concerns from reusable presentation
components.

## Data Fetching

Use Nuxt composables deliberately:

```vue
<script setup lang="ts">
const route = useRoute();
const page = computed(() => Number(route.query.page ?? 1));

const { data: tasks, status, error, refresh } = await useFetch('/api/tasks', {
  query: { page },
});
</script>

<template>
  <TaskListSkeleton v-if="status === 'pending'" />
  <ErrorState v-else-if="error" message="Failed to load tasks" @retry="refresh" />
  <EmptyState v-else-if="!tasks?.length" message="No tasks yet" />
  <TaskList v-else :tasks="tasks" />
</template>
```

Use `useFetch` or `useAsyncData` for server-aware data fetching. Avoid fetching the same data again on hydration unless the user explicitly refreshes or the route changes.

## State and SSR

- Use `ref` and `reactive` for local component state.
- Use `useState` only for SSR-safe state that must be shared across components during rendering and hydration.
- Keep browser-only APIs behind `import.meta.client`, `onMounted`, or `<ClientOnly>`.
- Avoid hydration mismatches: do not render time, random IDs, viewport-dependent values, or local storage values on the server unless they are deterministic.
- Put server endpoints in `server/api/` and keep UI components free of direct database or secret access.
- Keep route state in the URL when filters, sorting, search terms, or pagination should be shareable.

## Tailwind CSS 4

Tailwind CSS 4 is CSS-first. Prefer project tokens in CSS over JavaScript config when the project is using the v4 defaults:

```css
@import "tailwindcss";

@theme {
  --color-surface: oklch(0.99 0.01 255);
  --color-surface-muted: oklch(0.96 0.015 255);
  --color-default: oklch(0.86 0.02 255);
  --color-primary: oklch(0.48 0.18 260);
  --color-muted: oklch(0.48 0.03 255);
  --radius-card: 0.875rem;
}
```

Then use semantic utilities in templates:

```vue
<template>
  <section class="rounded-card border border-default bg-surface p-4 text-primary md:p-6">
    <p class="text-sm text-muted">Updated just now</p>
  </section>
</template>
```

## Tailwind Class Patterns

- Use existing `@theme` tokens before adding new ones.
- Prefer semantic names like `surface`, `muted`, and `primary` over literal names tied to one palette.
- Avoid arbitrary values like `p-[13px]` unless matching a precise design spec or third-party integration.
- Keep responsive classes mobile-first: base styles first, then `sm:`, `md:`, `lg:`, `xl:`.
- Avoid dynamic class strings that Tailwind cannot detect at build time. Map variants to complete class names instead.

```vue
<script setup lang="ts">
const toneClasses = {
  neutral: 'border-default bg-surface text-primary',
  warning: 'border-warning bg-warning-muted text-warning',
  success: 'border-success bg-success-muted text-success',
} as const;

defineProps<{
  tone: keyof typeof toneClasses;
}>();
</script>

<template>
  <div :class="['rounded-card border px-3 py-2', toneClasses[tone]]">
    <slot />
  </div>
</template>
```

## Nuxt Verification

- [ ] Nuxt pages hydrate without mismatch warnings
- [ ] Browser-only behavior is guarded with `import.meta.client`, `onMounted`, or `<ClientOnly>`
- [ ] Server routes live in `server/api/` and do not leak secrets to client components
- [ ] Tailwind CSS 4 classes use existing `@theme` tokens where possible
- [ ] Dynamic variants are mapped to complete class strings
- [ ] Responsive behavior is tested in Nuxt pages and reusable components
