import json
from datetime import datetime, timedelta, timezone
from fsrs import Scheduler, Card, Rating
sch = Scheduler(desired_retention=0.9, learning_steps=(timedelta(minutes=10),),
                relearning_steps=(timedelta(minutes=10),), maximum_interval=36500, enable_fuzzing=False)
cards, out = {}, []
for r in json.load(open('history.json')):
    t = datetime.fromtimestamp(r['t']/1000, tz=timezone.utc)
    c = cards.get(r['card']) or Card(card_id=hash(r['card']) % 10**9, due=t)
    c, log = sch.review_card(c, Rating.Good if r['pass'] else Rating.Again, review_datetime=t)
    cards[r['card']] = c
    out.append({'card': r['card'], 't': r['t'], 'state': int(c.state), 'stability': c.stability,
                'difficulty': c.difficulty, 'due': int(c.due.timestamp()*1000), 'step': c.step})
json.dump(out, open('py_out.json','w'))
print('py-fsrs done', len(out))
