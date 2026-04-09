# Passenger-Only Tool Design

## Goal

Remove all functionality except passenger information extraction. The app should expose a single tool that extracts passenger names and passenger numbers from copied booking text.

## Scope

- Remove the date formatter route, view, and navigation entry.
- Remove the basic text cleanup mode from the text formatter view.
- Keep the passenger extraction workflow, guide content, sample data, and copy behavior.
- Update documentation so the project description matches the reduced scope.

## Resulting UX

- The app opens directly to the text formatter page.
- The sidebar contains one entry: `文本整理`.
- The page presents one workflow only: paste passenger data, extract passenger info, copy the result.

## Constraints

- Preserve the current passenger extraction behavior.
- Do not leave dead UI branches, route branches, or mode persistence for removed features.
