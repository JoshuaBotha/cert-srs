# Explain every remaining due-date mismatch: does ts-fsrs's Good interval equal max(py Good, py Hard + 1)?
import json, copy
from datetime import datetime, timedelta, timezone
from fsrs import Scheduler, Card, Rating, State
sch = Scheduler(desired_retention=0.9, learning_steps=(timedelta(minutes=10),),
                relearning_steps=(timedelta(minutes=10),), maximum_interval=36500, enable_fuzzing=False)
ts = json.load(open('ts_out.json'))
cards, explained, unexplained, exact = {}, 0, [], 0
for i, r in enumerate(json.load(open('history.json'))):
    t = datetime.fromtimestamp(r['t']/1000, tz=timezone.utc)
    pre = cards.get(r['card']) or Card(card_id=1, due=t)
    rating = Rating.Good if r['pass'] else Rating.Again
    c, _ = sch.review_card(copy.deepcopy(pre), rating, review_datetime=t)
    cards[r['card']] = c
    tsd = ts[i]['due']; pyd = int(c.due.timestamp()*1000)
    if tsd == pyd: exact += 1; continue
    h, _ = sch.review_card(copy.deepcopy(pre), Rating.Hard, review_datetime=t)
    ivl = lambda d: round((d.timestamp()*1000 - r['t'])/86400000)
    g_ivl, h_ivl = ivl(c.due), ivl(h.due)
    h_ivl = min(h_ivl, g_ivl)
    want = max(g_ivl, h_ivl + 1) if c.state == State.Review and h.state == State.Review else g_ivl
    got = round((tsd - r['t'])/86400000)
    (explained := explained + 1) if got == want else unexplained.append((r['card'], t.isoformat(), g_ivl, h_ivl, got))
print(f'due exact: {exact}; differ but explained by Good >= Hard+1: {explained}; unexplained: {len(unexplained)}')
for u in unexplained: print(u)
