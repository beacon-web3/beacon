<script setup lang="ts">
defineProps<{
  mode: 'signup' | 'login' | 'password-reset' | 'password-reset-confirm'
  title: string
  description: string
  endpoint: string
  inputId: string
  submitLabel: string
  successMessage: string
  errorMessage: string
  alternateTo: string
  alternateLabel: string
  resetUid?: string
  resetToken?: string
  clearOnSuccess?: boolean
}>()

const { t } = useI18n()
</script>

<template>
  <div class="beacon-container py-16 sm:py-24">
    <section class="grid min-h-[calc(100vh-13rem)] gap-10 lg:grid-cols-[minmax(0,0.82fr)_minmax(22rem,0.58fr)] lg:items-center">
      <AuthContextPanel
        :title="title"
        :description="description"
      />

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

        <AuthForm
          :mode="mode"
          :endpoint="endpoint"
          :input-id="inputId"
          :submit-label="submitLabel"
          :success-message="successMessage"
          :error-message="errorMessage"
          :alternate-to="alternateTo"
          :alternate-label="alternateLabel"
          :reset-uid="resetUid"
          :reset-token="resetToken"
          :clear-on-success="clearOnSuccess"
        />
      </div>
    </section>
  </div>
</template>
