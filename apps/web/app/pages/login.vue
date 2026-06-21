<template>
  <main class="beacon-container py-20 sm:py-28">
    <UCard class="mx-auto max-w-xl text-center">
      <UBadge
        color="primary"
        variant="subtle"
        :label="$t('auth.comingSoon')"
        class="mb-4"
      />
      <h1 class="font-serif text-4xl font-semibold tracking-[-0.045em] text-ink">
        {{ $t('auth.loginTitle') }}
      </h1>
      <p class="mt-4 leading-7 text-ink-muted">
        {{ $t('auth.loginDescription') }}
      </p>
      <UButton
        :to="$localePath('/')"
        :label="$t('auth.backHome')"
        variant="outline"
        color="neutral"
        class="mt-8"
      />
    </UCard>
  </main>
</template>
