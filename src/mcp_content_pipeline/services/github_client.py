"""GitHub API client for markdown storage."""

from __future__ import annotations

import re
from datetime import datetime

from github import Auth, Github, GithubException, InputGitTreeElement
from slugify import slugify

from mcp_content_pipeline.models.schemas import SyncFileResult, SyncResult, VideoAnalysis, XDigestAnalysis


def generate_markdown(analysis: VideoAnalysis) -> str:
    """Generate a markdown file from an analysis result."""
    takeaways = "\n".join(f"- {t}" for t in analysis.key_takeaways)
    topics = ", ".join(analysis.topics)

    return f"""# {analysis.title}

**Channel:** {analysis.channel}
**URL:** {analysis.url}
**Analysed:** {analysis.date_analysed}
**Topics:** {topics}

---

**TL;DR:** {analysis.tldr}

{takeaways}
"""


def generate_x_digest_markdown(digest: XDigestAnalysis) -> str:
    """Generate a markdown file from an X digest analysis result."""
    accounts = ", ".join(digest.accounts)
    topics = ", ".join(digest.topics)
    takeaways = "\n".join(f"- {t}" for t in digest.key_takeaways)

    return f"""# {digest.title}

**Accounts:** {accounts}
**Analysed:** {digest.date_analysed}
**Topics:** {topics}
**Posts analysed:** {digest.post_count}

---

**TL;DR:** {digest.tldr}

{takeaways}
"""


def generate_x_digest_filename(digest: XDigestAnalysis, output_dir: str) -> str:
    """Generate a filename for an X digest markdown file."""
    try:
        date_str = datetime.fromisoformat(digest.date_analysed).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        date_str = datetime.now().strftime("%Y-%m-%d")

    return f"{output_dir}/{date_str}-x-digest.md"


def generate_filename(analysis: VideoAnalysis, output_dir: str) -> str:
    """Generate a filename for the analysis markdown file."""
    try:
        date_str = datetime.fromisoformat(analysis.date_analysed).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        date_str = datetime.now().strftime("%Y-%m-%d")

    slug = slugify(analysis.title, max_length=80)
    return f"{output_dir}/{date_str}-{slug}.md"


def parse_index_entries(index_content: str) -> dict[str, str]:
    """Parse existing index.md and return a dict of filename -> full table row."""
    entries: dict[str, str] = {}
    for line in index_content.split("\n"):
        if not line.startswith("|") or line.startswith("| Date") or line.startswith("|---"):
            continue
        # Extract filename from markdown link: [basename](./basename)
        match = re.search(r"\[([^\]]+\.md)\]", line)
        if match:
            key = match.group(1).replace(r"\|", "|")
            entries[key] = line
    return entries


def generate_index(
    analyses: list[VideoAnalysis],
    output_dir: str,
    existing_index_content: str | None = None,
) -> str:
    """Generate an index.md table; merges with existing_index_content if provided."""
    # Start with existing entries
    entries: dict[str, str] = {}
    if existing_index_content:
        entries = parse_index_entries(existing_index_content)

    # Add/overwrite with new analyses
    for analysis in analyses:
        filename = generate_filename(analysis, output_dir)
        basename = filename.split("/")[-1]
        try:
            date_str = datetime.fromisoformat(analysis.date_analysed).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            date_str = "Unknown"
        escaped_title = analysis.title.replace("|", r"\|")
        escaped_basename = basename.replace("|", r"\|")
        row = f"| {date_str} | {escaped_title} | [{escaped_basename}](./{escaped_basename}) |"
        entries[basename] = row

    # Sort rows by date descending (date is first column)
    sorted_rows = sorted(entries.values(), key=_extract_date_from_row, reverse=True)

    lines = [
        "# YouTube Analyses",
        "",
        "| Date | Title | File |",
        "|------|-------|------|",
        *sorted_rows,
        "",
    ]
    return "\n".join(lines)


def generate_x_digest_index(
    digests: list[XDigestAnalysis],
    output_dir: str,
    existing_index_content: str | None = None,
) -> str:
    """Generate an index.md table of X digests; merges with existing_index_content if provided."""
    entries: dict[str, str] = {}
    if existing_index_content:
        entries = parse_index_entries(existing_index_content)

    for digest in digests:
        filename = generate_x_digest_filename(digest, output_dir)
        basename = filename.split("/")[-1]
        try:
            date_str = datetime.fromisoformat(digest.date_analysed).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            date_str = "Unknown"
        escaped_title = digest.title.replace("|", r"\|")
        escaped_basename = basename.replace("|", r"\|")
        accounts = ", ".join(digest.accounts).replace("|", r"\|")
        row = f"| {date_str} | {escaped_title} | {accounts} | [{escaped_basename}](./{escaped_basename}) |"
        entries[basename] = row

    sorted_rows = sorted(entries.values(), key=_extract_date_from_row, reverse=True)

    lines = [
        "# X Feed Digests",
        "",
        "| Date | Title | Accounts | File |",
        "|------|-------|----------|------|",
        *sorted_rows,
        "",
    ]
    return "\n".join(lines)


def _extract_date_from_row(row: str) -> str:
    """Extract the date string from a table row for sorting."""
    parts = row.split("|")
    if len(parts) >= 2:
        return parts[1].strip()
    return ""


def _read_file(repo, path: str, branch: str) -> str | None:
    """Return a file's text on branch, or None if it does not exist."""
    try:
        return repo.get_contents(path, ref=branch).decoded_content.decode()  # type: ignore[union-attr]
    except GithubException:
        return None


async def sync_to_github(
    token: str,
    repo_name: str,
    branch: str,
    output_dir: str,
    analyses: list[VideoAnalysis],
    commit_message: str = "Add video analyses",
    x_digests: list[XDigestAnalysis] | None = None,
    x_output_dir: str | None = None,
) -> SyncResult:
    """Push analysis markdown files and their indexes to GitHub as a single commit."""
    x_digests = x_digests or []
    if not analyses and not x_digests:
        return SyncResult(files=[])

    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_name)
    x_dir = x_output_dir or output_dir

    changes: dict[str, str] = {}
    for analysis in analyses:
        changes[generate_filename(analysis, output_dir)] = generate_markdown(analysis)
    for digest in x_digests:
        changes[generate_x_digest_filename(digest, x_dir)] = generate_x_digest_markdown(digest)

    file_results = []
    for path, content in changes.items():
        current = _read_file(repo, path, branch)
        action = "created" if current is None else "unchanged" if current == content else "updated"
        file_results.append(SyncFileResult(path=path, action=action))

    # Indexes only change for the content type being synced
    index_paths: list[str] = []
    if analyses:
        path = f"{output_dir}/index.md"
        changes[path] = generate_index(analyses, output_dir, _read_file(repo, path, branch))
        index_paths.append(path)
    if x_digests:
        path = f"{x_dir}/index.md"
        changes[path] = generate_x_digest_index(x_digests, x_dir, _read_file(repo, path, branch))
        index_paths.append(path)

    ref = repo.get_git_ref(f"heads/{branch}")
    parent = repo.get_git_commit(ref.object.sha)
    tree = repo.create_git_tree(
        [InputGitTreeElement(path, "100644", "blob", content=content) for path, content in changes.items()],
        parent.tree,
    )
    if tree.sha == parent.tree.sha:
        return SyncResult(files=file_results, index_paths=index_paths)

    commit = repo.create_git_commit(commit_message, tree, [parent])
    ref.edit(commit.sha)

    return SyncResult(files=file_results, commit_sha=commit.sha, index_paths=index_paths)
