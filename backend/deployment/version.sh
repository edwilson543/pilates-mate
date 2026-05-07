#!/usr/bin/env bash
#
# Determine the current version of the application as a positive integer.
# This is derived by counting the number of merge commits on the main branch.
#

set -euo pipefail

function get_version {
    local commit="${1:-HEAD}"

    # Get the full commit SHA
    commit=$(git rev-parse "$commit")

    # Check if this commit is on the main branch
    if git merge-base --is-ancestor "$commit" origin/main 2>/dev/null; then
        # Count first-parent commits (merge commits) up to this point
        version=$(git rev-list --count --first-parent "$commit")
    else
        # For commits not on main, find the version of the last main branch commit
        # in this branch's history
        merge_base=$(git merge-base "$commit" origin/main)
        base_version=$(git rev-list --count --first-parent "$merge_base")

        # Add dev suffix with commit count since divergence
        extra_commits=$(git rev-list --count "$commit" --not "$merge_base")
        short_sha=$(git rev-parse --short=7 "$commit")

        version="${base_version}.dev${extra_commits}+${short_sha}"
    fi

    echo "$version"
}

# Run the function
get_version "$@"
