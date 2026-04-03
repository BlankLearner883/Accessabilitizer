"""Simple terminal progress bar (block-based)."""


class ProgressBar:
    """Displays a progress bar of filled/empty blocks. Call update(0..1), then end() or finish()."""

    def __init__(self, total_segment_count: int) -> None:
        self.total_segment_count = total_segment_count

    def update(self, current_completion: float) -> None:
        """Update bar; current_completion should be in [0, 1]."""
        filled = round(current_completion * self.total_segment_count)
        bar = "█" * filled + "_" * (self.total_segment_count - filled)
        print(bar, end="\r")

    def end(self) -> None:
        """Finish the bar (newline)."""
        print()

    def finish(self) -> None:
        """Alias for end(); use for consistency with callers that expect finish()."""
        self.end()