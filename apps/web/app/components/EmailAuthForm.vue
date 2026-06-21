<script setup lang="ts">
type AuthResponse = {
  account: {
    id: number
    email: string
  }
}

const props = defineProps<{
  title: string
  description: string
  endpoint: string
  inputId: string
  submitLabel: string
  successMessage: string
  errorMessage: string
  alternateTo: string
  alternateLabel: string
  clearOnSuccess?: boolean
}>()

const { t } = useI18n()
const localePath = useLocalePath()
const config = useRuntimeConfig()

const apiBaseUrl = computed(() => {
  return typeof config.public.apiBaseUrl === 'string'
    ? config.public.apiBaseUrl
    : undefined
})

const email = ref('')
const isSubmitting = ref(false)
const errorText = ref('')
const successText = ref('')

async function submit() {
  errorText.value = ''
  successText.value = ''
  isSubmitting.value = true

  try {
    const response = await $fetch<AuthResponse>(props.endpoint, {
      baseURL: apiBaseUrl.value,
      method: 'POST',
      body: { email: email.value }
    })

    successText.value = t(props.successMessage, { email: response.account.email })
    if (props.clearOnSuccess) {
      email.value = ''
    }
  } catch {
    errorText.value = t(props.errorMessage)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="beacon-container py-16 sm:py-24">
    <section class="grid min-h-[calc(100vh-13rem)] gap-10 lg:grid-cols-[minmax(0,0.82fr)_minmax(22rem,0.58fr)] lg:items-center">
      <div>
        <UBadge
          :label="t('auth.badge')"
          color="primary"
          variant="subtle"
          size="lg"
        />

        <h1 class="beacon-display mt-8 max-w-3xl text-5xl text-ink sm:text-6xl lg:text-7xl">
          {{ t(title) }}
        </h1>

        <p class="mt-7 max-w-2xl text-lg leading-8 text-ink-muted">
          {{ t(description) }}
        </p>

        <div class="mt-10 grid max-w-2xl gap-4 sm:grid-cols-3">
          <div class="border-t border-rule pt-4">
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-ink-faint">
              {{ t('auth.context.bookFirst.label') }}
            </p>
            <p class="mt-2 text-sm font-semibold text-ink">
              {{ t('auth.context.bookFirst.value') }}
            </p>
          </div>
          <div class="border-t border-rule pt-4">
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-ink-faint">
              {{ t('auth.context.wallet.label') }}
            </p>
            <p class="mt-2 text-sm font-semibold text-ink">
              {{ t('auth.context.wallet.value') }}
            </p>
          </div>
          <div class="border-t border-rule pt-4">
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-ink-faint">
              {{ t('auth.context.status.label') }}
            </p>
            <p class="mt-2 text-sm font-semibold text-ink">
              {{ t('auth.context.status.value') }}
            </p>
          </div>
        </div>
      </div>

      <div class="beacon-panel p-5 sm:p-6">
        <div class="flex items-start justify-between gap-5 border-b border-rule pb-5">
          <div>
            <p class="beacon-kicker">
              {{ t('auth.panelEyebrow') }}
            </p>
            <h2 class="mt-2 text-2xl font-semibold tracking-[-0.04em] text-ink">
              {{ t('auth.panelTitle') }}
            </h2>
          </div>
          <UIcon
            name="i-lucide-mail-plus"
            class="size-6 shrink-0 text-beacon-600 dark:text-beacon-300"
          />
        </div>

        <form
          class="mt-6 space-y-5"
          @submit.prevent="submit"
        >
          <div>
            <label
              :for="inputId"
              class="block text-sm font-semibold text-ink"
            >
              {{ t('auth.emailLabel') }}
            </label>
            <input
              :id="inputId"
              v-model="email"
              name="email"
              type="email"
              required
              autocomplete="email"
              :placeholder="t('auth.emailPlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <p class="text-sm leading-6 text-ink-muted">
            {{ t('auth.emailHelp') }}
          </p>

          <p
            v-if="successText"
            role="status"
            class="rounded-xl border border-reputation/25 bg-reputation-muted px-4 py-3 text-sm font-medium text-ink"
          >
            {{ successText }}
          </p>
          <p
            v-if="errorText"
            role="alert"
            class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700 dark:border-red-900/70 dark:bg-red-950/30 dark:text-red-300"
          >
            {{ errorText }}
          </p>

          <div class="grid gap-3">
            <UButton
              type="submit"
              :loading="isSubmitting"
              :disabled="isSubmitting"
              :label="isSubmitting ? t('auth.submitting') : t(submitLabel)"
              color="primary"
              size="xl"
              trailing-icon="i-lucide-arrow-right"
              block
            />
            <UButton
              :to="localePath(alternateTo)"
              :label="t(alternateLabel)"
              variant="ghost"
              color="neutral"
              size="lg"
              block
            />
          </div>
        </form>
      </div>
    </section>
  </div>
</template>
