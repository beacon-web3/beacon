# Accessibility Checklist

Use this reference for detailed accessibility checks when building or reviewing user-facing UI. Target WCAG 2.1 AA unless the project has a stricter standard.

## Semantics

- Use native elements before ARIA: `button`, `a`, `label`, `input`, `select`, `textarea`, `nav`, `main`, `section`, and headings.
- Use one `h1` per page and do not skip heading levels.
- Use `button` for actions and `a` for navigation.
- Avoid clickable `div` or `span` elements unless there is no native alternative and keyboard behavior is fully implemented.

## Keyboard

- Every interactive element is reachable with `Tab`.
- Focus order matches the visual and reading order.
- Focus is visible and not hidden by custom outlines or overlays.
- `Enter` and `Space` activate custom button-like controls when native buttons cannot be used.
- Dialogs, popovers, and menus manage focus on open and close.
- Escape closes dismissible overlays unless there is a product-specific reason not to.

## Names and Labels

- Every form control has a visible label or an accessible name.
- Icon-only buttons have `aria-label` or visible text for screen readers.
- Images have useful `alt` text, or empty `alt=""` when decorative.
- Form errors are associated with the relevant field using visible text and accessible relationships.

## State and Feedback

- Loading states communicate what is loading without trapping focus.
- Error states explain what happened and how to recover.
- Empty states explain the state and offer a next step when appropriate.
- Success, warning, and error states are not conveyed by color alone.
- Live regions are used sparingly and only for changes users need announced.

## Visual Design

- Normal text contrast is at least 4.5:1.
- Large text and meaningful icons have at least 3:1 contrast.
- UI remains usable at 200% zoom.
- Touch targets are large enough for mobile use and have adequate spacing.
- Motion respects reduced-motion preferences when animations are non-essential.

## Testing

- Navigate the complete flow with keyboard only.
- Test with a screen reader for core flows when practical.
- Run axe-core, browser dev tools accessibility checks, or the project's existing accessibility tooling.
- Test responsive layouts at 320px, 768px, 1024px, and 1440px.
- Check loading, error, and empty states, not only the happy path.
