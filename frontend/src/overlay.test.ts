import { describe, it, expect } from 'vitest';
import { normalizedToInternal } from './overlay';

describe('normalizedToInternal', () => {
  it('maps normalized coords to internal pixels', () => {
    const res = normalizedToInternal(0.5, 0.25, 100, 200, 200, 400);
    expect(res.x).toBe(100);
    expect(res.y).toBe(100);
  });
});
