from pathlib import Path

import chess
import chess.engine
import pytest

from infrastructure.stockfish_client import (
    StockfishClient,
    StockfishNotFoundError,
    StockfishUnavailableError,
)


def write_fake_engine(path: Path, *, ready: bool = True) -> Path:
    path.write_text(
        """#!/bin/sh
while IFS= read -r command; do
  case "$command" in
    uci)
      echo "id name fake-stockfish"
      echo "uciok"
      ;;
    isready)
      %s
      ;;
    quit)
      exit 0
      ;;
    go*)
      echo "info depth 1 score cp 20 pv e2e4"
      echo "bestmove e2e4"
      ;;
  esac
done
"""
        % ('echo "readyok"' if ready else "echo 'not-ready'"),
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def test_client_discovers_and_probes_engine(tmp_path: Path) -> None:
    executable = write_fake_engine(tmp_path / "stockfish")
    client = StockfishClient(executable=executable)

    status = client.check()

    assert status.available is True
    assert status.executable == executable.resolve()


def test_client_reports_missing_engine(tmp_path: Path) -> None:
    client = StockfishClient(project_root=tmp_path)

    status = client.check()

    assert status.available is False
    assert status.executable is None
    with pytest.raises(StockfishNotFoundError, match="not found"):
        client.ensure_available()


def test_client_reports_engine_that_does_not_answer_uci(tmp_path: Path) -> None:
    executable = write_fake_engine(tmp_path / "stockfish", ready=False)
    client = StockfishClient(executable=executable, startup_timeout=0.1)

    status = client.check()

    assert status.available is False
    assert status.executable == executable.resolve()
    with pytest.raises(StockfishUnavailableError):
        client.start()


def test_client_analyse_starts_engine_lazily(tmp_path: Path) -> None:
    executable = write_fake_engine(tmp_path / "stockfish")
    client = StockfishClient(executable=executable)

    try:
        result = client.analyse(chess.Board(), chess.engine.Limit(depth=1))

        assert result["pv"][0] == chess.Move.from_uci("e2e4")
    finally:
        client.close()
