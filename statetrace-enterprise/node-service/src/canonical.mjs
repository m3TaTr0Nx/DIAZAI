import { createHash } from 'node:crypto';

export const ZERO_HASH = '0'.repeat(64);

export function stableStringify(value) {
  if (value === null) return 'null';
  if (typeof value === 'string') return JSON.stringify(value);
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) throw new TypeError('non-finite numbers are not canonical');
    return JSON.stringify(value);
  }
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  if (typeof value === 'object') {
    return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${stableStringify(value[k])}`).join(',')}}`;
  }
  throw new TypeError(`unsupported canonical type: ${typeof value}`);
}

export function sha256Hex(value) {
  const raw = Buffer.isBuffer(value) ? value : Buffer.from(stableStringify(value), 'utf8');
  return createHash('sha256').update(raw).digest('hex');
}

export function stateIndex(value) {
  return Number(BigInt(`0x${sha256Hex(value).slice(0, 16)}`) % 729n);
}

export function stateDigits(index) {
  if (!Number.isInteger(index) || index < 0 || index >= 729) throw new RangeError('index must be 0..728');
  return [Math.floor(index / 81) + 1, Math.floor(index / 9) % 9 + 1, index % 9 + 1];
}

export function indexFromDigits(i, j, k) {
  if (![i,j,k].every(d => Number.isInteger(d) && d >= 1 && d <= 9)) throw new RangeError('digits must be 1..9');
  return (i-1)*81 + (j-1)*9 + (k-1);
}

export function semanticProjection(event) {
  return Object.fromEntries(Object.keys(event).sort().filter(k => !['trace_id','event_id','timestamp'].includes(k)).map(k => [k,event[k]]));
}
