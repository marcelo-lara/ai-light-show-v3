export function normalizedToInternal(nx: number, ny: number, metaW: number, metaH: number, internalW: number, internalH: number) {
  return { x: nx * internalW, y: ny * internalH };
}
