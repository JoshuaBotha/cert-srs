/* Cert SRS scheduler core — FSRS-6 via ts-fsrs 5.4.2 (pinned).
 * Pure logic, no I/O. The app inlines this file unchanged; Node tests require() it.
 * Spec: Cert SRS v1 spec, "Scheduling" and "Card types" sections.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.CertSched = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var VERSION = 'cert-srs-sched/1.1.0';
  var MIN = 60000, HOUR = 3600000, DAY = 86400000;
  var DEFAULTS = {
    retention: 0.9,       // desired retention (spec: 90%)
    fuzz: true,           // spec: fuzzing on
    budgetMin: 20,        // spec: 20 minutes of measured review time
    rolloverHour: 4,      // a study day runs 04:00 to 04:00 local, as in Anki
    step: '10m',          // spec: a fail comes back after 10 minutes
    maxCardMs: 180000,    // one card never counts for more than 3 minutes of measured time
    learnAheadMin: 20     // nothing else left: show a missed card up to 20 min early (Anki's default)
  };

  function create(F, opts) {
    var o = Object.assign({}, DEFAULTS, opts || {});
    var rng = o.rng || Math.random;
    var params = F.generatorParameters({
      request_retention: o.retention,
      maximum_interval: 36500,
      enable_fuzz: o.fuzz,
      enable_short_term: true,
      learning_steps: [o.step],     // one step: a pass on first sight graduates at once
      relearning_steps: [o.step]
    });
    var f = F.fsrs(params);
    var NEW = F.State.New, LEARNING = F.State.Learning, RELEARNING = F.State.Relearning;

    /* ---------- FSRS state <-> stored JSON ---------- */
    function toCard(s) {
      return {
        due: new Date(s.due), stability: s.stability, difficulty: s.difficulty,
        elapsed_days: s.elapsedDays || 0, scheduled_days: s.scheduledDays || 0,
        learning_steps: s.learningSteps || 0, reps: s.reps || 0, lapses: s.lapses || 0,
        state: s.state, last_review: s.lastReview ? new Date(s.lastReview) : undefined
      };
    }
    function fromCard(c) {
      return {
        due: +c.due, stability: c.stability, difficulty: c.difficulty,
        elapsedDays: c.elapsed_days, scheduledDays: c.scheduled_days,
        learningSteps: c.learning_steps, reps: c.reps, lapses: c.lapses,
        state: c.state, lastReview: c.last_review ? +c.last_review : null
      };
    }

    /* Grade one review. passed=false covers Fail and a guessed correct pick. */
    function grade(fs, passed, now) {
      var card = fs ? toCard(fs) : F.createEmptyCard(new Date(now));
      var rec = f.next(card, new Date(now), passed ? F.Rating.Good : F.Rating.Again);
      return {
        fsrs: fromCard(rec.card),
        stateBefore: card.state,
        elapsedDays: rec.log.elapsed_days,
        rating: passed ? 3 : 1
      };
    }
    /* Retrievability at the true (fractional) elapsed time. ts-fsrs's own
     * get_retrievability floors elapsed days, which reads a card checked minutes
     * before its due time as a whole day fresher (0.947 instead of 0.910). */
    function retrievability(fs, now) {
      if (!fs || fs.state === NEW || !fs.lastReview) return 0;
      var t = Math.max(0, (now - fs.lastReview) / DAY);
      return F.forgetting_curve(params.w, t, fs.stability);
    }
    function isLearning(fs) { return fs.state === LEARNING || fs.state === RELEARNING; }

    /* ---------- study days ---------- */
    function dayStart(now) {
      var d = new Date(now - o.rolloverHour * HOUR);
      d.setHours(o.rolloverHour, 0, 0, 0);
      return +d;
    }
    function dayEnd(now) {
      var d = new Date(dayStart(now)); d.setDate(d.getDate() + 1); return +d;
    }
    function dayKey(now) {
      var d = new Date(now - o.rolloverHour * HOUR);
      return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    }
    function prevKeys(todayKey, n) {
      var p = todayKey.split('-').map(Number), out = [];
      for (var i = 1; i <= n; i++) {
        var d = new Date(p[0], p[1] - 1, p[2] - i, 12);
        out.push(d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'));
      }
      return out;
    }

    /* ---------- new-material throttle ----------
     * Keeps the 7-day average near the budget. Mean of measured minutes over the
     * days studied in the 7 calendar days before today; thresholds and counts are
     * the spec simulation's (budget 20: <16 -> 9, <18.5 -> 7, <21 -> 5, else 2),
     * scaled proportionally if the daily budget changes. */
    function avg7(days, todayKey) {
      var keys = prevKeys(todayKey, 7), tot = 0, n = 0;
      for (var i = 0; i < keys.length; i++) {
        var d = days && days[keys[i]];
        if (d && d.ms > 0) { tot += d.ms; n++; }
      }
      return n ? tot / n / MIN : 0;
    }
    function newQuota(days, todayKey, budgetMin) {
      var b = budgetMin || o.budgetMin, a = avg7(days, todayKey), k = b / 20;
      if (a < b * 0.8) return Math.round(9 * k);
      if (a < b * 0.925) return Math.round(7 * k);
      if (a < b * 1.05) return Math.round(5 * k);
      return Math.round(2 * k);
    }

    /* ---------- the session queue ----------
     * ctx = {
     *   catalog: {trackId: {concept, kind, domain, objective, order}}  (live content)
     *   states:  {trackId: trackState}   (introduced tracks only)
     *   weights: {domain: weight}
     *   usedMs, budgetMs, quota, lastDomain
     * } */
    function siblingsSeenToday(ctx, ds) {
      var seen = {};
      for (var id in ctx.states) {
        var st = ctx.states[id], meta = ctx.catalog[id];
        if (!meta || !st.fsrs.lastReview || st.fsrs.lastReview < ds) continue;
        (seen[meta.concept] = seen[meta.concept] || {})[id] = true;
      }
      return seen;
    }
    function blocked(seen, meta, id) {
      var s = seen[meta.concept];
      if (!s) return false;
      for (var t in s) if (t !== id) return true;   // the concept's other track was seen today
      return false;
    }
    function newToday(ctx, ds) {
      var n = 0;
      for (var id in ctx.states) if (ctx.states[id].introduced >= ds) n++;
      return n;
    }
    function dueList(ctx, now) {
      var ds = dayStart(now), de = dayEnd(now), seen = siblingsSeenToday(ctx, ds);
      var due = [], waitUntil = Infinity, nextLearning = null;
      for (var id in ctx.states) {
        var meta = ctx.catalog[id];
        if (!meta) continue;                         // content withdrawn
        var fs = ctx.states[id].fsrs;
        if (blocked(seen, meta, id)) continue;
        if (isLearning(fs)) {
          if (fs.due <= now) due.push(id);
          else if (fs.due < de && fs.due < waitUntil) { waitUntil = fs.due; nextLearning = id; }
        } else if (fs.due < de) due.push(id);
      }
      return { due: due, waitUntil: waitUntil, nextLearning: nextLearning, seen: seen, ds: ds, de: de };
    }

    /* New tracks: domain with the largest weight x coverage gap first, then the
     * least-covered objective, then authoring order, recall before scenario. */
    function pickNew(ctx, seen) {
      var dom = {}, obj = {}, cand = [];
      for (var id in ctx.catalog) {
        var m = ctx.catalog[id], intro = !!ctx.states[id];
        var d = dom[m.domain] = dom[m.domain] || { tot: 0, intro: 0 };
        var ob = obj[m.objective] = obj[m.objective] || { tot: 0, intro: 0 };
        d.tot++; ob.tot++;
        if (intro) { d.intro++; ob.intro++; }
        else if (!blocked(seen, m, id)) cand.push(id);
      }
      if (!cand.length) return null;
      function w(dm) { return (ctx.weights && ctx.weights[dm]) || 0; }
      function dScore(dm) { var d = dom[dm]; return w(dm) * (1 - d.intro / d.tot); }
      function oCov(ob) { var x = obj[ob]; return x.intro / x.tot; }
      cand.sort(function (a, b) {
        var A = ctx.catalog[a], B = ctx.catalog[b];
        return (dScore(B.domain) - dScore(A.domain)) || (w(B.domain) - w(A.domain)) ||
          (String(A.domain).localeCompare(String(B.domain), undefined, { numeric: true })) ||
          (oCov(A.objective) - oCov(B.objective)) ||
          (String(A.objective).localeCompare(String(B.objective), undefined, { numeric: true })) ||
          ((A.order || 0) - (B.order || 0)) ||
          ((A.kind === 'recall' ? 0 : 1) - (B.kind === 'recall' ? 0 : 1)) ||
          (a < b ? -1 : a > b ? 1 : 0);
      });
      return cand[0];
    }

    /* Next card: due first (lowest retrievability, domains mixed), then new
     * tracks within the day's quota, then missed cards shown early (learn-ahead),
     * until the measured budget is used. */
    function next(ctx, now) {
      if (ctx.usedMs >= ctx.budgetMs) return { done: 'budget' };
      var L = dueList(ctx, now);
      if (L.due.length) {
        var withR = L.due.map(function (id) { return { id: id, r: retrievability(ctx.states[id].fsrs, now), d: ctx.catalog[id].domain }; });
        withR.sort(function (a, b) { return a.r - b.r || (a.id < b.id ? -1 : 1); });
        var pick = withR[0];
        if (ctx.lastDomain != null && pick.d === ctx.lastDomain) {
          for (var i = 1; i < Math.min(3, withR.length); i++) if (withR[i].d !== ctx.lastDomain) { pick = withR[i]; break; }
        }
        return { track: pick.id, isNew: false };
      }
      if (newToday(ctx, L.ds) < ctx.quota) {
        var t = pickNew(ctx, L.seen);
        if (t) return { track: t, isNew: true };
      }
      if (L.nextLearning && L.waitUntil - now <= o.learnAheadMin * MIN) return { track: L.nextLearning, isNew: false, early: true };
      if (L.waitUntil < Infinity) return { wait: L.waitUntil - now };
      return { done: 'empty' };
    }

    /* Header counts: due now or later today, plus new still allowed today. */
    function counts(ctx, now) {
      var L = dueList(ctx, now), learningLater = 0;
      for (var id in ctx.states) {
        var fs = ctx.states[id].fsrs, m = ctx.catalog[id];
        if (m && isLearning(fs) && fs.due > now && fs.due < L.de && !blocked(L.seen, m, id)) learningLater++;
      }
      var avail = 0;
      for (var t in ctx.catalog) if (!ctx.states[t] && !blocked(L.seen, ctx.catalog[t], t)) avail++;
      var nw = Math.max(0, Math.min(ctx.quota - newToday(ctx, L.ds), avail));
      return { due: L.due.length + learningLater, fresh: nw, total: L.due.length + learningLater + nw };
    }
    function dueTomorrow(ctx, now) {
      var d = new Date(dayEnd(now)); d.setDate(d.getDate() + 1);
      var end = +d, n = 0;
      for (var id in ctx.states) if (ctx.catalog[id] && ctx.states[id].fsrs.due < end) n++;
      return n;
    }

    /* ---------- variants and options ---------- */
    function pickVariant(st, ids) {
      var seen = (st && st.seen) || {}, last = st && st.lastVariant;
      var pool = ids.filter(function (v) { return v !== last; });
      if (!pool.length) pool = ids.slice();
      var lo = Infinity;
      pool.forEach(function (v) { lo = Math.min(lo, seen[v] || 0); });
      var ties = pool.filter(function (v) { return (seen[v] || 0) === lo; });
      return ties[Math.floor(rng() * ties.length)];
    }
    function shuffle(a) {
      a = a.slice();
      for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rng() * (i + 1)); var x = a[i]; a[i] = a[j]; a[j] = x; }
      return a;
    }
    /* Four options: the correct one(s) plus distractors drawn from the pool, reshuffled every review. */
    function buildOptions(v) {
      var k = v.pick || 1;
      var wrong = shuffle(v.distractors).slice(0, 4 - k).map(function (d) { return { text: d.text, why: d.why, ok: false }; });
      var right = v.correct.slice(0, k).map(function (c) { return { text: c.text, why: c.why, ok: true }; });
      return shuffle(right.concat(wrong));
    }
    function scoreOptions(opts, picked) {
      var need = opts.filter(function (x) { return x.ok; }).length;
      return picked.length === need && picked.every(function (i) { return opts[i] && opts[i].ok; });
    }

    /* ---------- applying a review to a track state ---------- */
    function applyReview(st, meta, variantId, passed, now) {
      var g = grade(st ? st.fsrs : null, passed, now);
      var seen = Object.assign({}, (st && st.seen) || {});
      seen[variantId] = now;
      return {
        state: {
          track: meta.track, concept: meta.concept, kind: meta.kind,
          introduced: st ? st.introduced : now,
          fsrs: g.fsrs, seen: seen, lastVariant: variantId,
          updated: now, sched: VERSION
        },
        grade: g
      };
    }
    function addDay(days, now, ms) {
      var k = dayKey(now), out = {};
      var keys = Object.keys(days || {}).sort().slice(-29);
      keys.forEach(function (x) { out[x] = days[x]; });
      var cur = out[k] || { ms: 0, n: 0 };
      out[k] = { ms: cur.ms + ms, n: cur.n + 1 };
      return out;
    }
    function measured(ms) { return Math.max(0, Math.min(ms, o.maxCardMs)); }

    return {
      VERSION: VERSION, FSRS_LIB: 'ts-fsrs@5.4.2', options: o, params: params, fsrs: f,
      grade: grade, retrievability: retrievability, isLearning: isLearning,
      dayStart: dayStart, dayEnd: dayEnd, dayKey: dayKey, avg7: avg7, newQuota: newQuota,
      next: next, counts: counts, dueTomorrow: dueTomorrow, pickNew: pickNew,
      pickVariant: pickVariant, shuffle: shuffle, buildOptions: buildOptions, scoreOptions: scoreOptions,
      applyReview: applyReview, addDay: addDay, measured: measured, toCard: toCard, fromCard: fromCard
    };
  }

  return { create: create, VERSION: VERSION };
});
