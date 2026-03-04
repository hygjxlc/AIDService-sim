"""Unit tests for file service"""
import pytest
import tempfile
import os
from pathlib import Path
from src.services.file_service import (
    validate_file,
    get_missing_files,
    REQUIRED_FILES,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE
)


class TestFileValidation:
    """Tests for file validation"""
    
    def test_valid_required_file(self):
        """Test validation of valid required file"""
        is_valid, error = validate_file("config.yml", 1000)
        assert is_valid is True
        assert error == ""
    
    def test_valid_optional_file(self):
        """Test validation of valid optional file"""
        is_valid, error = validate_file("product.stp", 1000)
        assert is_valid is True
    
    def test_invalid_extension(self):
        """Test validation with invalid extension"""
        is_valid, error = validate_file("test.exe", 1000)
        assert is_valid is False
        assert "不支持的文件格式" in error
    
    def test_file_not_in_list(self):
        """Test validation with file not in allowed list"""
        is_valid, error = validate_file("random.csv", 1000)
        assert is_valid is False
        assert "不在允许的文件列表中" in error
    
    def test_file_too_large(self):
        """Test validation with file too large"""
        is_valid, error = validate_file("config.yml", MAX_FILE_SIZE + 1)
        assert is_valid is False
        assert "文件大小超过限制" in error
    
    def test_support_side_mould_pattern(self):
        """Test support_side_mould_*.stp pattern"""
        is_valid, error = validate_file("support_side_mould_1.stp", 1000)
        assert is_valid is True


class TestMissingFiles:
    """Tests for missing files detection"""
    
    def test_all_files_present(self):
        """Test when all required files are uploaded"""
        missing = get_missing_files(REQUIRED_FILES)
        assert len(missing) == 0
    
    def test_no_files_uploaded(self):
        """Test when no files are uploaded"""
        missing = get_missing_files([])
        assert len(missing) == len(REQUIRED_FILES)
    
    def test_some_files_missing(self):
        """Test when some files are missing"""
        uploaded = ["config.yml", "materials.csv"]
        missing = get_missing_files(uploaded)
        assert len(missing) == len(REQUIRED_FILES) - 2
        assert "config.yml" not in missing
        assert "materials.csv" not in missing
    
    def test_case_insensitive(self):
        """Test case-insensitive file matching"""
        uploaded = ["CONFIG.YML", "MATERIALS.CSV"]
        missing = get_missing_files(uploaded)
        assert "config.yml" not in missing
        assert "materials.csv" not in missing
