export default defineAppConfig({
  ui: {
    colors: {
      primary: 'beacon',
      secondary: 'ledger',
      neutral: 'slate'
    },
    icons: {
      loading: 'i-lucide-loader-circle',
      close: 'i-lucide-x',
      check: 'i-lucide-check',
      chevronDown: 'i-lucide-chevron-down',
      chevronRight: 'i-lucide-chevron-right',
      arrowLeft: 'i-lucide-arrow-left',
      arrowRight: 'i-lucide-arrow-right'
    },
    button: {
      slots: {
        base: 'cursor-pointer rounded-md font-semibold tracking-[-0.01em] transition-colors disabled:cursor-not-allowed aria-disabled:cursor-not-allowed',
        leadingIcon: 'shrink-0',
        trailingIcon: 'shrink-0'
      },
      variants: {
        block: {
          true: {
            base: 'w-full justify-center',
            trailingIcon: 'ms-0'
          }
        }
      },
      defaultVariants: {
        color: 'primary',
        variant: 'solid'
      }
    },
    badge: {
      slots: {
        base: 'rounded-sm font-semibold tracking-[0.08em] uppercase'
      },
      defaultVariants: {
        variant: 'subtle'
      }
    },
    card: {
      slots: {
        root: 'rounded-xl border border-rule bg-paper shadow-none ring-0',
        header: 'border-b border-rule',
        footer: 'border-t border-rule'
      }
    },
    input: {
      slots: {
        root: 'rounded-md',
        base: 'font-medium'
      }
    },
    modal: {
      slots: {
        content: 'rounded-xl border border-rule bg-paper shadow-ledger'
      }
    }
  }
})
