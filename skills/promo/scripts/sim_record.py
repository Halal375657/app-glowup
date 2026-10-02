#!/usr/bin/env python3
"""Record clean, marketing-ready footage from the iOS Simulator.

Usage:
  sim_record.py clean <udid>               Set a tidy status bar (9:41, full battery, full signal). Undo: `reset`.
  sim_record.py reset <udid>               Restore the real status bar.
  sim_record.py start <udid> <out.mov>     Start recording in the background (HEVC, with the status bar cleaned).
  sim_record.py stop  <out.mov>            Stop that recording and wait until the file is finalized.
  sim_record.py trim  <in.mov> <out.mp4> <start_s> <end_s> [--fps 30]
                                           Cut a clip and re-encode it as constant-frame-rate H.264 (editor-safe).

simctl writes variable-frame-rate video that only contains frames when the screen changes; `trim`
converts it to constant frame rate so editors and Hyperframes seek it reliably.
"""
import os, signal, subprocess, sys, time


def sh(*args, **kw):
    return subprocess.run(args, check=True, **kw)


def pidfile(out):
    return os.path.abspath(out) + ".pid"


def clean(udid):
    sh("xcrun", "simctl", "status_bar", udid, "override", "--time", "9:41", "--dataNetwork", "wifi",
       "--wifiMode", "active", "--wifiBars", "3", "--cellularMode", "active", "--cellularBars", "4",
       "--operatorName", "", "--batteryState", "charged", "--batteryLevel", "100")


def start(udid, out):
    out = os.path.abspath(out)  # simctl resolves relative paths against its own working directory
    os.makedirs(os.path.dirname(out), exist_ok=True)
    clean(udid)
    log = open(out + ".log", "w")
    p = subprocess.Popen(["xcrun", "simctl", "io", udid, "recordVideo", "--codec=hevc", "--force", out],
                         stdout=log, stderr=log, start_new_session=True)
    open(pidfile(out), "w").write(str(p.pid))
    time.sleep(1.5)  # recording takes a moment to begin
    if p.poll() is not None:
        sys.exit(f"recording failed to start; see {out}.log")
    print(f"recording to {out} (pid {p.pid}); run `sim_record.py stop {out}` when done")


def stop(out):
    out = os.path.abspath(out)
    pid = int(open(pidfile(out)).read())
    os.kill(pid, signal.SIGINT)  # SIGINT lets simctl finalize the file; SIGKILL would corrupt it
    for _ in range(60):
        try:
            os.kill(pid, 0)
            time.sleep(0.5)
        except ProcessLookupError:
            break
    os.remove(pidfile(out))
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                         capture_output=True, text=True).stdout.strip()
    print(f"saved {out} ({dur or '?'} s)")


def trim(src, dst, a, b, fps="30"):
    sh("ffmpeg", "-y", "-v", "error", "-ss", a, "-to", b, "-i", src, "-vf", f"fps={fps},format=yuv420p",
       "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-movflags", "+faststart", "-an", dst)
    print(f"saved {dst}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if a[0] == "clean":
        clean(a[1]); print("status bar cleaned")
    elif a[0] == "reset":
        sh("xcrun", "simctl", "status_bar", a[1], "clear"); print("status bar restored")
    elif a[0] == "start":
        start(a[1], a[2])
    elif a[0] == "stop":
        stop(a[1])
    elif a[0] == "trim":
        fps = a[a.index("--fps") + 1] if "--fps" in a else "30"
        trim(a[1], a[2], a[3], a[4], fps)
    else:
        sys.exit(__doc__)
