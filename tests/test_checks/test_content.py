"""Tests for content checks (checks 11–14). Implemented in Phase 3."""
import pytest


# generic_headings
@pytest.mark.skip(reason="check not implemented yet")
async def test_generic_headings_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_generic_headings_fail_h1_welcome(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_generic_headings_warn_h2_home(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_generic_headings_fail_three_generic(): ...


# faq_pattern
@pytest.mark.skip(reason="check not implemented yet")
async def test_faq_pass_dl_element(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_faq_pass_details_summary(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_faq_pass_schema_faqpage(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_faq_warn_absent(): ...


# eeat_signals
@pytest.mark.skip(reason="check not implemented yet")
async def test_eeat_pass_author_and_date(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_eeat_fail_neither(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_eeat_warn_date_only(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_eeat_warn_author_only(): ...


# structured_content
@pytest.mark.skip(reason="check not implemented yet")
async def test_structured_content_pass_ul(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_structured_content_pass_table(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_structured_content_fail_none(): ...
