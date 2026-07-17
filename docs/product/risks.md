---
type: Product Spec
title: Risk Register
description: Known product, economic, security, trust, and abuse risks with mitigation directions.
tags: [risks, security, trust, abuse, legal]
timestamp: 2026-07-17
---

# Risks

This document tracks known product, economic, security, and trust risks for Beacon.

## Self-Farming

An attacker may create a recommendation and support it from many wallets to capture curator and early supporter rewards.

Risk factors:

* Wallets are cheap to create.
* Wallet age and transaction history can be manufactured by sophisticated farmers.
* Early supporter rewards can be attractive if later organic users arrive.

Mitigation directions:

* Make farming economically unattractive through treasury retention and reward delays.
* Require meaningful curator stake locks.
* Monitor suspicious wallet clusters.
* Use wallet history only as a weak risk signal.
* Keep reward formulas conservative until real data is available.

## Ponzi Perception

Because some rewards are funded by later support activity, users may perceive Beacon as paying early users from later users.

Mitigation directions:

* Position Beacon around discovery reputation, not yield.
* Make NFT badges and curator track records central to the product.
* Add sustainable external revenue only after community approval.
* Use treasury staking yield to reduce dependence on future support activity.
* Avoid language that promises profit.

## Popularity Bias

Well-known books or series may dominate support because they are already
familiar.

Mitigation directions:

* Use one canonical page per standalone book work or recognized series.
* Preserve first-discoverer credit.
* Add freshness and category-specific ranking.
* Highlight emerging books separately from all-time leaders.
* Reward discovery quality, not just total support.

## Stalled Recommendations

Many recommendations may stall below the next reward milestone, leaving supporters without financial rewards.

Mitigation directions:

* Make milestone progress visible.
* Provide immediate badge rewards.
* Build profile reputation around early support.
* Consider periodic community-funded rewards for high-quality stalled recommendations.

## Governance Fatigue

If every decision requires voting, participation may collapse and execution may slow.

Mitigation directions:

* Restrict voting to major economic and policy decisions.
* Let the team handle operational and technical decisions.
* Use clear proposal categories and thresholds.
* Keep proposals specific and measurable.

## Treasury Trust Risk

Users may lose trust if treasury flows are unclear or if the team appears to extract hidden value.

Mitigation directions:

* Public treasury dashboard.
* Separate Community Treasury and Operating Reserve.
* Publish the operating reserve percentage before launch.
* Require governance approval for new revenue models.
* Use multisig or governance controls where appropriate.
* Use program-controlled Solana accounts for trust-sensitive user deposits,
  curator locks, reward pools, and Community Treasury balances wherever feasible.
* Publicly disclose any authority that can move funds or change fund movement
  rules.

## Custody And Private-Key Risk

Users may fear that developers, a company wallet, a backend server, or a
compromised private key could drain pooled SOL.

Mitigation directions:

* Avoid storing user deposits and community-controlled funds in ordinary
  externally owned wallets.
* Prefer Solana program-controlled accounts, such as PDAs, where no private key
  exists for the account.
* Use multisig for any remaining human-controlled authority.
* Publish treasury, program, multisig, governance, and upgrade authority
  addresses.
* Make custody/control status visible in the product dashboard.

## Smart Contract Bug Risk

Even if no person can directly steal funds, contract bugs can still cause loss,
locked funds, incorrect rewards, or unauthorized movement.

Mitigation directions:

* Keep on-chain responsibilities limited to trust-sensitive economic state.
* Keep contracts simple enough to audit and explain.
* Open-source production contracts before public launch.
* Obtain professional security review before contracts custody meaningful SOL.
* Publish audit reports and known limitations.
* Run localnet/devnet testing before production deployment.

## Upgrade Authority Risk

A program-controlled treasury can still require trust if an admin can upgrade the
program at any time and change fund movement rules.

Mitigation directions:

* Treat upgrade authority as part of the custody model.
* Disclose early-stage upgrade authority clearly.
* Prefer multisig over single-signer upgrade authority.
* Introduce timelocks before custody-affecting upgrades execute.
* Move upgrade authority toward governance as Beacon matures.
* Classify custody-affecting upgrades as high-impact governance actions.

## Staking Risk

Staked SOL introduces liquidity and validator risk.

Mitigation directions:

* Prefer native SOL staking at launch.
* Avoid complex DeFi strategies during MVP.
* Maintain liquidity buffers for unlocks and rewards.
* Publicly disclose staking approach and risks.

## Legal and Regulatory Risk

Beacon combines payments, rewards, staking, NFTs, and governance. These features may create regulatory issues depending on jurisdiction and framing.

Mitigation directions:

* Obtain legal review before launch.
* Avoid profit guarantees.
* Avoid marketing Beacon as an investment product.
* Keep user-facing language focused on discovery and reputation.
* Review NFT badge design for IP and securities concerns.

## Content and IP Risk

Book metadata, cover art, and recommendation pages can raise copyright and licensing issues.

Mitigation directions:

* Do not mint NFTs that imply ownership of books.
* Avoid unlicensed cover art in badge metadata.
* Use licensed metadata providers or user-generated curator notes.
* Provide moderation and takedown workflows.

## Open Questions

* What reward parameters make self-farming unprofitable?
* Which legal jurisdictions are launch targets?
* What content metadata source is safe for commercial use?
* What abuse signals should be monitored from day one?
* Which risks must block launch versus remain monitored post-launch?
* Which contracts must be audited before public launch?
* What level of formal verification or third-party review is required before
  custodying significant SOL?
* What multisig threshold and signer distribution are acceptable for early
  authority control?
* What timelock duration gives users enough time to inspect high-impact changes?
