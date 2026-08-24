import os
import sys
from pathlib import Path

import click
from tuyalight.config import AppConfig
from tuyalight.engine import LightshowEngine


@click.group()
def main() -> None:
    """TuyaLight CLI."""
    pass


@main.command()
@click.option("-c", "--config", default="config.toml", help="Path to config.toml")
@click.option("--background", is_flag=True, help="Run without console output")
def run(config: str, background: bool) -> None:
    """Start the lightshow."""
    cfg = AppConfig.load(config)
    engine = LightshowEngine(cfg)
    engine.run(background=background)


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
        # Resolve pythonw.exe (windowless python) and absolute project path
        pythonw = Path(sys.executable).parent / "pythonw.exe"
        project_dir = Path.cwd()
        config_path = project_dir / "config.toml"

        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{project_dir}"
WshShell.Run """{pythonw}"" -m tuyalight run --background -c ""{config_path}""", 0, False
'''
        vbs_path.write_text(vbs_content, encoding="utf-8")
        click.echo(f"Added to Windows Startup: {vbs_path}")
