**Overview

All requirements from ev1.pdf are added as issues to the Issue Board Requirements.  This evolution is also a milestone which allows for easy monitoring of time spent per issue.  Each section header has been created as a label and tagged to the respective requirements.  From there, Issue Boards for Frontend and Backend have been created and contain all the same requirements as issues.

**Creating Issues from Requirements

Each requirement must be broken into action items and a new issue created for each action item.  These action items are created within the Frontend and Backend Issue Boards as the action items pertain to each section.  Each new issue (action item) will need two additional labels:
1. The requirement number to which the action item applies/addresses
2. The phase at which the action item can be completed. 

Using this format, a list within an issue board can be created containing all the issues associated with a specific label, in this case we shall sort by Phase #.

***Example

Issue #34: Req-2.3. The administrator shall be able to add, modify, and remove racks within the system; users shall be able to review them.

* New Issue: Create functionality to add racks from the UI
* New label: Req-2.3
* New label: Phase 2

**Closing Issues

The git commands below can be used to close issues within GitLab

git commit -m "Your commit message here" -m "Close #Issue"
git push

