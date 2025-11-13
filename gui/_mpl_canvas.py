from __future__ import annotations

from typing import Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    """Lightweight Matplotlib canvas for embedding in PySide6 widgets."""

    def __init__(
        self,
        parent: Optional[object] = None,
        *,
        width: float = 5.0,
        height: float = 3.0,
        dpi: int = 100,
    ) -> None:
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure.set_facecolor("white")
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        if parent is not None:
            self.setParent(parent)
        self.figure.tight_layout()
