# Bot for Harvester GitHub issue management

This repo helps to automate the Harvester issue and project management with:
- Auto-create [pre ready-for-testing checklist](./github-bot/harvester_github_bot/templates/pre-merge.md) when the issue is moved to the `Review` pipeline.
- Auto-create automation-related e2e test issue (by adding `not-require/test-plan` label).
- Auto-create a backport issue when an issue contains the `backport-needed/*` label.

## Bootstrap

Before starting this bot, you should setup following env and run that commands:

```sh
export GITHUB_TOKEN="" 
export GITHUB_OWNER="" 
export GITHUB_REPOSITORY=
export DEVELOPER_GITHUB_PROJECT_NUMBER=""
export COMMUNITY_GITHUB_PROJECT_NUMBER=""
export WORKING_STATUS="Analysis/Design,Implement,Review,Ready For Testing"
export E2E_PIPELINE="Review,Ready For Testing,Testing" # example
export FLASK_USERNAME="" # Use basic auth here, such as http://username:passowrd@localhost:8080
export FLASK_PASSWORD=""
export GITHUB_REPOSITORY_TEST=""
cd github-bot
gunicorn harvester_github_bot:app
```

## Deployment

1.How do we deploy harvester github bot?
-> We use docker-compose.

2. How do we rollout the latest image?
-> We use watchover.

## Features

There are two webhooks deal with different features:

1. Github Repository Webhook (`GITHUB_TOKEN`)  
    When adding backport label on the Github, this bot will handle webhook to do following things:
    - Create an issue in `GITHUB_REPOSITORY`.
2. Github Organization Webook 
    - When moving the issue to specified pipleline (`E2E_PIPELINE`) in developer Github Project (`DEVELOPER_GITHUB_PROJECT_NUMBER`), this bot will handle the webhook to create comment in `GITHUB_REPOSITORY`, and create an issue in e2e testing repo (`GITHUB_REPOSITORY_TEST`).
    - When moving the issue to specified status (`WORKING_STATUS`) in developer Github Project (`DEVELOPER_GITHUB_PROJECT_NUMBER`), this bot will automatically add the issue to the current sprint.
    - When moving the issue to specficed status in community Github Proejct (`COMMUNITY_GITHUB_PROJECT_NUMBER`), this bot will add a milestone to the issue.

## References

Harvester-bot currently uses Github Project Grahql to create back

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
