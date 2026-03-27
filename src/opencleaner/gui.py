from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .core import ScanItem, clean_items, human_readable_size, run_scan


class OpenCleanerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("OpenCleaner")
        self.geometry("900x560")
        self.minsize(860, 520)

        self.report_items: list[ScanItem] = []
        self.selection_vars: dict[str, tk.BooleanVar] = {}
        self.row_to_item: dict[str, ScanItem] = {}
        self._scan_in_progress = False

        self._build_ui()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        header = ttk.Frame(self, padding=(16, 12))
        header.pack(fill="x")

        ttk.Label(header, text="OpenCleaner", font=("Segoe UI", 22, "bold")).pack(side="left")
        ttk.Label(
            header,
            text="Optimize storage and clean unnecessary files safely.",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(10, 0), pady=(8, 0))

        controls = ttk.Frame(self, padding=(16, 2))
        controls.pack(fill="x")

        self.scan_button = ttk.Button(controls, text="Scan", command=self.run_scan)
        self.scan_button.pack(side="left")

        self.clean_button = ttk.Button(controls, text="Clean Selected", command=self.clean_selected, state="disabled")
        self.clean_button.pack(side="left", padx=8)

        self.select_all_button = ttk.Button(controls, text="Select All", command=self.select_all, state="disabled")
        self.select_all_button.pack(side="left")

        self.clear_selection_button = ttk.Button(
            controls,
            text="Clear Selection",
            command=self.clear_selection,
            state="disabled",
        )
        self.clear_selection_button.pack(side="left", padx=8)

        self.total_var = tk.StringVar(value="Potential reclaimable space: --")
        ttk.Label(controls, textvariable=self.total_var, font=("Segoe UI", 10, "bold")).pack(side="right")

        progress_wrap = ttk.Frame(self, padding=(16, 4))
        progress_wrap.pack(fill="x")
        self.progress = ttk.Progressbar(progress_wrap, mode="indeterminate")
        self.progress.pack(fill="x")

        body = ttk.Frame(self, padding=(16, 8))
        body.pack(fill="both", expand=True)

        columns = ("enabled", "category", "targets", "size")
        self.tree = ttk.Treeview(body, columns=columns, show="headings", selectmode="none")
        self.tree.heading("enabled", text="Selected")
        self.tree.heading("category", text="Category")
        self.tree.heading("targets", text="Target Paths")
        self.tree.heading("size", text="Estimated")
        self.tree.column("enabled", width=70, anchor="center")
        self.tree.column("category", width=200, anchor="w")
        self.tree.column("targets", width=500, anchor="w")
        self.tree.column("size", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Button-1>", self._toggle_row_selection)

        self.status_var = tk.StringVar(value="Ready. Click Scan to analyze cleanable files.")
        ttk.Label(self, textvariable=self.status_var, padding=(16, 8), foreground="#555").pack(fill="x")

    def _set_actions_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.clean_button.configure(state=state)
        self.select_all_button.configure(state=state)
        self.clear_selection_button.configure(state=state)

    def _toggle_scan_state(self, scanning: bool) -> None:
        self._scan_in_progress = scanning
        if scanning:
            self.scan_button.configure(state="disabled")
            self.progress.start(8)
            self.status_var.set("Scanning system locations...")
        else:
            self.scan_button.configure(state="normal")
            self.progress.stop()

    def run_scan(self) -> None:
        if self._scan_in_progress:
            return

        self._toggle_scan_state(True)

        def worker() -> None:
            report = run_scan()
            self.after(0, lambda: self._render_scan(report.items, report.total_bytes))

        threading.Thread(target=worker, daemon=True).start()

    def _render_scan(self, items: list[ScanItem], total_bytes: int) -> None:
        self.report_items = items
        self.selection_vars = {}
        self.row_to_item = {}

        self.tree.delete(*self.tree.get_children())

        for idx, item in enumerate(items):
            row_id = str(idx)
            self.selection_vars[row_id] = tk.BooleanVar(value=True)
            self.row_to_item[row_id] = item
            self.tree.insert(
                "",
                "end",
                iid=row_id,
                values=("✓", item.label, ", ".join(str(p) for p in item.paths), human_readable_size(item.bytes_size)),
            )

        self.total_var.set(f"Potential reclaimable space: {human_readable_size(total_bytes)}")

        has_data = bool(items)
        self._set_actions_state(has_data)
        self._toggle_scan_state(False)
        self.status_var.set(f"Scan complete. Found {len(items)} categories.")

    def _toggle_row_selection(self, event: tk.Event) -> None:
        if self._scan_in_progress:
            return

        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or col != "#1":
            return

        variable = self.selection_vars.get(row_id)
        if not variable:
            return

        variable.set(not variable.get())
        self.tree.set(row_id, "enabled", "✓" if variable.get() else "")

    def select_all(self) -> None:
        for row_id, variable in self.selection_vars.items():
            variable.set(True)
            self.tree.set(row_id, "enabled", "✓")
        self.status_var.set("All categories selected.")

    def clear_selection(self) -> None:
        for row_id, variable in self.selection_vars.items():
            variable.set(False)
            self.tree.set(row_id, "enabled", "")
        self.status_var.set("Selection cleared.")

    def _selected_items(self) -> list[ScanItem]:
        selected: list[ScanItem] = []
        for row_id, variable in self.selection_vars.items():
            if variable.get() and row_id in self.row_to_item:
                selected.append(self.row_to_item[row_id])
        return selected

    def clean_selected(self) -> None:
        if self._scan_in_progress:
            return

        selected = self._selected_items()
        if not selected:
            messagebox.showinfo("OpenCleaner", "Select at least one category to clean.")
            return

        count = len(selected)
        confirm = messagebox.askyesno(
            "Confirm cleanup",
            f"OpenCleaner will clean {count} selected categories. Continue?",
        )
        if not confirm:
            return

        deleted, reclaimed = clean_items(selected)
        self.status_var.set(
            f"Cleanup complete. Removed {deleted} entries and reclaimed {human_readable_size(reclaimed)}."
        )
        messagebox.showinfo(
            "Cleanup complete",
            f"Deleted {deleted} entries and reclaimed approximately {human_readable_size(reclaimed)}.",
        )
        self.run_scan()
