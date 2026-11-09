// In-memory stand-in for claude.use('db') and claude.use('user'), same path grammar as the real store.
function makeStore(seed, opts = {}) {
  const docs = new Map(Object.entries(seed || {}));
  const log = [], queries = [];
  const segs = p => p.split('/');
  const snap = (path) => ({ id: segs(path).pop(), exists: docs.has(path), data: () => docs.has(path) ? JSON.parse(JSON.stringify(docs.get(path))) : undefined, metadata: { fromCache: false, hasPendingWrites: false } });
  let failNext = opts.failNext || 0;
  function doc(path) {
    if (segs(path).length % 2) throw new TypeError('doc path needs even segments: ' + path);
    return {
      id: segs(path).pop(), path,
      get: async () => snap(path),
      set: async (data) => {
        if (failNext > 0) { failNext--; throw { code: 'unavailable', message: 'test outage' }; }
        if (typeof data !== 'object' || Array.isArray(data)) throw { code: 'invalid_argument' };
        if (JSON.stringify(data).length > 256 * 1024) throw { code: 'invalid_argument', message: 'too big' };
        docs.set(path, JSON.parse(JSON.stringify(data))); log.push(['set', path]);
      },
      update: async (data) => { if (!docs.has(path)) throw { code: 'invalid_argument' }; docs.set(path, Object.assign(docs.get(path), data)); },
      delete: async () => { if (failNext > 0) { failNext--; throw { code: 'unavailable', message: 'test outage' }; } docs.delete(path); log.push(['delete', path]); },
      collection: (c) => collection(path + '/' + c),
    };
  }
  function collection(path) {
    if (segs(path).length % 2 === 0) throw new TypeError('collection path needs odd segments: ' + path);
    const n = segs(path).length + 1;
    // Query builders as in the contract: up to 10 where filters, one orderBy, limit 1-1000; without orderBy, id order.
    const ops = { '==': (a, b) => a === b, '!=': (a, b) => a !== b, '<': (a, b) => a < b, '<=': (a, b) => a <= b, '>': (a, b) => a > b, '>=': (a, b) => a >= b,
      'in': (a, b) => b.includes(a), 'not-in': (a, b) => !b.includes(a), 'array-contains': (a, b) => Array.isArray(a) && a.includes(b) };
    function query(q) {
      const run = async () => {
        queries.push({ path, ...q });
        let d = [...docs.keys()].filter(k => k.startsWith(path + '/') && segs(k).length === n).sort().map(snap);
        for (const [f, op, v] of q.where) d = d.filter(s => { const x = s.data()[f]; return x !== undefined && ops[op](x, v); });
        if (q.order) { const [f, dir] = q.order; d.sort((a, b) => { const x = a.data()[f], y = b.data()[f]; if (x === y) return 0; if (x === undefined) return 1; if (y === undefined) return -1; return (x < y ? -1 : 1) * (dir === 'desc' ? -1 : 1); }); }
        if (q.limit) d = d.slice(0, q.limit);
        return { docs: d, size: d.length, empty: !d.length };
      };
      return {
        where: (f, op, v) => { if (!ops[op] || q.where.length >= 10) throw { code: 'invalid_argument' }; return query({ ...q, where: [...q.where, [f, op, v]] }); },
        orderBy: (f, dir) => { if (q.order) throw { code: 'invalid_argument' }; return query({ ...q, order: [f, dir || 'asc'] }); },
        limit: (k) => { if (!(k >= 1 && k <= 1000)) throw { code: 'invalid_argument' }; return query({ ...q, limit: k }); },
        get: run,
      };
    }
    return Object.assign(query({ where: [], order: null, limit: 0 }), {
      path,
      doc: (id) => doc(path + '/' + (id || Math.random().toString(36).slice(2))),
    });
  }
  return { db: { doc, collection }, docs, log, queries, setFail: n => { failNext = n; } };
}

// The published db rules, enforced per viewer over one shared store. Levels follow the share menu:
// view (Viewer, Commenter) < interact (Contributor) < admin (Editor) < owner (the artifact's owner).
//   ''                  read view,     write owner      cards and exams: everyone reads, only the owner writes
//   data/users/{self}   write interact                  each viewer's private progress; nobody else reads it
//   reports             read admin,    write owner      the owner (and Editors) read every report; only the owner marks one done
//   reports/{self}      read interact, write interact   each colleague writes and reads only their own
const LEVEL = { view: 1, interact: 2, admin: 3, owner: 4 };
function allowed(path, uid, level, write) {
  const s = path.split('/'), L = LEVEL[level];
  if (s[0] === 'data' && s[1] === 'users') return s.length > 2 && s[2] === uid && L >= LEVEL.interact;
  if (s[0] === 'reports') {
    const own = s.length > 1 && s[1] === uid && L >= LEVEL.interact;
    return own || (write ? L >= LEVEL.owner : L >= LEVEL.admin);
  }
  return write ? L >= LEVEL.owner : L >= LEVEL.view;
}
function viewAs(store, uid, level) {
  const deny = () => { throw { code: 'invalid_argument', message: 'rule' }; };
  const hidden = (id) => ({ id, exists: false, data: () => undefined, metadata: { fromCache: false, hasPendingWrites: false } });
  function wrapDoc(ref) {
    return { id: ref.id, path: ref.path,
      get: async () => allowed(ref.path, uid, level, false) ? ref.get() : hidden(ref.id),
      set: async (d) => allowed(ref.path, uid, level, true) ? ref.set(d) : deny(),
      update: async (d) => allowed(ref.path, uid, level, true) ? ref.update(d) : deny(),
      delete: async () => allowed(ref.path, uid, level, true) ? ref.delete() : deny(),
      collection: (c) => wrapCol(ref.collection(c)) };
  }
  function wrapQuery(q, path) {
    return { where: (...a) => wrapQuery(q.where(...a), path), orderBy: (...a) => wrapQuery(q.orderBy(...a), path), limit: (k) => wrapQuery(q.limit(k), path),
      get: async () => { const r = await q.get(); const docs = r.docs.filter(d => allowed(path + '/' + d.id, uid, level, false)); return { docs, size: docs.length, empty: !docs.length }; } };
  }
  function wrapCol(c) { return Object.assign(wrapQuery(c, c.path), { path: c.path, doc: (id) => wrapDoc(c.doc(id)) }); }
  return { doc: (p) => wrapDoc(store.db.doc(p)), collection: (p) => wrapCol(store.db.collection(p)) };
}
module.exports = { makeStore, viewAs, allowed };
