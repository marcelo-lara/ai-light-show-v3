export function normalizedToInternal(nx: number, ny: number, _metaW: number, _metaH: number, internalW: number, internalH: number) {
  return { x: nx * internalW, y: ny * internalH };
}
