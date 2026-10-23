"""Tests for the sync_to_github tool and GitHub client."""

from __future__ import annotations

import re

import pytest

from mcp_content_pipeline.models.schemas import VideoAnalysis, XDigestAnalysis
from mcp_content_pipeline.services.github_client import (
    generate_filename,
    generate_index,
    generate_markdown,
    generate_x_digest_index,
    generate_x_digest_markdown,
    parse_index_entries,
)
from mcp_content_pipeline.tools.sync_to_github import sync_to_github


@pytest.fixture
def analysis():
    return VideoAnalysis(
        title="ML in Production: 3 Strategies",
        channel="Tech Hub",
        url="https://www.youtube.com/watch?v=abc123",
        date_analysed="2026-03-08T12:00:00",
        key_takeaways=["Takeaway 1", "Takeaway 2", "Takeaway 3"],
        tldr="A short summary of the video content.",
        topics=["MLOps", "AI"],
    )


class TestGenerateMarkdown:
    def test_markdown_contains_title(self, analysis):
        md = generate_markdown(analysis)
        assert "# ML in Production: 3 Strategies" in md

    def test_markdown_contains_channel(self, analysis):
        md = generate_markdown(analysis)
        assert "**Channel:** Tech Hub" in md

    def test_markdown_contains_url(self, analysis):
        md = generate_markdown(analysis)
        assert "**URL:** https://www.youtube.com/watch?v=abc123" in md

    def test_markdown_contains_takeaways(self, analysis):
        md = generate_markdown(analysis)
        assert "- Takeaway 1" in md
        assert "- Takeaway 2" in md
        assert "- Takeaway 3" in md

    def test_markdown_contains_tldr(self, analysis):
        md = generate_markdown(analysis)
        assert "A short summary of the video content." in md

    def test_markdown_tldr_before_points(self, analysis):
        md = generate_markdown(analysis)
        assert f"**TL;DR:** {analysis.tldr}" in md
        assert md.index("**TL;DR:**") < md.index(f"- {analysis.key_takeaways[0]}")
        assert "Social Hook" not in md

    def test_markdown_contains_topics(self, analysis):
        md = generate_markdown(analysis)
        assert "**Topics:** MLOps, AI" in md


class TestGenerateXDigestMarkdown:
    def test_tldr_then_points(self):
        digest = XDigestAnalysis(
            title="AI Digest",
            accounts=["karpathy", "bcherny"],
            topics=["ai agents"],
            key_takeaways=["Point one (@karpathy)", "Point two (@bcherny)"],
            tldr="Agents are shipping.",
            post_count=4,
        )
        md = generate_x_digest_markdown(digest)
        assert "**Accounts:** karpathy, bcherny" in md
        assert "**Posts analysed:** 4" in md
        assert md.index("**TL;DR:** Agents are shipping.") < md.index("- Point one (@karpathy)")
        assert "Social Hook" not in md
        assert "Notable Posts" not in md


class TestGenerateFilename:
    def test_filename_format(self, analysis):
        filename = generate_filename(analysis, "content/youtube")
        assert filename == "content/youtube/2026-03-08-ml-in-production-3-strategies.md"

    def test_filename_slugification(self):
        a = VideoAnalysis(
            title="What's the Deal with AI? A Deep Dive!!!",
            channel="Test",
            url="https://youtube.com/watch?v=abc",
            date_analysed="2026-01-15T10:00:00",
            key_takeaways=["t1"],
            tldr="summary",
            topics=["AI"],
        )
        filename = generate_filename(a, "output")
        assert "what-s-the-deal-with-ai-a-deep-dive" in filename
        assert filename.endswith(".md")
        assert filename.startswith("output/2026-01-15-")

    def test_filename_long_title_truncated(self):
        a = VideoAnalysis(
            title="A" * 200,
            channel="Test",
            url="https://youtube.com/watch?v=abc",
            date_analysed="2026-01-01T00:00:00",
            key_takeaways=["t1"],
            tldr="s",
            topics=["t"],
        )
        filename = generate_filename(a, "out")
        # slug max_length=80, so filename should be reasonable length
        slug_part = filename.split("/")[-1]
        assert len(slug_part) < 120


class TestGenerateIndex:
    def test_index_contains_header(self, analysis):
        index = generate_index([analysis], "content/youtube")
        assert "# YouTube Analyses" in index

    def test_index_contains_table_headers(self, analysis):
        index = generate_index([analysis], "content/youtube")
        assert "| Date | Title | File |" in index

    def test_index_contains_entry(self, analysis):
        index = generate_index([analysis], "content/youtube")
        assert "ML in Production: 3 Strategies" in index
        assert "2026-03-08" in index

    def test_index_multiple_distinct_entries(self):
        a1 = VideoAnalysis(
            title="Video One",
            channel="C",
            url="https://youtube.com/watch?v=1",
            date_analysed="2026-03-08T12:00:00",
            key_takeaways=["t"],
            tldr="s",
            topics=["t"],
        )
        a2 = VideoAnalysis(
            title="Video Two",
            channel="C",
            url="https://youtube.com/watch?v=2",
            date_analysed="2026-03-09T12:00:00",
            key_takeaways=["t"],
            tldr="s",
            topics=["t"],
        )
        index = generate_index([a1, a2], "content/youtube")
        lines = [line for line in index.split("\n") if line.startswith("| 2026")]
        assert len(lines) == 2

    def test_index_empty_list(self):
        index = generate_index([], "content/youtube")
        assert "# YouTube Analyses" in index


class TestIndexMergeBehavior:
    """Tests for merging new analyses with existing index.md entries."""

    def _make_analysis(self, title: str, date: str) -> VideoAnalysis:
        return VideoAnalysis(
            title=title,
            channel="Channel",
            url="https://youtube.com/watch?v={title}",
            date_analysed=date,
            key_takeaways=["t"],
            tldr="s",
            topics=["t"],
        )

    def test_existing_entries_preserved(self):
        existing_index = (
            "# YouTube Analyses\n\n"
            "| Date | Title | File |\n"
            "|------|-------|------|\n"
            "| 2026-03-01 | Old Video | [2026-03-01-old-video.md](./2026-03-01-old-video.md) |\n"
        )
        new_analysis = self._make_analysis("New Video", "2026-03-10T12:00:00")
        index = generate_index([new_analysis], "content/youtube", existing_index)

        assert "Old Video" in index
        assert "New Video" in index

    def test_duplicates_deduplicated(self):
        existing_index = (
            "# YouTube Analyses\n\n"
            "| Date | Title | File |\n"
            "|------|-------|------|\n"
            "| 2026-03-08 | ML in Production: 3 Strategies | "
            "[2026-03-08-ml-in-production-3-strategies.md]"
            "(./2026-03-08-ml-in-production-3-strategies.md) |\n"
        )
        # Same analysis again — should deduplicate, not create two rows
        dup_analysis = self._make_analysis(
            "ML in Production: 3 Strategies", "2026-03-08T12:00:00"
        )
        index = generate_index([dup_analysis], "content/youtube", existing_index)

        data_rows = [
            line for line in index.split("\n") if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 1

    def test_new_entries_added(self):
        existing_index = (
            "# YouTube Analyses\n\n"
            "| Date | Title | File |\n"
            "|------|-------|------|\n"
            "| 2026-03-01 | First | [2026-03-01-first.md](./2026-03-01-first.md) |\n"
        )
        a1 = self._make_analysis("Second", "2026-03-05T12:00:00")
        a2 = self._make_analysis("Third", "2026-03-10T12:00:00")
        index = generate_index([a1, a2], "content/youtube", existing_index)

        assert "First" in index
        assert "Second" in index
        assert "Third" in index
        data_rows = [
            line for line in index.split("\n") if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 3

    def test_sorted_by_date_descending(self):
        existing_index = (
            "# YouTube Analyses\n\n"
            "| Date | Title | File |\n"
            "|------|-------|------|\n"
            "| 2026-03-01 | Oldest | [2026-03-01-oldest.md](./2026-03-01-oldest.md) |\n"
        )
        middle = self._make_analysis("Middle", "2026-03-05T12:00:00")
        newest = self._make_analysis("Newest", "2026-03-10T12:00:00")
        index = generate_index([middle, newest], "content/youtube", existing_index)

        data_rows = [
            line for line in index.split("\n") if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 3
        assert "Newest" in data_rows[0]
        assert "Middle" in data_rows[1]
        assert "Oldest" in data_rows[2]

    def test_no_existing_index(self):
        """When there's no existing index, behaves like before."""
        analysis = self._make_analysis("Only Video", "2026-03-08T12:00:00")
        index = generate_index([analysis], "content/youtube", None)

        assert "Only Video" in index
        data_rows = [
            line for line in index.split("\n") if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 1

    def test_parse_index_entries(self):
        content = (
            "# YouTube Analyses\n\n"
            "| Date | Title | File |\n"
            "|------|-------|------|\n"
            "| 2026-03-01 | Vid A | [2026-03-01-vid-a.md](./2026-03-01-vid-a.md) |\n"
            "| 2026-03-05 | Vid B | [2026-03-05-vid-b.md](./2026-03-05-vid-b.md) |\n"
        )
        entries = parse_index_entries(content)
        assert len(entries) == 2
        assert "2026-03-01-vid-a.md" in entries
        assert "2026-03-05-vid-b.md" in entries


class TestPipeEscaping:
    """Tests for pipe character escaping in markdown table rows."""

    def _make_analysis(self, title: str, date: str) -> VideoAnalysis:
        return VideoAnalysis(
            title=title,
            channel="Channel",
            url="https://youtube.com/watch?v=test",
            date_analysed=date,
            key_takeaways=["t"],
            tldr="s",
            topics=["t"],
        )

    def test_pipe_in_title_escaped_in_index(self):
        analysis = self._make_analysis("React | Vue | Angular", "2026-03-08T12:00:00")
        index = generate_index([analysis], "content/youtube")
        # The title should have escaped pipes so the table isn't broken
        assert r"React \| Vue \| Angular" in index

    def test_pipe_in_title_table_columns_intact(self):
        analysis = self._make_analysis("A | B", "2026-03-08T12:00:00")
        index = generate_index([analysis], "content/youtube")
        # Table rows should still have exactly 4 real column separators (leading, 3 between, trailing)
        data_rows = [
            line for line in index.split("\n")
            if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 1
        # Split on unescaped pipes only: count real columns
        cols = re.split(r"(?<!\\)\|", data_rows[0])
        # Leading empty + Date + Title + File + trailing empty = 5 parts
        assert len(cols) == 5

    def test_parse_index_entries_with_escaped_pipes(self):
        content = (
            "# YouTube Analyses\n\n"
            "| Date | Title | File |\n"
            "|------|-------|------|\n"
            r"| 2026-03-08 | React \| Vue | [2026-03-08-react-vue.md](./2026-03-08-react-vue.md) |"
            "\n"
        )
        entries = parse_index_entries(content)
        assert "2026-03-08-react-vue.md" in entries

    def test_roundtrip_pipe_in_title(self):
        """Generate index, parse it back, then merge — should not duplicate."""
        analysis = self._make_analysis("Foo | Bar", "2026-03-08T12:00:00")
        index = generate_index([analysis], "content/youtube")
        # Parse and re-generate with the same analysis
        index2 = generate_index([analysis], "content/youtube", index)
        data_rows = [
            line for line in index2.split("\n")
            if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 1


class TestSyncToGithub:
    @pytest.mark.asyncio
    async def test_sync_commit_message_too_long(self, analysis):
        from mcp_content_pipeline.config import Settings

        settings = Settings(
            pipeline_api_key="test",
            github_token="token",
            github_repo="owner/repo",
        )
        with pytest.raises(ValueError, match="500 characters or fewer"):
            await sync_to_github(
                analyses=[analysis], settings=settings, commit_message="A" * 501
            )

    @pytest.mark.asyncio
    async def test_sync_commit_message_empty(self, analysis):
        from mcp_content_pipeline.config import Settings

        settings = Settings(
            pipeline_api_key="test",
            github_token="token",
            github_repo="owner/repo",
        )
        with pytest.raises(ValueError, match="must not be empty"):
            await sync_to_github(
                analyses=[analysis], settings=settings, commit_message="   "
            )

    @pytest.mark.asyncio
    async def test_sync_commit_message_at_limit(self, analysis):
        from mcp_content_pipeline.config import Settings

        settings = Settings(
            pipeline_api_key="test",
            github_token="token",
            github_repo="owner/repo",
        )
        # Should not raise for commit_message validation — will fail on GitHub call instead
        with pytest.raises(Exception):
            await sync_to_github(
                analyses=[analysis], settings=settings, commit_message="A" * 500
            )

    @pytest.mark.asyncio
    async def test_sync_missing_token(self, analysis):
        from mcp_content_pipeline.config import Settings

        settings = Settings(
            pipeline_api_key="test",
            github_token="",
            github_repo="owner/repo",
        )
        with pytest.raises(ValueError, match="GitHub token not configured"):
            await sync_to_github(analyses=[analysis], settings=settings)

    @pytest.mark.asyncio
    async def test_sync_missing_repo(self, analysis):
        from mcp_content_pipeline.config import Settings

        settings = Settings(
            pipeline_api_key="test",
            github_token="token",
            github_repo="",
        )
        with pytest.raises(ValueError, match="GitHub repo not configured"):
            await sync_to_github(analyses=[analysis], settings=settings)


class TestGenerateXDigestIndex:
    def _make_digest(self, title: str, date: str, accounts: list[str] | None = None) -> XDigestAnalysis:
        return XDigestAnalysis(
            title=title,
            date_analysed=date,
            accounts=accounts or ["karpathy", "bcherny"],
            topics=["AI"],
            key_takeaways=["t"],
            tldr="s",
            post_count=5,
        )

    def test_index_contains_header(self):
        digest = self._make_digest("Daily Digest", "2026-03-08T12:00:00")
        index = generate_x_digest_index([digest], "content/x-digest")
        assert "# X Feed Digests" in index

    def test_index_contains_table_headers(self):
        digest = self._make_digest("Daily Digest", "2026-03-08T12:00:00")
        index = generate_x_digest_index([digest], "content/x-digest")
        assert "| Date | Title | Accounts | File |" in index

    def test_index_contains_entry(self):
        digest = self._make_digest("Daily Digest", "2026-03-08T12:00:00")
        index = generate_x_digest_index([digest], "content/x-digest")
        assert "Daily Digest" in index
        assert "2026-03-08" in index
        assert "karpathy, bcherny" in index

    def test_existing_entries_preserved(self):
        existing_index = (
            "# X Feed Digests\n\n"
            "| Date | Title | Accounts | File |\n"
            "|------|-------|----------|------|\n"
            "| 2026-03-01 | Old Digest | karpathy | [2026-03-01-x-digest.md](./2026-03-01-x-digest.md) |\n"
        )
        new_digest = self._make_digest("New Digest", "2026-03-10T12:00:00")
        index = generate_x_digest_index([new_digest], "content/x-digest", existing_index)
        assert "Old Digest" in index
        assert "New Digest" in index

    def test_sorted_by_date_descending(self):
        existing_index = (
            "# X Feed Digests\n\n"
            "| Date | Title | Accounts | File |\n"
            "|------|-------|----------|------|\n"
            "| 2026-03-01 | Oldest | karpathy | [2026-03-01-x-digest.md](./2026-03-01-x-digest.md) |\n"
        )
        newest = self._make_digest("Newest", "2026-03-10T12:00:00")
        index = generate_x_digest_index([newest], "content/x-digest", existing_index)
        data_rows = [
            line for line in index.split("\n") if line.startswith("|") and "Date" not in line and "---" not in line
        ]
        assert len(data_rows) == 2
        assert "Newest" in data_rows[0]
        assert "Oldest" in data_rows[1]

    def test_empty_list(self):
        index = generate_x_digest_index([], "content/x-digest")
        assert "# X Feed Digests" in index


def _mock_repo(existing: dict[str, str] | None = None):
    """Mock repo whose get_contents serves `existing` paths and 404s the rest."""
    from unittest.mock import MagicMock

    from github import GithubException

    existing = existing or {}

    def get_contents(path, ref=None):
        if path not in existing:
            raise GithubException(404, "Not found", None)
        return MagicMock(decoded_content=existing[path].encode())

    repo = MagicMock()
    repo.get_contents.side_effect = get_contents
    repo.create_git_commit.return_value = MagicMock(sha="abc123")
    repo.create_git_tree.return_value = MagicMock(sha="new-tree")
    return repo


async def _sync(repo, analyses=(), x_digests=None):
    from unittest.mock import patch

    from mcp_content_pipeline.services.github_client import sync_to_github as _sync_gh

    with patch("mcp_content_pipeline.services.github_client.Github") as mock_github:
        mock_github.return_value.get_repo.return_value = repo
        return await _sync_gh(
            token="token",
            repo_name="owner/repo",
            branch="main",
            output_dir="content/youtube",
            analyses=list(analyses),
            commit_message="test",
            x_digests=x_digests,
            x_output_dir="content/x-digest",
        )


def _tree_paths(repo) -> list[str]:
    elements = repo.create_git_tree.call_args.args[0]
    return [e._identity["path"] for e in elements]


@pytest.fixture
def digest():
    return XDigestAnalysis(
        title="Daily Digest",
        date_analysed="2026-03-08T12:00:00",
        accounts=["karpathy"],
        topics=["AI"],
        key_takeaways=["t"],
        tldr="s",
        post_count=5,
    )


class TestSyncSingleCommit:
    @pytest.mark.asyncio
    async def test_video_and_digest_in_one_commit(self, analysis, digest):
        repo = _mock_repo()
        result = await _sync(repo, [analysis], [digest])

        repo.create_git_commit.assert_called_once()
        repo.get_git_ref.return_value.edit.assert_called_once_with("abc123")
        repo.create_file.assert_not_called()
        repo.update_file.assert_not_called()
        assert sorted(_tree_paths(repo)) == [
            "content/x-digest/2026-03-08-x-digest.md",
            "content/x-digest/index.md",
            "content/youtube/2026-03-08-ml-in-production-3-strategies.md",
            "content/youtube/index.md",
        ]
        assert result.commit_sha == "abc123"
        assert result.index_paths == ["content/youtube/index.md", "content/x-digest/index.md"]

    @pytest.mark.asyncio
    async def test_digest_only_leaves_youtube_index_alone(self, digest):
        repo = _mock_repo()
        result = await _sync(repo, [], [digest])

        assert sorted(_tree_paths(repo)) == ["content/x-digest/2026-03-08-x-digest.md", "content/x-digest/index.md"]
        assert result.index_paths == ["content/x-digest/index.md"]

    @pytest.mark.asyncio
    async def test_video_only_leaves_x_index_alone(self, analysis):
        repo = _mock_repo()
        await _sync(repo, [analysis])

        assert all(p.startswith("content/youtube/") for p in _tree_paths(repo))

    @pytest.mark.asyncio
    async def test_nothing_to_sync_makes_no_commit(self):
        repo = _mock_repo()
        result = await _sync(repo, [], None)

        repo.create_git_commit.assert_not_called()
        assert result.files == []
        assert result.commit_sha is None

    @pytest.mark.asyncio
    async def test_created_vs_updated_and_index_merge(self, analysis):
        existing_md = "content/youtube/2026-03-08-ml-in-production-3-strategies.md"
        old_row = "| 2026-01-01 | Old Video | [2026-01-01-old-video.md](./2026-01-01-old-video.md) |"
        repo = _mock_repo({
            existing_md: "old",
            "content/youtube/index.md": f"# YouTube Analyses\n\n| Date | Title | File |\n|------|-------|------|\n{old_row}\n",
        })
        result = await _sync(repo, [analysis])

        assert result.files[0].action == "updated"
        index = next(e for e in repo.create_git_tree.call_args.args[0] if e._identity["path"] == "content/youtube/index.md")
        assert old_row in index._identity["content"]
        assert "ML in Production: 3 Strategies" in index._identity["content"]

    @pytest.mark.asyncio
    async def test_identical_content_makes_no_commit(self, analysis):
        from mcp_content_pipeline.services.github_client import generate_markdown

        path = "content/youtube/2026-03-08-ml-in-production-3-strategies.md"
        repo = _mock_repo({path: generate_markdown(analysis)})
        repo.create_git_tree.return_value = repo.get_git_commit.return_value.tree
        result = await _sync(repo, [analysis])

        repo.create_git_commit.assert_not_called()
        repo.get_git_ref.return_value.edit.assert_not_called()
        assert result.files[0].action == "unchanged"
        assert result.commit_sha is None

    @pytest.mark.asyncio
    async def test_reads_at_parent_commit(self, analysis):
        repo = _mock_repo()
        repo.get_git_commit.return_value.sha = "parent-sha"
        await _sync(repo, [analysis])

        assert {c.kwargs["ref"] for c in repo.get_contents.call_args_list} == {"parent-sha"}

    @pytest.mark.asyncio
    async def test_non_404_error_aborts_instead_of_rebuilding_index(self, analysis):
        from github import GithubException

        repo = _mock_repo()
        repo.get_contents.side_effect = GithubException(502, "Bad gateway", None)
        with pytest.raises(GithubException):
            await _sync(repo, [analysis])
        repo.create_git_commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_same_output_dirs_rejected(self, analysis, digest):
        from mcp_content_pipeline.services.github_client import sync_to_github as _sync_gh

        with pytest.raises(ValueError, match="must differ"):
            await _sync_gh(
                token="t", repo_name="o/r", branch="main", output_dir="content",
                analyses=[analysis], x_digests=[digest], x_output_dir="content",
            )

