"""
Security and validation tests for crispr-offtarget-scanner.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from crispr_offtarget import lookup, process_csv


class TestLookup:
    """Tests for the core lookup function."""

    def test_lookup_returns_expected_keys(self):
        result = lookup("cas9 guide rna")
        assert "top_hit" in result
        assert "score" in result
        assert "all" in result
        assert "query" in result

    def test_lookup_crispr_terms(self):
        result = lookup("cas9")
        assert result["score"] > 0
        assert "Cas9" in result["top_hit"]

    def test_lookup_pam_site(self):
        result = lookup("pam site")
        assert result["score"] > 0

    def test_lookup_mismatch(self):
        result = lookup("off-target mismatch")
        assert result["score"] > 0

    def test_lookup_cfd_score(self):
        result = lookup("cfd specificity")
        assert result["score"] > 0

    def test_lookup_empty_query(self):
        result = lookup("")
        assert "top_hit" in result
        assert "score" in result

    def test_lookup_case_insensitive(self):
        result_lower = lookup("cas9")
        result_upper = lookup("CAS9")
        assert result_lower["top_hit"] == result_upper["top_hit"]

    def test_lookup_no_match(self):
        result = lookup("xyznonexistent")
        # When no match, score should be 0 and top_hit should be "no match"
        assert result["score"] == 0 or result["top_hit"] == "no match"


class TestProcessCsv:
    """Tests for CSV processing with validation."""

    def test_process_csv_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            process_csv("nonexistent_file.csv", "output.csv")

    def test_process_csv_empty_headers(self, tmp_path):
        input_file = tmp_path / "bad.csv"
        input_file.write_text("")

        with pytest.raises((ValueError, StopIteration)):
            process_csv(str(input_file), str(tmp_path / "out.csv"))

    def test_process_csv_valid_input(self, tmp_path):
        input_file = tmp_path / "input.csv"
        input_file.write_text("query,name\nQ1,cas9\nQ2,pam\n")

        output_file = tmp_path / "output.csv"
        results = process_csv(str(input_file), str(output_file))

        assert len(results) == 2
        assert output_file.exists()
        assert all("top_hit" in r for r in results)
        assert all("lookup_score" in r for r in results)

    test_process_csv_valid_input.sample_csv = None  # marker for test


class TestBatchCli:
    """Tests for CLI batch command error handling."""

    def test_batch_missing_input_file(self, capsys):
        from cli import main
        result = main(["batch", "-i", "nonexistent.csv"])
        assert result == 1

    def test_batch_valid_csv(self, tmp_path, capsys):
        from cli import main
        input_file = tmp_path / "input.csv"
        input_file.write_text("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\nT1,KEY-01,10.0,5.0,NOMINAL,false\n")

        output_file = tmp_path / "output.csv"
        result = main(["batch", "-i", str(input_file), "-o", str(output_file)])

        assert result == 0
        assert output_file.exists()


class TestPhiGuard:
    """Tests for PHI guard functionality."""

    def test_phi_guard_blocks_mrn(self):
        from agents.base import PHIGuard, SecurityException
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_phi_guard_blocks_ssn(self):
        from agents.base import PHIGuard, SecurityException
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phi_guard_blocks_phone(self):
        from agents.base import PHIGuard, SecurityException
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_phi_guard_allows_clean_text(self):
        from agents.base import PHIGuard
        # Should not raise
        PHIGuard.assert_no_phi("Cas9 guide RNA target sequence analysis")

    def test_phi_redaction(self):
        from agents.base import PHIGuard
        redacted = PHIGuard.redact_phi("Patient MRN-12345678 test")
        assert "REDACTED" in redacted
        assert "MRN-12345678" not in redacted
