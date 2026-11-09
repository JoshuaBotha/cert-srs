# The spec's original pacing script (from the design session), constants inlined, logic unchanged.
import random, statistics, sys
from datetime import datetime, timedelta, timezone
from fsrs import Scheduler, Card, Rating
N_RECALL, N_SCEN = 219, 153
SECS = {"recall": {"pass": 12, "fail": 20, "first": 6}, "scenario": {"pass": 50, "fail": 75, "first": 15}}
P_FIRST = {"recall": 0.55, "scenario": 0.55}
def run(seed, budget=20.0, days=150):
    rng = random.Random(seed)
    sch = Scheduler(desired_retention=0.9, learning_steps=(timedelta(minutes=10),),
                    relearning_steps=(timedelta(minutes=10),), enable_fuzzing=True)
    pool = ["recall"] * N_RECALL + ["scenario"] * N_SCEN
    rng.shuffle(pool)
    start = datetime(2026, 11, 16, 6, 0, tzinfo=timezone.utc)
    active, daily, intro_day, news = [], [], None, []
    for d in range(days):
        t = start + timedelta(days=d)
        end = t + timedelta(hours=16)
        avg7 = statistics.mean(daily[-7:]) if daily else 0
        n = 9 if avg7 < budget - 4 else 7 if avg7 < budget - 1.5 else 5 if avg7 < budget + 1 else 2
        k = 0
        for _ in range(n):
            if pool:
                active.append({"card": Card(due=t), "kind": pool.pop(), "new": True}); k += 1
        news.append(k)
        if not pool and intro_day is None:
            intro_day = d + 1
        secs = 0
        while True:
            due = [a for a in active if a["card"].due <= end]
            if not due:
                break
            nxt = min(due, key=lambda a: a["card"].due)
            t = max(t, nxt["card"].due)
            p = P_FIRST[nxt["kind"]] if nxt["new"] else sch.get_card_retrievability(nxt["card"], current_datetime=t)
            ok = rng.random() < p
            s = SECS[nxt["kind"]]["pass" if ok else "fail"] + (SECS[nxt["kind"]]["first"] if nxt["new"] else 0)
            nxt["card"], _ = sch.review_card(nxt["card"], Rating.Good if ok else Rating.Again, review_datetime=t)
            nxt["new"] = False
            secs += s
            t += timedelta(seconds=s)
        daily.append(secs / 60)
    return daily, intro_day, news
res = []
for seed in range(1, 9):
    daily, intro, news = run(seed)
    wk = [statistics.mean(daily[i:i + 7]) for i in range(0, intro - 6, 7)]
    res.append((intro, statistics.mean(daily[:intro]), max(wk), statistics.mean(daily[intro:intro + 28]), statistics.mean(news[:intro])))
print(f"intro weeks {min(r[0] for r in res)/7:.1f}–{max(r[0] for r in res)/7:.1f} | new/day {statistics.mean(r[4] for r in res):.1f} | mean {statistics.mean(r[1] for r in res):.1f} min | peak week {max(r[2] for r in res):.1f} | after {statistics.mean(r[3] for r in res):.1f} min")
