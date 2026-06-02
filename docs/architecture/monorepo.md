# Monorepo Architecture

## Overview

Beacon is organized as a monorepo.

The project consists of multiple applications and shared packages that evolve together and share common business concepts. A monorepo allows all components to be versioned, reviewed, and released from a single source of truth.

## Goals

The monorepo structure is intended to provide:

* Consistent development workflows
* Shared type definitions
* Easier onboarding
* Simplified dependency management
* Unified CI/CD pipelines
* Coordinated changes across applications

## Repository Layout

```text
beacon/
│
├── apps/
│   ├── web/
│   ├── api/
│   └── contracts/
│
├── packages/
│   ├── sdk/
│   ├── types/
│   └── config/
│
├── docs/
├── scripts/
└── .github/
```

---

## Applications

### apps/web

Future Nuxt 3 frontend application.

Responsibilities:

* User interface
* Wallet connection
* Recommendation browsing
* Recommendation creation
* User profiles
* Leaderboards
* Analytics dashboards

---

### apps/api

Future Django backend application.

Responsibilities:

* Business logic
* Recommendation management
* Search
* Ranking algorithms
* Reward calculations
* Moderation tools
* Administrative interfaces

---

### apps/contracts

Future Solana smart contracts developed with Anchor.

Responsibilities:

* Stake management
* Reward distribution
* Treasury management
* Lock periods
* On-chain verification

Only economic and trust-sensitive functionality should live on-chain.

---

## Shared Packages

### packages/sdk

Shared SDK for interacting with Beacon services and smart contracts.

Potential responsibilities:

* Solana transaction helpers
* API client utilities
* Contract interaction abstractions

---

### packages/types

Shared TypeScript types and schemas.

Examples:

* Recommendation
* UserProfile
* RewardDistribution
* WalletProfile

The goal is to avoid duplicate type definitions across applications.

---

### packages/config

Shared configuration files.

Examples:

* ESLint
* Prettier
* TypeScript settings
* Environment templates

---

## Design Philosophy

### Keep Business Logic Centralized

Business logic should primarily reside in the backend.

The frontend should focus on presentation and user experience.

---

### Keep Blockchain Usage Minimal

Only functionality requiring trustless execution should be implemented on-chain.

Examples:

* Stakes
* Rewards
* Treasury operations

Everything else should remain off-chain for flexibility and lower cost.

---

### Prefer Simplicity

The project should begin as a modular monolith.

Avoid:

* Microservices
* Event buses
* Service meshes
* Premature distributed architectures

The architecture should evolve only when justified by actual product needs.

---

## Future Additions

Potential future directories:

```text
apps/mobile/
apps/indexer/

packages/ui/
packages/contracts-client/

infrastructure/
```

These should only be introduced when there is a clear requirement.

## Architectural Principle

Beacon's competitive advantage comes from its curation marketplace and community, not from architectural complexity.

The repository should remain simple, understandable, and easy for contributors to navigate.
