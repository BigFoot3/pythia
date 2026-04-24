"""Tests for structure checks (checks 1–4). Implemented in Phase 3."""
import pytest


@pytest.mark.skip(reason="check not implemented yet")
async def test_llms_txt_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_llms_txt_fail_missing(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_llms_txt_fail_empty(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_llms_full_txt_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_llms_full_txt_warn_missing(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_robots_ai_bots_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_robots_ai_bots_fail_gptbot_blocked(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_robots_ai_bots_fail_claudebot_blocked(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_robots_ai_bots_warn_no_robots_txt(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_sitemap_accessible_pass_direct(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_sitemap_accessible_pass_via_robots(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_sitemap_accessible_fail(): ...
