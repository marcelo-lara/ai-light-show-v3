interface DiagnosticsProps {
  metadata?: any;
}

export default function Diagnostics({ metadata }: DiagnosticsProps) {
  const d = metadata?.render_diagnostics;

  const fmt = (v: unknown) => (v === undefined || v === null ? 'N/A' : String(v));

  const avgRgb = d?.average_rgb_color
    ? `rgb(${d.average_rgb_color.join(',')})`
    : null;

  const blankPercent = d?.blank_frame_percent;
  const showWarning = typeof blankPercent === 'number' && blankPercent > 1;

  return (
    <div className="diagnostics-panel" style={{ marginTop: 8 }}>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <div>Average Brightness: {fmt(d?.average_brightness)}</div>
        <div>Average RGB: {avgRgb ? <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}><span>{avgRgb}</span><span style={{ width: 18, height: 18, background: avgRgb, border: '1px solid #000' }} /></span> : fmt(d?.average_rgb_color)}</div>
        <div>Mean Frame Δ: {fmt(d?.mean_frame_delta)}</div>
        <div>Blank Frames: {fmt(d?.blank_frame_count)} ({fmt(d?.blank_frame_percent)}%)</div>
        <div>Render Duration: {fmt(d?.render_duration)}</div>
        <div>Frame Count: {fmt(d?.frame_count ?? metadata?.frame_count)}</div>
      </div>

      {showWarning && (
        <div style={{ color: 'white', background: '#c0392b', padding: '6px 8px', marginTop: 8, display: 'inline-block' }}>
          Warning: blank-frame percentage &gt; 1%
        </div>
      )}
    </div>
  );
}
