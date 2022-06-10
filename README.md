# Bot for Harvester GitHub issue management [![Build Status](https://drone-publish.rancher.io/api/badges/harvester/bot/status.svg)](https://drone-publish.rancher.io/harvester/bot)

This repo helps to automate the Harvester issue and project management with:
- Auto-create [pre ready-for-testing checklist](./github-bot/harvester_github_bot/templates/pre-merge.md) when the issue is moved to the `Review` pipeline.
- Auto-create automation-related e2e test issue (by adding `not-require/test-plan` label).
- Auto-create a backport issue when an issue contains the `backport-needed/*` label.
