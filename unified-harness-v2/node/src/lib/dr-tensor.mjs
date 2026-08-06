export const DIGITS = Object.freeze([1,2,3,4,5,6,7,8,9]);
export const UNITS = Object.freeze([1,2,4,5,7,8]);
export const STATORS = Object.freeze([3,6,9]);
export function dr(n) { return ((Math.trunc(n) - 1) % 9 + 9) % 9 + 1; }
export function encodeTriple(i, j, k) {
  for (const value of [i,j,k]) if (!Number.isInteger(value) || value < 1 || value > 9) throw new RangeError('triple digits must be integers 1..9');
  return (i - 1) * 81 + (j - 1) * 9 + (k - 1);
}
export function decodeAddress(address) {
  if (!Number.isInteger(address) || address < 0 || address >= 729) throw new RangeError('address must be 0..728');
  return [Math.floor(address / 81) + 1, Math.floor((address % 81) / 9) + 1, address % 9 + 1];
}
export function flatten27(i, j, k) {
  const digits = [i,j,k];
  for (const value of digits) if (!Number.isInteger(value) || value < 1 || value > 9) throw new RangeError('triple digits must be integers 1..9');
  const split = digits.map((value) => [Math.floor((value - 1) / 3), (value - 1) % 3]);
  return { row: split[0][0] * 9 + split[1][0] * 3 + split[2][0], column: split[0][1] * 9 + split[1][1] * 3 + split[2][1] };
}
export function unflatten27(row, column) {
  for (const value of [row,column]) if (!Number.isInteger(value) || value < 0 || value > 26) throw new RangeError('row and column must be 0..26');
  const trits = (value) => [Math.floor(value / 9), Math.floor((value % 9) / 3), value % 3];
  const hi = trits(row), lo = trits(column);
  return [3 * hi[0] + lo[0] + 1, 3 * hi[1] + lo[1] + 1, 3 * hi[2] + lo[2] + 1];
}
function gcd(a,b) { while (b) [a,b] = [b,a%b]; return Math.abs(a); }
export function classify(i,j,k) {
  const pairwise = gcd(i,j) === 1 && gcd(i,k) === 1 && gcd(j,k) === 1;
  const setwise = gcd(gcd(i,j),k) === 1;
  return pairwise ? 'y' : setwise ? 's' : 'n';
}
export function admissible(i,j,k) { return (i === j && j === k) || (i !== j && i !== k && j !== k); }
export function shell(i,j,k) { return new Set([i,j,k]).size === 2; }
export function hinge(i,j,k) { return i * k === j * j; }
export function inspectTriple(i,j,k) {
  const address = encodeTriple(i,j,k); const matrix = flatten27(i,j,k);
  return { i,j,k, triple: `${i}${j}${k}`, address, matrix, trits: address.toString(3).padStart(6,'0'), dr: dr(i+j+k), class: classify(i,j,k), admissible: admissible(i,j,k), shell: shell(i,j,k), hinge: hinge(i,j,k), rotor_axes: [i,j,k].map((v) => UNITS.includes(v)), stator_axes: [i,j,k].map((v) => STATORS.includes(v)) };
}
export function census() {
  const counts = { total:0, admissible:0, shell:0, hinge:0, y:0, s:0, n:0 };
  for (const i of DIGITS) for (const j of DIGITS) for (const k of DIGITS) { counts.total++; if (admissible(i,j,k)) counts.admissible++; if (shell(i,j,k)) counts.shell++; if (hinge(i,j,k)) counts.hinge++; counts[classify(i,j,k)]++; }
  return counts;
}
