
## Pre Ready-For-Testing Checklist
* [ ] **If labeled: require/HEP** Has the Harvester Enhancement Proposal PR submitted?
  The HEP PR is at:

* [ ] Where is the reproduce steps/test steps documented?
The reproduce steps/test steps are at:

* [ ] Is there a workaround for the issue? If so, where is it documented?
The workaround is at:

* [ ] Have the backend code been merged (harvester, harvester-installer, etc) (including `backport-needed/*`)?
The PR is at:

    * [ ] Does the PR include the explanation for the fix or the feature? 

    * [ ] Does the PR include deployment change (YAML/Chart)? If so, where are the PRs for both YAML file and Chart?
    The PR for the YAML change is at:
    The PR for the chart change is at:


* [ ] **If labeled: area/ui** Has the UI issue filed or ready to be merged?
The UI issue/PR is at:

* [ ] **If labeled: require/doc, require/knowledge-base** Has the necessary document PR submitted or merged?
The documentation/KB PR is at:

<!-- bot will auto create the e2e automation test issue using [the template](https://github.com/harvester/test/issues/new?assignees=&labels=area%2Ftest&template=test.md&title=%5BTEST%5D)) -->
* [ ] **If NOT labeled: not-require/test-plan** Has the e2e test plan been merged? Have QAs agreed on the automation test case? If only test case skeleton w/o implementation, have you created an implementation issue?
    - The automation skeleton PR is at:
    - The automation test case PR is at:

* [ ] **If the fix introduces the code for backward compatibility** Has a separate issue been filed with the label `release/obsolete-compatibility`?
The compatibility issue is filed at:
