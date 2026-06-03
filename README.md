# Beacon

> A decentralized discovery marketplace where people stake money behind recommendations.

## Vision

The internet is entering an era of content abundance.

As AI dramatically reduces the cost of creating books, videos, games, articles, music, and ideas, the challenge shifts from creation to discovery. Finding content worth our attention becomes increasingly difficult as the volume of available content grows.

Beacon is designed to address this problem by creating a market for curation.

Instead of relying solely on likes, ratings, or algorithms, users put real value behind their recommendations. By introducing financial commitment into the recommendation process, Beacon aims to surface stronger signals and reward users who discover quality content before it becomes widely recognized.

## How It Works

### Recommendation Creation

Users create recommendations by locking a stake for a fixed period.

This stake acts as a commitment mechanism and discourages low-effort or spam submissions.

### Community Support

Other users can support recommendations they believe in by contributing a small amount of SOL.

Support is not a refundable vote. It represents conviction.

### Reward Distribution

As recommendations gain traction, rewards are distributed among:

* The original curator
* Early supporters
* The protocol treasury

The exact reward model is documented in the tokenomics section.

## Initial Focus

The first version of Beacon focuses exclusively on books.

Books provide a focused environment to validate the core hypothesis:

> Are people willing to financially back recommendations they genuinely believe in?

Once validated, the platform may expand into:

* Movies
* TV Series
* Video Games
* Podcasts
* Educational Content
* Business Ideas
* Startups
* Products

## Planned Technology Stack

### Frontend

* Nuxt 3
* TypeScript

### Backend

* Django
* Django REST Framework

### Database

* PostgreSQL

### Blockchain

* Solana
* Anchor Framework

### Infrastructure

* Docker
* GitHub Actions
* Cloud Hosting (TBD)

## Repository Structure

```text
apps/
├── web/         # Nuxt frontend
├── api/         # Django backend
└── contracts/   # Solana smart contracts

packages/
├── sdk/         # Shared client SDK
├── types/       # Shared TypeScript types
└── config/      # Shared configuration

docs/            # Documentation
scripts/         # Development scripts
```

## Licensing

This repository uses multiple licenses.

### AGPL v3

Applies to:

* Frontend application
* Backend application

### Apache 2.0

Applies to:

* Solana smart contracts
* SDK packages

See individual LICENSE files for details.

## Project Status

Early planning and architecture phase.

No production code has been implemented yet.

## Development Workflow

Local frontend tooling is currently managed in `apps/web/` with pnpm. Local backend tooling is currently managed in `apps/api/` with a Python virtual environment.

Fast pre-commit checks are configured through the tracked hook at `.husky/pre-commit`. See `docs/development/git-hooks.md` for setup and usage details.

Testing is split by workspace. Frontend E2E tests use Playwright in `apps/web/`; backend tests use pytest in `apps/api/`. See `docs/development/testing.md` for commands and scope.

Local backend development can run through Docker Compose in `apps/api/`, including the Django API and PostgreSQL database. See `docs/development/database.md` for setup commands.

## Core Principle

In a world of infinite content, attention becomes the scarce resource.

Beacon rewards the people who help others discover what matters.
