"""
학습 감시 스크립트.
- 5 epoch마다 상태 출력
- 최근 10 epoch 동안 mAP50 변화량 < threshold 이면 학습 프로세스 종료
"""

import csv
import os
import sys
import time
import signal
from pathlib import Path

RESULTS_CSV = Path(__file__).parent / "models" / "runs" / "pothole-crack" / "results.csv"
TRAIN_PID   = int(sys.argv[1]) if len(sys.argv) > 1 else None

MAP_COL       = "metrics/mAP50(B)"
REPORT_EVERY  = 5      # N epoch마다 보고
PATIENCE_EP   = 10     # 이 에폭 수 동안
MAP_THRESHOLD = 0.003  # mAP50 최소 개선량 (미만이면 종료)
POLL_SEC      = 30     # CSV 폴링 간격(초)


def read_results():
    if not RESULTS_CSV.exists():
        return []
    with open(RESULTS_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def fmt(val):
    try:
        return f"{float(val):.4f}"
    except Exception:
        return val


def kill_train(pid):
    if pid is None:
        print("[watcher] PID 없음 — 수동으로 종료하세요.")
        return
    try:
        if sys.platform == "win32":
            os.system(f"taskkill /F /PID {pid}")
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"[watcher] PID {pid} 종료 신호 전송 완료.")
    except Exception as e:
        print(f"[watcher] 종료 실패: {e}")


def main():
    print(f"[watcher] 시작 — 학습 PID: {TRAIN_PID}")
    print(f"[watcher] {REPORT_EVERY}에폭마다 보고 / "
          f"최근 {PATIENCE_EP}에폭 mAP50 개선 < {MAP_THRESHOLD} 이면 자동 종료")
    sys.stdout.flush()

    last_reported = 0

    while True:
        time.sleep(POLL_SEC)
        rows = read_results()
        if not rows:
            continue

        n = len(rows)
        latest = rows[-1]
        epoch  = int(latest.get("epoch", 0))
        map50  = float(latest.get(MAP_COL, 0))

        # ── 5에폭마다 보고 ───────────────────────────────────────────
        if epoch >= last_reported + REPORT_EVERY:
            last_reported = epoch
            time_s = float(latest.get("time", 0))
            # 직전 epoch과 시간 차이로 1 epoch 소요시간 계산
            if n >= 2:
                prev_time = float(rows[-2].get("time", 0))
                ep_time   = time_s - prev_time
            else:
                ep_time = time_s

            map5095 = float(latest.get("metrics/mAP50-95(B)", 0))
            box_loss = float(latest.get("val/box_loss", 0))
            cls_loss = float(latest.get("val/cls_loss", 0))

            # 예상 남은 시간
            if n >= 2:
                avg_ep = (time_s - float(rows[0].get("time", 0))) / max(epoch - 1, 1)
            else:
                avg_ep = ep_time
            remaining = avg_ep * (100 - epoch) / 60

            print(
                f"\n[Epoch {epoch:3d}/100]  "
                f"mAP50={map50:.4f}  mAP50-95={map5095:.4f}  "
                f"val_box={box_loss:.4f}  val_cls={cls_loss:.4f}  "
                f"epoch소요={ep_time/60:.1f}분  예상잔여={remaining:.0f}분"
            )
            sys.stdout.flush()

        # ── 10에폭 변화율 체크 → 자동 종료 ─────────────────────────
        if n >= PATIENCE_EP:
            recent = [float(r.get(MAP_COL, 0)) for r in rows[-PATIENCE_EP:]]
            improvement = max(recent) - min(recent)
            if improvement < MAP_THRESHOLD:
                print(
                    f"\n[watcher] 최근 {PATIENCE_EP}에폭 mAP50 변화량={improvement:.4f} "
                    f"< {MAP_THRESHOLD} → 학습 자동 종료"
                )
                sys.stdout.flush()
                kill_train(TRAIN_PID)
                break

        # 학습 프로세스가 이미 종료됐으면 감시 종료
        if TRAIN_PID:
            try:
                if sys.platform == "win32":
                    result = os.popen(f"tasklist /FI \"PID eq {TRAIN_PID}\" /NH").read()
                    if str(TRAIN_PID) not in result:
                        print(f"\n[watcher] PID {TRAIN_PID} 종료 감지 — 감시 종료")
                        break
                else:
                    os.kill(TRAIN_PID, 0)
            except ProcessLookupError:
                print(f"\n[watcher] PID {TRAIN_PID} 종료 감지 — 감시 종료")
                break


if __name__ == "__main__":
    main()
