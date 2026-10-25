# DSA Study

A personal app for one learner to work through a fixed number of study sessions on data structures and algorithms, keeping a record of every problem solved and how it was solved.

## Language

**Plan**:
The learner's full run of 70 Sessions, from the first diagnostic Session to the last.
_Avoid_: Course, program, roadmap, curriculum

**Problem**:
A single DSA exercise in the problem bank, with a statement, a topic, and the pattern that solves it.
_Avoid_: Question, exercise, challenge

**Problem Bank**:
The learner's collection of every Problem they have worked on or queued, regardless of where it came from.
_Avoid_: Database, library, catalog

**Topic**:
The broad DSA area a Problem belongs to, such as Heaps or Dynamic Programming. Each Problem has exactly one.
_Avoid_: Category, area, chapter

**Pattern**:
A named, reusable technique for solving Problems, such as "monotonic stack" or "prefix sum + hashmap". A Problem can be tagged with several.
_Avoid_: Trick, technique, approach

**Notes**:
The learner's own free-text explanation of how a Problem is solved, kept on the Problem and revised after any Attempt.
_Avoid_: Comments, write-up

**Source**:
Where a Problem came from: LeetCode, proposed by Claude, or the original diagnostic.
_Avoid_: Origin, provider

**Session**:
One sitting in which the learner works on new Problems and re-solves old ones. Sessions are numbered in order.
_Avoid_: Study block, sitting, day

**Attempt**:
One timed try at a Problem within a Session, ending when the learner passes or gives up. An Attempt can contain several Submissions.
_Avoid_: Try, run

**Submission**:
One check of the learner's code against all of a Problem's tests during an Attempt.
_Avoid_: Run, check

**Time Cap**:
The 30-minute limit on an Attempt. The learner may keep working past it, but the Attempt is then over the cap.
_Avoid_: Timeout, deadline

**Hint**:
One of three pre-written aids for a Problem, each giving away more than the last: a nudge, then the Pattern, then the key insight. The learner reveals them in order during an Attempt, and the Attempt records how many were used.
_Avoid_: Tip, clue, help

**Review**:
An Attempt at a Problem the learner has attempted before, scheduled by Session count rather than calendar time.
_Avoid_: Revision, repeat, re-solve

**Clean Attempt**:
An Attempt whose solution passes every test within 20 minutes without using any Hint.
_Avoid_: Success, solve, pass

**Review Ladder**:
The sequence of gaps between Reviews of a Problem: 2, then 6, then 15 Sessions. A Clean Attempt moves the Problem up one step; any other Attempt sends it back to the first step.
_Avoid_: Schedule, spaced repetition

### Problem status

**New**:
The status of a Problem the learner has never attempted.
_Avoid_: Queued, unsolved, todo

**In Review**:
The status of a Problem on the Review Ladder, with a step and the Session in which its next Review is due.
_Avoid_: Learning, active, pending

**Mastered**:
The status of a Problem that has cleared the last step of the Review Ladder and is no longer scheduled for Review.
_Avoid_: Done, complete, learned

### Progress

**Topic Block**:
The run of consecutive Sessions in which a Topic's New Problems are introduced. Topic Blocks follow a fixed order and cover Sessions 3–55.
_Avoid_: Unit, module, phase

**Mixed Set**:
A Session in the final stretch of the Plan (Sessions 56–70) whose New Problems are drawn from any Topic.
_Avoid_: Mock, random session

**Topic Strength**:
A Topic's rating of Solid, Shaky or Weak, based on the share of its Problems whose most recent Attempt was clean.
_Avoid_: Score, level, grade
