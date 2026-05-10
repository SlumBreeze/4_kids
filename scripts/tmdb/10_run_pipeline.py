import argparse
import os
import site
import subprocess
import sys
from dataclasses import dataclass
from typing import List

USER_SITE = site.getusersitepackages()
if USER_SITE and USER_SITE not in sys.path:
    site.addsitedir(USER_SITE)

try:
    from rich.console import Console
    from rich.table import Table
except ModuleNotFoundError:
    Console = None
    Table = None

console = Console() if Console else None


@dataclass
class Stage:
    name: str
    command: List[str]
    external: bool = False


CONTENT_STAGES = [
    Stage("discover", [sys.executable, "scripts/tmdb/1_discover.py"], external=True),
    Stage("enrich", [sys.executable, "scripts/tmdb/2_enrich.py"], external=True),
    Stage("assess-rules", [sys.executable, "scripts/tmdb/3_assess.py"]),
    Stage("auto-review", [sys.executable, "scripts/tmdb/4_review_auto.py"]),
    Stage("import", [sys.executable, "scripts/tmdb/5_import.py", "--yes"]),
    Stage("validate-shows", [sys.executable, "scripts/tmdb/11_validate_shows.py", "--fix"]),
]

AUDIT_STAGES = [
    Stage("refresh-report", [sys.executable, "scripts/tmdb/7_refresh_existing.py"], external=True),
    Stage("variant-audit", [sys.executable, "scripts/tmdb/8_audit_variants.py"]),
    Stage("free-source-report", [sys.executable, "scripts/tmdb/9_enrich_free_sources.py"], external=True),
]

APPLY_REFRESH_STAGE = Stage(
    "refresh-apply",
    [sys.executable, "scripts/tmdb/7_refresh_existing.py", "--apply"],
    external=True,
)


def subprocess_env() -> dict:
    env = os.environ.copy()
    if USER_SITE:
        existing = env.get("PYTHONPATH", "")
        paths = [USER_SITE]
        if existing:
            paths.append(existing)
        env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def selected_stages(args: argparse.Namespace) -> List[Stage]:
    stages = []
    if args.mode in {"content", "all"}:
        stages.extend(CONTENT_STAGES)
    if args.mode in {"audit", "all"}:
        if args.apply_refresh:
            stages.append(APPLY_REFRESH_STAGE)
            stages.extend(stage for stage in AUDIT_STAGES if stage.name != "refresh-report")
        else:
            stages.extend(AUDIT_STAGES)
    return stages


def print_plan(stages: List[Stage], args: argparse.Namespace) -> None:
    if not Table or not console:
        print("Pipeline Plan")
        for index, stage in enumerate(stages, start=1):
            external = "yes" if stage.external else "no"
            command = " ".join(stage.command)
            print(f"{index}. {stage.name} | external APIs: {external} | {command}")
        if args.dry_run:
            print("Dry run only. No stages were executed.")
        return

    table = Table(title="Pipeline Plan")
    table.add_column("Order", style="cyan")
    table.add_column("Stage", style="green")
    table.add_column("Runs external APIs", style="yellow")
    table.add_column("Command", style="magenta")
    for index, stage in enumerate(stages, start=1):
        command = " ".join(stage.command)
        table.add_row(str(index), stage.name, "yes" if stage.external else "no", command)

    console.print(table)
    if args.dry_run:
        console.print("[yellow]Dry run only. No stages were executed.[/]")


def run_stage(stage: Stage) -> int:
    if console:
        console.rule(f"[bold blue]{stage.name}[/]")
    else:
        print(f"\n== {stage.name} ==")
    result = subprocess.run(stage.command, check=False, env=subprocess_env())
    if result.returncode != 0:
        message = f"Stage failed: {stage.name} ({result.returncode})"
        console.print(f"[red]{message}[/]") if console else print(message)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run KidShow Scout content acquisition and audit stages."
    )
    parser.add_argument(
        "--mode",
        choices=["content", "audit", "all"],
        default="all",
        help="Which stage group to run.",
    )
    parser.add_argument(
        "--apply-refresh",
        action="store_true",
        help="Apply existing-record TMDB refresh changes during audit runs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned stages without executing them.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue running later stages after a failure.",
    )
    args = parser.parse_args()

    stages = selected_stages(args)
    print_plan(stages, args)

    if args.dry_run:
        return

    failed = []
    for stage in stages:
        code = run_stage(stage)
        if code != 0:
            failed.append(stage.name)
            if not args.continue_on_error:
                break

    if failed:
        message = f"Pipeline completed with failures: {', '.join(failed)}"
        console.print(f"[red]{message}[/]") if console else print(message)
        raise SystemExit(1)

    if console:
        console.print("[bold green]Pipeline completed successfully.[/]")
    else:
        print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
