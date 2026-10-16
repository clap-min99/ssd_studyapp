// 사용자별 메모리 캐시. 브라우저를 닫으면 사라지고 최대 80건만 보관한다.
export function createReadCache({ now = Date.now, limit = 80 } = {}) {
  const values = new Map();
  const pending = new Map();
  let generation = 0;
  return {
    read(key, load, ttl = 0) {
      const cached = values.get(key);
      if (ttl > 0 && cached?.expires > now()) return Promise.resolve(structuredClone(cached.data));
      values.delete(key);
      if (!pending.has(key)) {
        const started = generation;
        const request = Promise.resolve().then(load).then((data) => {
          if (ttl > 0 && generation === started) {
            values.set(key, { data: structuredClone(data), expires: now() + ttl });
            while (values.size > limit) values.delete(values.keys().next().value);
          }
          return data;
        }).finally(() => {
          if (pending.get(key) === request) pending.delete(key);
        });
        pending.set(key, request);
      }
      return pending.get(key).then((data) => structuredClone(data));
    },
    clear() {
      generation += 1;
      values.clear();
      pending.clear();
    },
  };
}
