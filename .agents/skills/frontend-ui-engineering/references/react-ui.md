# React UI Reference

Use this reference when working in React, TSX, React Query, SWR, Zustand, Redux, or similar React application code.

## File Structure

Colocate everything related to a component when the project allows it:

```
src/components/
  TaskList/
    TaskList.tsx          # Component implementation
    TaskList.test.tsx     # Tests
    TaskList.stories.tsx  # Storybook stories, if using
    use-task-list.ts      # Custom hook, if complex state
    types.ts              # Component-specific types, if needed
```

## Focused Components

```tsx
export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className="flex items-center gap-3 p-3">
      <Checkbox checked={task.done} onChange={() => onToggle(task.id)} />
      <span className={task.done ? 'line-through text-muted' : ''}>{task.title}</span>
      <Button variant="ghost" size="sm" onClick={() => onDelete(task.id)}>
        <TrashIcon />
      </Button>
    </li>
  );
}
```

Keep components focused. If a component handles fetching, mutation, routing, layout, and rendering, split container/page concerns from presentation concerns.

## Data and Presentation

```tsx
export function TaskListContainer() {
  const { tasks, isLoading, error, refetch } = useTasks();

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="Failed to load tasks" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="No tasks yet" />;

  return <TaskList tasks={tasks} />;
}

export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul role="list" className="divide-y">
      {tasks.map((task) => <TaskItem key={task.id} task={task} />)}
    </ul>
  );
}
```

## State Management

Choose the simplest approach that works:

```
Local state (useState)           Component-specific UI state
Lifted state                     Shared between 2-3 sibling components
Context                          Theme, auth, locale, read-heavy write-rare state
URL state (searchParams)         Filters, pagination, shareable UI state
Server state (React Query, SWR)  Remote data with caching
Global store (Zustand, Redux)    Complex client state shared app-wide
```

Follow the project's React Compiler guidance. Do not add `useMemo` or `useCallback` by default unless the project already relies on manual memoization or there is a measured need.

Use modern React APIs when appropriate and already supported by the project:

- `useEffectEvent` for event-like logic used inside effects.
- `startTransition` for non-urgent state updates that can yield to user input.
- `useDeferredValue` for expensive filtering or rendering that should lag behind typing.

## Accessibility Examples

Prefer native elements:

```tsx
<button onClick={handleClick}>Click me</button>
```

Avoid clickable non-interactive elements:

```tsx
<div onClick={handleClick}>Click me</div>
```

If there is no visible text, label the control:

```tsx
<button aria-label="Close dialog"><XIcon /></button>
```

Move focus when context changes:

```tsx
function Dialog({ isOpen, onClose }: DialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) closeRef.current?.focus();
  }, [isOpen]);

  return (
    <dialog open={isOpen}>
      <button ref={closeRef} onClick={onClose}>Close</button>
    </dialog>
  );
}
```

## Empty States

```tsx
function TaskList({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return (
      <div role="status" className="py-12 text-center">
        <TasksEmptyIcon className="mx-auto h-12 w-12 text-muted" />
        <h3 className="mt-2 text-sm font-medium">No tasks</h3>
        <p className="mt-1 text-sm text-muted">Get started by creating a new task.</p>
        <Button className="mt-4" onClick={onCreateTask}>Create Task</Button>
      </div>
    );
  }

  return <ul role="list">...</ul>;
}
```

## Loading and Optimistic Updates

```tsx
function TaskListSkeleton() {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="Loading tasks">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-12 animate-pulse rounded bg-muted" />
      ))}
    </div>
  );
}
```

```tsx
function useToggleTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData(['tasks']);

      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map((task) => task.id === taskId ? { ...task, done: !task.done } : task),
      );

      return { previous };
    },
    onError: (_err, _taskId, context) => {
      queryClient.setQueryData(['tasks'], context?.previous);
    },
  });
}
```

## React Verification

- [ ] Effects do not duplicate work unnecessarily in development strict mode
- [ ] Async requests are cancelled or ignored when components unmount where relevant
- [ ] Optimistic updates have rollback behavior
- [ ] Components remain usable with keyboard and screen readers
- [ ] Responsive behavior is tested on mobile and desktop widths
