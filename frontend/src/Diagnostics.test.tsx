import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Diagnostics from './Diagnostics';

describe('Diagnostics', () => {
  it('renders values and shows warning when blank percent > 1', () => {
    const metadata = {
      frame_count: 1000,
      render_diagnostics: {
        average_brightness: 0.5,
        average_rgb_color: [10, 20, 30],
        mean_frame_delta: 20,
        blank_frame_count: 20,
        blank_frame_percent: 2.0,
        render_duration: 10.5,
        frame_count: 1000,
      },
    };

    render(<Diagnostics metadata={metadata} />);

    expect(screen.getByText(/Average Brightness/i)).toBeTruthy();
    expect(screen.getByText(/Average RGB/i)).toBeTruthy();
    expect(screen.getByText(/Blank Frames/i)).toBeTruthy();
    expect(screen.getByText(/Warning: blank-frame percentage/i)).toBeTruthy();
  });

  it('does not show warning when blank percent <= 1', () => {
    const metadata = {
      render_diagnostics: {
        blank_frame_percent: 0.5,
      },
    };

    render(<Diagnostics metadata={metadata} />);
    const warn = screen.queryByText(/Warning: blank-frame percentage/i);
    expect(warn).toBeNull();
  });
});
