"""Acesso ao ffmpeg (usa o do sistema ou o binário do imageio-ffmpeg)."""
import shutil
import subprocess


def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def run(args: list[str]) -> str:
    """Roda o ffmpeg e devolve o stderr (onde ele escreve logs e metadados)."""
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-y", *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg falhou:\n{proc.stderr[-2000:]}")
    return proc.stderr
