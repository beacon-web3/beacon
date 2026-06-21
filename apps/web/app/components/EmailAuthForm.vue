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
  <div class="beacon-container py-20 sm:py-28">
    <UCard class="mx-auto max-w-xl">
      <h1 class="font-serif text-4xl font-semibold tracking-[-0.045em] text-ink">
        {{ t(title) }}
      </h1>
      <p class="mt-4 leading-7 text-ink-muted">
        {{ t(description) }}
      </p>

      <form
        class="mt-8 space-y-5"
        @submit.prevent="submit"
      >
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
          class="w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink shadow-sm outline-none transition placeholder:text-ink-faint focus:border-reputation focus:ring-4 focus:ring-reputation/15"
        >

        <p
          v-if="successText"
          role="status"
          class="rounded-xl border border-reputation/20 bg-reputation/10 px-4 py-3 text-sm font-medium text-reputation"
        >
          {{ successText }}
        </p>
        <p
          v-if="errorText"
          role="alert"
          class="rounded-xl bg-red-50 px-4 py-3 text-sm font-medium text-red-700 dark:bg-red-950/30 dark:text-red-300"
        >
          {{ errorText }}
        </p>

        <div class="flex flex-col gap-3 sm:flex-row">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="inline-flex justify-center rounded-xl bg-reputation px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-reputation/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ isSubmitting ? t('auth.submitting') : t(submitLabel) }}
          </button>
          <UButton
            :to="localePath(alternateTo)"
            :label="t(alternateLabel)"
            variant="outline"
            color="neutral"
            class="justify-center"
          />
        </div>
      </form>
    </UCard>
  </div>
</template>
