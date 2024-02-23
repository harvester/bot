# Bot for Harvester GitHub issue management [![Build Status](https://drone-publish.rancher.io/api/badges/harvester/bot/status.svg)](https://drone-publish.rancher.io/harvester/bot)

This repo helps to automate the Harvester issue and project management with:
- Auto-create [pre ready-for-testing checklist](./github-bot/harvester_github_bot/templates/pre-merge.md) when the issue is moved to the `Review` pipeline.
- Auto-create automation-related e2e test issue (by adding `not-require/test-plan` label).
- Auto-create a backport issue when an issue contains the `backport-needed/*` label.


## License
Copyright (c) 2024 [SUSE](https://www.suse.com/)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
