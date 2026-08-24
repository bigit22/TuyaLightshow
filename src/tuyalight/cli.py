import os
import sys
from pathlib import Path

import click

from tuyalight.config import AppConfig
from tuyalight.engine import LightshowEngine


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """TuyaLight CLI."""
    if ctx.invoked_subcommand is None:
        from tuyalight.gui import run_gui

        run_gui()


@main.command()
@click.option("-c", "--config", default="config.toml", help="Path to config.toml")
@click.option("--background", is_flag=True, help="Run without console output")
def run(config: str, background: bool) -> None:
    """Start the lightshow."""
    cfg = AppConfig.load(config)
    engine = LightshowEngine(cfg)
    engine.run(background=background)


@main.command()
@click.option("-c", "--config", default="config.toml", help="Path to config.toml")
def gui(config: str) -> None:
    """Launch Liquid Glass GUI."""
    from tuyalight.gui import run_gui

    run_gui(config_path=config)


@main.command()
@click.option("--enable", is_flag=True, help="Add to Windows Startup")
@click.option("--disable", is_flag=True, help="Remove from Windows Startup")
def startup(enable: bool, disable: bool) -> None:
    """Manage Windows Startup (runs in background without console)."""
    if sys.platform != "win32":
        click.echo("Startup feature is only available on Windows.")
        return

    startup_dir = (
        Path(os.getenv("APPDATA", ""))
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )
    vbs_path = startup_dir / "tuyalight_bg.vbs"

    if disable:
        if vbs_path.exists():
            vbs_path.unlink()
            click.echo("Removed from Windows Startup.")
        else:
            click.echo("Not found in Startup.")
        return

    if enable:
        is_frozen = getattr(sys, "frozen", False)
        exe_path = Path(sys.executable).resolve()
        project_dir = Path.cwd().resolve()
        config_path = project_dir / "config.toml"

        if is_frozen:
            # Запуск из собранного .exe
            vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{project_dir}"
WshShell.Run """{exe_path}"" run --background -c ""{config_path}""", 0, False
'''
        else:
            # Запуск из исходников Python
            pythonw = exe_path.parent / "pythonw.exe"
            if not pythonw.exists():
                pythonw = exe_path

            vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{project_dir}"
WshShell.Run """{pythonw}"" -m tuyalight run --background -c ""{config_path}""", 0, False
'''

        vbs_path.write_text(vbs_content, encoding="utf-8")
        click.echo(f"Added to Windows Startup: {vbs_path}")
