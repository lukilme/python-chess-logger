"""Bridge between the application and the Stockfish UCI executable."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from typing import Any

import chess
import chess.engine


class StockfishError(RuntimeError):
    """Base exception for Stockfish client failures."""


class StockfishNotFoundError(StockfishError):
    """Raised when no Stockfish executable can be found."""


class StockfishUnavailableError(StockfishError):
    """Raised when a discovered executable does not answer UCI commands."""


@dataclass(frozen=True)
class StockfishStatus:
    """Result of checking whether Stockfish can be used."""

    available: bool
    executable: Path | None
    reason: str


class StockfishClient:
    """Manage the lifecycle of Stockfish and expose a small Python API.

    The client performs a real UCI handshake before reporting the engine as
    available. Discovery is deterministic and does not download files or
    mutate the repository implicitly.
    """

    # all the important bits of the Stockfish executable name, in order, with optional separators, i guess
    EXECUTABLE_PATTERN = re.compile(
        r"^stockfish"
        r"(?:[-_](?:linux|ubuntu|windows|macos|darwin))?"
        r"(?:[-_](?:x86-64|x86_64|arm64|aarch64|universal))?"
        r"(?:[-_](?:avx2|bmi2|modern|generic))?"
        r"(?:\.exe)?$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        executable: str | Path | None = None,
        project_root: str | Path | None = None,
        *,
        startup_timeout: float = 5.0,
    ) -> None:
        if startup_timeout <= 0:
            raise ValueError("startup_timeout must be greater than zero")

        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])
        self._configured_executable = (
            Path(executable).expanduser() if executable is not None else None
        )
        self.startup_timeout = startup_timeout
        self._engine: chess.engine.SimpleEngine | None = None
        self._executable: Path | None = None

    @property
    def executable(self) -> Path | None:
        """Return the executable selected by the last successful discovery."""

        return self._executable

    @property
    def is_running(self) -> bool:
        return self._engine is not None

    def candidate_paths(self) -> tuple[Path, ...]:
        """Return repository candidates in discovery order."""

        candidates: list[Path] = []
        if self._configured_executable is not None:
            candidates.append(self._configured_executable)

        engine_root = self.project_root / "data" / "engine"
        for directory in (engine_root, engine_root / "stockfish"):
            if directory.is_dir():
                candidates.extend(
                    path
                    for path in directory.iterdir()
                    if path.is_file() and self._matches_executable_name(path.name)
                )

        # Covers official archives extracted below data/engine.
        candidates.extend(
            path
            for path in engine_root.rglob("*")
            if path.is_file() and self._matches_executable_name(path.name)
        )
        return tuple(dict.fromkeys(candidates))

    def discover_executable(self) -> Path | None:
        """Find a usable-looking executable without starting it."""

        for candidate in self.candidate_paths():
            if candidate.is_file() and self._is_executable(candidate):
                return candidate.resolve()

        path_environment = shutil.which("stockfish")
        if path_environment:
            return Path(path_environment).resolve()
        return None

    def check(self) -> StockfishStatus:
        """Discover and probe Stockfish, returning an actionable diagnosis."""

        executable = self.discover_executable()
        if executable is None:
            archive = next(
                (path for path in (self.project_root / "data" / "engine").glob("*.tar.gz")),
                None,
            )
            if archive is not None:
                reason = (
                    f"Stockfish archive found at {archive}, but no executable was "
                    "found. Extract it and make the binary executable."
                )
            else:
                reason = (
                    "Stockfish executable not found. Install it or pass executable=... "
                    "to StockfishClient."
                )
            return StockfishStatus(
                False,
                None,
                reason,
            )

        try:
            probe = chess.engine.SimpleEngine.popen_uci(
                str(executable), timeout=self.startup_timeout
            )
            try:
                probe.ping()
            finally:
                probe.quit()
        except (
            OSError,
            chess.engine.EngineError,
            TimeoutError,
            asyncio.TimeoutError,
        ) as exc:
            return StockfishStatus(
                False,
                executable,
                f"Stockfish was found at {executable}, but UCI probe failed: {exc}",
            )

        return StockfishStatus(True, executable, "Stockfish is available and answered UCI.")

    def ensure_available(self) -> Path:
        """Return a validated executable or raise a specific error."""

        status = self.check()
        if not status.available:
            if status.executable is None:
                raise StockfishNotFoundError(status.reason)
            raise StockfishUnavailableError(status.reason)
        self._executable = status.executable
        return status.executable

    def start(self) -> StockfishClient:
        """Start Stockfish after validating its executable."""

        if self._engine is not None:
            return self

        executable = self.ensure_available()
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(
                str(executable), timeout=self.startup_timeout
            )
        except (
            OSError,
            chess.engine.EngineError,
            TimeoutError,
            asyncio.TimeoutError,
        ) as exc:
            raise StockfishUnavailableError(
                f"Could not start Stockfish at {executable}: {exc}"
            ) from exc
        return self

    def analyse(
        self,
        board: chess.Board,
        limit: chess.engine.Limit,
        *,
        multipv: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Analyse a position, starting the engine lazily if necessary."""

        engine = self.start()._require_engine()
        if multipv is None:
            return engine.analyse(board, limit)
        return engine.analyse(board, limit, multipv=multipv)

    def configure(self, options: dict[str, Any]) -> None:
        """Apply UCI options to a running engine."""

        self.start()._require_engine().configure(options)

    def close(self) -> None:
        """Stop the child process and release its resources."""

        if self._engine is not None:
            self._engine.quit()
            self._engine = None

    def __enter__(self) -> StockfishClient:
        return self.start()

    def __exit__(self, *_: object) -> None:
        self.close()

    def _require_engine(self) -> chess.engine.SimpleEngine:
        if self._engine is None:
            raise StockfishUnavailableError("Stockfish is not running.")
        return self._engine

    @staticmethod
    def _is_executable(path: Path) -> bool:
        return path.stat().st_mode & 0o111 != 0

    @classmethod
    def _matches_executable_name(cls, filename: str) -> bool:
        return cls.EXECUTABLE_PATTERN.fullmatch(filename) is not None