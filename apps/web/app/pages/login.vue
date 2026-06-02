<template>
  <UContainer class="py-24">
    <UCard class="mx-auto max-w-xl text-center">
      <UBadge
        color="primary"
        variant="subtle"
        :label="$t('auth.comingSoon')"
        class="mb-4"
      />
      <h1
        class="text-3xl font-black tracking-tight text-neutral-950 dark:text-white"
      >
        {{ $t('auth.loginTitle') }}
      </h1>
      <p class="mt-4 text-neutral-600 dark:text-neutral-300">
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
  </UContainer>
</template>
