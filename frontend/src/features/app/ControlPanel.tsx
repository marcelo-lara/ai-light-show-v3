import React from 'react';
import ParameterInput from './ParameterInput';
import type { PresetSummary, PresetParameter } from './types';

interface Props {
  controlTabs: string[];
  activeTab: string;
  setActiveTab: (t: string) => void;
  activeParameters: PresetParameter[];
  presets: PresetSummary[];
  selectedShow: string;
  setSelectedShow: (s: string) => void;
  activePreset: PresetSummary | null;
  handleGenerate: () => void;
  serverState: string;
  params: Record<string, boolean | number | string>;
  handleParamChange: (id: string, v: boolean | number | string) => void;
}

export default function ControlPanel({ controlTabs, activeTab, setActiveTab, activeParameters, presets, selectedShow, setSelectedShow, activePreset, handleGenerate, serverState, params, handleParamChange }: Props) {
  return (
    <div className="control-panel">
      <div className="control-tabs">
        {controlTabs.map((tab) => (
          <button key={tab} className={`control-tab ${tab === activeTab ? 'active' : ''}`} onClick={() => setActiveTab(tab)} type="button">
            {tab}
          </button>
        ))}
      </div>

      <div className="control-panel-body">
        {activeTab === 'Main' ? (
          <div className="main-tab-panel">
            <div className="math-section">
              <div className="math-section-title">Main</div>
              <div className="form-group">
                <label>Show Name</label>
                <select value={selectedShow} onChange={(event) => setSelectedShow(event.target.value)}>
                  {presets.map((preset) => (
                    <option key={preset.preset_id} value={preset.preset_id}>
                      {preset.name}
                    </option>
                  ))}
                </select>
              </div>
              {activePreset && (
                <div className="preset-summary">
                  <p>{activePreset.description}</p>
                  <div className="preset-tags">
                    {activePreset.tags.map((tag) => (
                      <span key={tag} className="tag-chip">{tag}</span>
                    ))}
                  </div>
                </div>
              )}
              <button className="render-button" onClick={handleGenerate} disabled={serverState === 'GENERATING...' || !selectedShow || !activePreset}>
                {serverState === 'GENERATING...' ? 'GENERATING...' : 'RENDER'}
              </button>
            </div>
          </div>
        ) : activeParameters.length > 0 ? (
          <div className="tab-panel">
            <div className="math-section-title">{activeTab}</div>
            {activeParameters.map((parameter) => (
              <div className="form-group" key={parameter.id}>
                <label>{parameter.label}</label>
                <ParameterInput parameter={parameter} value={params[parameter.id]} onChange={handleParamChange} />
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-panel">No controls in this parameter group.</div>
        )}
      </div>
    </div>
  );
}
