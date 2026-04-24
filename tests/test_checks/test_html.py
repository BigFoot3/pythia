"""Tests for HTML checks (checks 6–10). Implemented in Phase 3."""
import pytest


# single_h1
@pytest.mark.skip(reason="check not implemented yet")
async def test_single_h1_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_single_h1_fail_missing(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_single_h1_warn_multiple(): ...


# heading_hierarchy
@pytest.mark.skip(reason="check not implemented yet")
async def test_heading_hierarchy_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_heading_hierarchy_fail_h1_to_h3(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_heading_hierarchy_fail_h2_to_h4(): ...


# title_length
@pytest.mark.skip(reason="check not implemented yet")
async def test_title_length_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_title_length_fail_absent(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_title_length_warn_too_short(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_title_length_warn_too_long(): ...


# meta_description
@pytest.mark.skip(reason="check not implemented yet")
async def test_meta_description_pass(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_meta_description_fail_absent(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_meta_description_warn_too_short(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_meta_description_warn_too_long(): ...


# opengraph_minimal
@pytest.mark.skip(reason="check not implemented yet")
async def test_opengraph_pass_all_three(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_opengraph_fail_none(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_opengraph_warn_missing_one(): ...


@pytest.mark.skip(reason="check not implemented yet")
async def test_opengraph_warn_missing_two(): ...
