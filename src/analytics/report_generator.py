"""Compatibility exports; report generation lives in :mod:`src.reporting`."""
from src.reporting.report_generator import (
    CSV_COLUMNS,
    factual_interpretation,
    export_metrics_csv,
    generate_comparison_pdf,
    generate_run_pdf,
    guard_interpretation,
)

__all__ = ["CSV_COLUMNS", "factual_interpretation", "export_metrics_csv",
           "generate_comparison_pdf", "generate_run_pdf", "guard_interpretation"]
