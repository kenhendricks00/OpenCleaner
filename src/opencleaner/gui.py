from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .core import ScanItem, clean_items, human_readable_size, run_scan


class OpenCleanerApp(tk.Tk):
    """OpenCleaner desktop application.

    Aesthetic direction: retro-futuristic command center with high-contrast accents,
    elevated typography, and clear information hierarchy.
    """

    BG = "#0a0f1f"
    SURFACE = "#121a33"
    SURFACE_ELEVATED = "#192447"
    PANEL_BORDER = "#32406d"
    ACCENT = "#3af2cf"
    ACCENT_SOFT = "#1bc6a8"
    TEXT_MAIN = "#e7efff"
    TEXT_MUTED = "#9fb2d9"
    WARNING = "#ffd166"

    def __init__(self) -> None:
        super().__init__()
        self.title("OpenCleaner")
        self.geometry("1080x680")
        self.minsize(980, 620)
        self.configure(bg=self.BG)

        self.report_items: list[ScanItem] = []
        self.selection_vars: dict[str, tk.BooleanVar] = {}
        self.row_to_item: dict[str, ScanItem] = {}
        self._scan_in_progress = False

        self.total_var = tk.StringVar(value="Potential reclaimable space: --")
        self.status_var = tk.StringVar(value="System standing by. Run scan to detect reclaimable files.")

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Root.TFrame", background=self.BG)
        style.configure("Surface.TFrame", background=self.SURFACE)
        style.configure("Elevated.TFrame", background=self.SURFACE_ELEVATED)

        style.configure(
            "Headline.TLabel",
            background=self.BG,
            foreground=self.TEXT_MAIN,
            font=("Bahnschrift", 28, "bold"),
        )
        style.configure(
            "Subhead.TLabel",
            background=self.BG,
            foreground=self.TEXT_MUTED,
            font=("Cascadia Code", 11),
        )
        style.configure(
            "Stat.TLabel",
            background=self.SURFACE_ELEVATED,
            foreground=self.ACCENT,
            font=("Bahnschrift", 14, "bold"),
        )
        style.configure(
            "StatCaption.TLabel",
            background=self.SURFACE_ELEVATED,
            foreground=self.TEXT_MUTED,
            font=("Cascadia Code", 9),
        )
        style.configure(
            "Footer.TLabel",
            background=self.BG,
            foreground=self.TEXT_MUTED,
            font=("Cascadia Code", 10),
        )

        style.configure(
            "Neon.TButton",
            font=("Bahnschrift", 11, "bold"),
            padding=(16, 10),
            foreground=self.BG,
            background=self.ACCENT,
            borderwidth=0,
        )
        style.map(
            "Neon.TButton",
            background=[("disabled", "#3b4d58"), ("active", "#66ffe1")],
            foreground=[("disabled", "#a7c3bc"), ("active", self.BG)],
        )

        style.configure(
            "Ghost.TButton",
            font=("Bahnschrift", 11),
            padding=(14, 10),
            foreground=self.TEXT_MAIN,
            background=self.SURFACE,
            bordercolor=self.PANEL_BORDER,
            borderwidth=1,
        )
        style.map(
            "Ghost.TButton",
            background=[("disabled", "#131a2d"), ("active", "#243258")],
            foreground=[("disabled", "#5d6d95"), ("active", self.TEXT_MAIN)],
        )

        style.configure(
            "Futuristic.Horizontal.TProgressbar",
            troughcolor=self.SURFACE,
            background=self.ACCENT,
            bordercolor=self.PANEL_BORDER,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT_SOFT,
            thickness=10,
        )

        style.configure(
            "Cleaner.Treeview",
            background=self.SURFACE,
            fieldbackground=self.SURFACE,
            foreground=self.TEXT_MAIN,
            bordercolor=self.PANEL_BORDER,
            rowheight=34,
            font=("Cascadia Code", 10),
        )
        style.configure(
            "Cleaner.Treeview.Heading",
            background=self.SURFACE_ELEVATED,
            foreground=self.TEXT_MAIN,
            font=("Bahnschrift", 11, "bold"),
            relief="flat",
        )
        style.map("Cleaner.Treeview", background=[("selected", "#2e3d6d")])
        style.map("Cleaner.Treeview.Heading", background=[("active", "#27396c")])

    def _build_ui(self) -> None:
        shell = ttk.Frame(self, style="Root.TFrame", padding=20)
        shell.pack(fill="both", expand=True)

        self._build_header(shell)
        self._build_controls(shell)
        self._build_table(shell)

        ttk.Label(shell, textvariable=self.status_var, style="Footer.TLabel", padding=(6, 12, 6, 2)).pack(fill="x")

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="Root.TFrame")
        header.pack(fill="x")

        left = ttk.Frame(header, style="Root.TFrame")
        left.pack(side="left", fill="x", expand=True)

        ttk.Label(left, text="OPENCLEANER", style="Headline.TLabel").pack(anchor="w")
        ttk.Label(
            left,
            text="Retro-futuristic workstation for cache and storage hygiene",
            style="Subhead.TLabel",
            padding=(2, 2, 2, 10),
        ).pack(anchor="w")

        stat_card = ttk.Frame(header, style="Elevated.TFrame", padding=(16, 12))
        stat_card.pack(side="right")
        ttk.Label(stat_card, text="SPACE INTELLIGENCE", style="StatCaption.TLabel").pack(anchor="e")
        ttk.Label(stat_card, textvariable=self.total_var, style="Stat.TLabel").pack(anchor="e", pady=(2, 0))

    def _build_controls(self, parent: ttk.Frame) -> None:
        wrap = ttk.Frame(parent, style="Surface.TFrame", padding=14)
        wrap.pack(fill="x", pady=(6, 10))

        self.scan_button = ttk.Button(wrap, text="Run Deep Scan", style="Neon.TButton", command=self.run_scan)
        self.scan_button.pack(side="left")

        self.clean_button = ttk.Button(
            wrap,
            text="Clean Selected",
            style="Ghost.TButton",
            command=self.clean_selected,
            state="disabled",
        )
        self.clean_button.pack(side="left", padx=(10, 0))

        self.select_all_button = ttk.Button(
            wrap,
            text="Select All",
            style="Ghost.TButton",
            command=self.select_all,
            state="disabled",
        )
        self.select_all_button.pack(side="left", padx=(10, 0))

        self.clear_selection_button = ttk.Button(
            wrap,
            text="Clear",
            style="Ghost.TButton",
            command=self.clear_selection,
            state="disabled",
        )
        self.clear_selection_button.pack(side="left", padx=(10, 0))

        self.progress = ttk.Progressbar(wrap, style="Futuristic.Horizontal.TProgressbar", mode="indeterminate")
        self.progress.pack(side="right", fill="x", expand=True, padx=(20, 4), ipady=1)

    def _build_table(self, parent: ttk.Frame) -> None:
        table_panel = tk.Frame(
            parent,
            bg=self.SURFACE,
            highlightbackground=self.PANEL_BORDER,
            highlightthickness=1,
            bd=0,
        )
        table_panel.pack(fill="both", expand=True)

        columns = ("enabled", "category", "targets", "size")
        self.tree = ttk.Treeview(
            table_panel,
            columns=columns,
            show="headings",
            selectmode="none",
            style="Cleaner.Treeview",
        )
        self.tree.heading("enabled", text="ARMED")
        self.tree.heading("category", text="MODULE")
        self.tree.heading("targets", text="TARGET LOCATIONS")
        self.tree.heading("size", text="EST. SIZE")

        self.tree.column("enabled", width=90, anchor="center")
        self.tree.column("category", width=240, anchor="w")
        self.tree.column("targets", width=560, anchor="w")
        self.tree.column("size", width=130, anchor="e")

        scrollbar = ttk.Scrollbar(table_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Button-1>", self._toggle_row_selection)

    def _set_actions_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.clean_button.configure(state=state)
        self.select_all_button.configure(state=state)
        self.clear_selection_button.configure(state=state)

    def _toggle_scan_state(self, scanning: bool) -> None:
        self._scan_in_progress = scanning
        if scanning:
            self.scan_button.configure(state="disabled")
            self.progress.start(9)
            self.status_var.set("Sweeping filesystem signatures... please stand by.")
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
                values=("●", item.label, "  |  ".join(str(p) for p in item.paths), human_readable_size(item.bytes_size)),
            )

        self.total_var.set(f"Potential reclaimable space: {human_readable_size(total_bytes)}")

        has_data = bool(items)
        self._set_actions_state(has_data)
        self._toggle_scan_state(False)
        if has_data:
            self.status_var.set(f"Scan complete: {len(items)} cleanup modules armed.")
        else:
            self.status_var.set("Scan complete: no cleanable categories detected.")

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
        self.tree.set(row_id, "enabled", "●" if variable.get() else "○")

    def select_all(self) -> None:
        for row_id, variable in self.selection_vars.items():
            variable.set(True)
            self.tree.set(row_id, "enabled", "●")
        self.status_var.set("All modules armed for cleanup.")

    def clear_selection(self) -> None:
        for row_id, variable in self.selection_vars.items():
            variable.set(False)
            self.tree.set(row_id, "enabled", "○")
        self.status_var.set("All modules disarmed.")

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
            messagebox.showinfo("OpenCleaner", "Arm at least one module before cleanup.")
            return

        count = len(selected)
        confirm = messagebox.askyesno(
            "Confirm cleanup",
            f"Execute cleanup for {count} armed modules?",
            icon="warning",
        )
        if not confirm:
            return

        deleted, reclaimed = clean_items(selected)
        self.status_var.set(
            f"Cleanup complete: removed {deleted} entries / reclaimed {human_readable_size(reclaimed)}."
        )
        messagebox.showinfo(
            "Cleanup complete",
            f"Removed {deleted} entries and reclaimed approximately {human_readable_size(reclaimed)}.",
        )
        self.run_scan()
