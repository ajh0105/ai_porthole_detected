"""
VS Code 터미널용 실시간 학습 모니터.
실행: python ai/monitor.py
"""

import csv
import os
import sys
import time
from pathlib import Path

RESULTS_CSV  = Path(__file__).parent / "models" / "runs" / "pothole-crack" / "results.csv"
TRAIN_LOG    = Path(__file__).parent / "train_log.txt"
POLL_SEC     = 5

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRAY   = "\033[90m"


def bar(ratio: float, width: int = 30) -> str:
    filled = int(ratio * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {ratio*100:5.1f}%"


def read_csv():
    if not RESULTS_CSV.exists():
        return []
    with open(RESULTS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_current_epoch():
    """train_log.txt 마지막 줄에서 현재 epoch 내 batch 진행률 파싱."""
    if not TRAIN_LOG.exists():
        return None
    try:
        with open(TRAIN_LOG, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 4096))
            tail = f.read().decode("utf-8", errors="ignore")
        for line in reversed(tail.splitlines()):
            line = line.strip().lstrip("\x1b[K")
            if "/" in line and "it/s" in line:
                parts = line.split()
                for p in parts:
                    if "/" in p and p.replace("/","").isdigit():
                        cur, total = p.split("/")
                        return int(cur), int(total)
    except Exception:
        pass
    return None


def clear():
    os.system("cls" if sys.platform == "win32" else "clear")


def render(rows):
    clear()
    n = len(rows)

    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{CYAN}  YOLOv11s  RDD2022  학습 모니터{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")

    if not rows:
        print(f"\n  {YELLOW}대기 중 — 첫 epoch 완료를 기다립니다...{RESET}\n")
        _show_batch_progress()
        return

    latest  = rows[-1]
    epoch   = int(latest.get("epoch", 0))
    map50   = float(latest.get("metrics/mAP50(B)", 0))
    map5095 = float(latest.get("metrics/mAP50-95(B)", 0))
    box_l   = float(latest.get("val/box_loss", 0))
    cls_l   = float(latest.get("val/cls_loss", 0))
    dfl_l   = float(latest.get("val/dfl_loss", 0))
    t_s     = float(latest.get("time", 0))

    # 에폭 소요시간
    if n >= 2:
        ep_time = t_s - float(rows[-2].get("time", 0))
        avg_time = (t_s - float(rows[0].get("time", 0))) / max(epoch - 1, 1)
    else:
        ep_time = t_s
        avg_time = t_s

    remaining_min = avg_time * (100 - epoch) / 60

    # 색상 결정 (mAP50 기준)
    if map50 >= 0.5:
        mc = GREEN
    elif map50 >= 0.3:
        mc = YELLOW
    else:
        mc = RED

    print(f"\n  {BOLD}진행률{RESET}  {bar(epoch/100)}")
    print(f"  {BOLD}Epoch  {RESET}  {epoch:3d} / 100")
    print(f"  {BOLD}경과   {RESET}  {t_s/3600:.1f}시간  |  예상 잔여 {remaining_min:.0f}분")
    print(f"  {BOLD}Epoch당{RESET}  {ep_time/60:.1f}분\n")

    print(f"  {BOLD}{'─'*40}{RESET}")
    print(f"  {BOLD}{'지표':<18}{'현재':>10}{'최고':>10}{RESET}")
    print(f"  {'─'*40}")

    map50_vals = [float(r.get("metrics/mAP50(B)", 0)) for r in rows]
    best_map50 = max(map50_vals)
    best_ep    = map50_vals.index(best_map50) + 1

    print(f"  {'mAP50':<18}{mc}{map50:>10.4f}{RESET}{GREEN}{best_map50:>10.4f}{RESET}  {GRAY}(ep{best_ep}){RESET}")
    print(f"  {'mAP50-95':<18}{map5095:>10.4f}")
    print(f"  {'val box_loss':<18}{box_l:>10.4f}")
    print(f"  {'val cls_loss':<18}{cls_l:>10.4f}")
    print(f"  {'val dfl_loss':<18}{dfl_l:>10.4f}")

    # 최근 5 epoch mAP50 추이
    if n >= 2:
        print(f"\n  {BOLD}최근 epoch mAP50 추이{RESET}")
        recent = rows[-min(8, n):]
        for r in recent:
            ep_n  = int(r.get("epoch", 0))
            m50   = float(r.get("metrics/mAP50(B)", 0))
            filled = int(m50 * 40)
            marker = f"{GREEN}▓{RESET}" if ep_n == epoch else "░"
            trend_bar = "█" * filled + "░" * (40 - filled)
            flag = f" {GREEN}★best{RESET}" if m50 == best_map50 else ""
            print(f"  ep{ep_n:3d}  {m50:.4f}  {CYAN}{trend_bar[:20]}{RESET}{flag}")

    # 현재 batch 진행
    print()
    _show_batch_progress()

    print(f"\n  {GRAY}업데이트: {time.strftime('%H:%M:%S')}  |  Ctrl+C 로 종료{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")


def _show_batch_progress():
    prog = read_current_epoch()
    if prog:
        cur, total = prog
        ratio = cur / total if total else 0
        print(f"  {BOLD}현재배치{RESET}  {bar(ratio, 25)}  {cur}/{total}")


def main():
    print("모니터 시작 중...")
    try:
        while True:
            rows = read_csv()
            render(rows)
            time.sleep(POLL_SEC)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}모니터 종료{RESET}")


if __name__ == "__main__":
    main()
