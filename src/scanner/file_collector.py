"""File collection module for gathering source code files."""
import os
from pathlib import Path
from typing import List, Tuple
from src.utils.config import ScanConfig


class FileCollector:
    """Collects and filters source code files for scanning."""

    def __init__(self, config: ScanConfig):
        """Initialize the file collector.

        Args:
            config: Scan configuration
        """
        self.config = config
        self.input_path = Path(config.input_path).resolve()

    def collect_files(self) -> List[Tuple[Path, int]]:
        """Collect all eligible source files.

        Returns:
            List of tuples (file_path, file_size)
        """
        files = []

        if not self.input_path.exists():
            raise ValueError(f"Input path does not exist: {self.input_path}")

        if self.input_path.is_file():
            # Single file mode
            if self._is_eligible_file(self.input_path):
                size = self.input_path.stat().st_size
                files.append((self.input_path, size))
        else:
            # Directory mode
            for root, dirs, filenames in os.walk(self.input_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded(d)]

                for filename in filenames:
                    file_path = Path(root) / filename

                    if self._is_eligible_file(file_path):
                        try:
                            size = file_path.stat().st_size
                            if size <= self.config.max_file_size:
                                files.append((file_path, size))
                            else:
                                print(f"Skipping large file: {file_path} ({size} bytes)")
                        except OSError as e:
                            print(f"Warning: Cannot access {file_path}: {e}")

        return files

    def _is_eligible_file(self, file_path: Path) -> bool:
        """Check if a file should be included in the scan.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be included
        """
        # Check if file is excluded
        if self._is_excluded(file_path.name):
            return False

        # Check extension
        if file_path.suffix.lower() not in self.config.supported_extensions:
            return False

        # Check if it's a regular file
        if not file_path.is_file():
            return False

        return True

    def _is_excluded(self, name: str) -> bool:
        """Check if a file or directory name matches exclusion patterns.

        Args:
            name: File or directory name

        Returns:
            True if should be excluded
        """
        for pattern in self.config.exclude_patterns:
            # Simple wildcard matching
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                if name.startswith(pattern[:-1]):
                    return True
            elif pattern in name or name == pattern:
                return True

        return False

    def read_file_chunked(self, file_path: Path) -> List[Tuple[str, int]]:
        """Read a file in chunks with line tracking.

        Args:
            file_path: Path to the file

        Returns:
            List of tuples (chunk_content, starting_line_number)
        """
        chunks = []
        current_chunk = []
        current_size = 0
        line_number = 1
        chunk_start_line = 1

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_size = len(line.encode('utf-8'))

                    # Start new chunk if size limit reached
                    if current_size + line_size > self.config.chunk_size and current_chunk:
                        chunks.append((''.join(current_chunk), chunk_start_line))
                        current_chunk = []
                        current_size = 0
                        chunk_start_line = line_number

                    current_chunk.append(line)
                    current_size += line_size
                    line_number += 1

                # Add remaining content
                if current_chunk:
                    chunks.append((''.join(current_chunk), chunk_start_line))

        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}")
            return []

        return chunks

    def create_batches(self, files: List[Tuple[Path, int]]) -> List[List[Path]]:
        """Group files into batches based on size.

        Args:
            files: List of (file_path, file_size) tuples

        Returns:
            List of file path batches
        """
        batches = []
        current_batch = []
        current_size = 0

        # Sort files by size (smallest first) for better packing
        sorted_files = sorted(files, key=lambda x: x[1])

        for file_path, file_size in sorted_files:
            if current_size + file_size > self.config.batch_size and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_size = 0

            current_batch.append(file_path)
            current_size += file_size

        # Add remaining files
        if current_batch:
            batches.append(current_batch)

        return batches
