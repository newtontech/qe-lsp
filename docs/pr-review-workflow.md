# PR Review Workflow

This document describes the review workflow for qe-lsp pull requests.

## Review States

When you submit a PR, reviewers will apply one of these labels:

### ✅ Merge
The PR is ready to merge. All checks pass and the implementation aligns with project conventions.

### 🔧 Modify
The PR needs changes before it can be merged. Reviewers will provide specific feedback on what needs to be addressed.

### ⏸️ Hold
The PR is conceptually sound but should wait for other work (dependencies, broader discussion, or scheduled merge windows).

## Review Process

1. **Automated Checks**: CI must pass (tests, code quality, type checking)
2. **Manual Review**: At least one maintainer reviews the implementation
3. **Decision**: Maintainer applies Merge/Modify/Hold label
4. **Iteration**: If Modify, address feedback and request re-review
5. **Merge**: Once approved, the PR will be merged by maintainers

## Codex Subagent Review

This project uses parallel Codex subagent review lanes for efficiency:

- Each subagent focuses on specific aspects (testing, documentation, type safety)
- Parallel reviews reduce turnaround time
- All subagent feedback is consolidated before maintainer decision

## Review Criteria

### Code Quality
- Follows project style guidelines (black formatting, type hints)
- Adequate test coverage for new features
- No regression in existing functionality

### Documentation
- README updated if user-facing features change
- Code comments for complex logic
- Docstrings for public APIs

### QE Semantics
- Accurate Quantum ESPRESSO syntax and semantics
- Proper error messages and diagnostics
- Validation rules match QE specification

### LSP Protocol
- Correct LSP message handling
- Proper feature registration
- Appropriate error handling

## Timeline

- Initial review response: within 2-3 business days
- Modify feedback: specific, actionable items
- Re-review: within 1-2 business days after updates
- Merge: after approval + CI passes

## Questions

If you have questions about the review process, ask in the PR or open a discussion.