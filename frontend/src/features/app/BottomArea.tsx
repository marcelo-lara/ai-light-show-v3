import React from 'react';
import ControlPanel from './ControlPanel';
import CanvasRenderer from './CanvasRenderer';

interface Props {
  controlTabs: string[];
  activeTab: string;
  setActiveTab: (t: string) => void;
  activeParameters: any[];
  presets: any[];
  selectedShow: string;
  setSelectedShow: (s: string) => void;
  activePreset: any;
  handleGenerate: () => void;
  serverState: string;
  params: Record<string, boolean | number | string>;
  handleParamChange: (id: string, v: boolean | number | string) => void;
  metadataRef: { current: any };
  legacyFramesData: { current: any[] };
  binaryFramesData: { current: Uint8Array | null };
  overlaysRef: { current: { fixtures: any[]; pois: any[] } };
  wavesurfer: { current: any };
  setDrift: (v: number) => void;
}

export default function BottomArea(props: Props) {
  return (
    <div className="bottom-area">
      <ControlPanel
        controlTabs={props.controlTabs}
        activeTab={props.activeTab}
        setActiveTab={props.setActiveTab}
        activeParameters={props.activeParameters}
        presets={props.presets}
        selectedShow={props.selectedShow}
        setSelectedShow={props.setSelectedShow}
        activePreset={props.activePreset}
        handleGenerate={props.handleGenerate}
        serverState={props.serverState}
        params={props.params}
        handleParamChange={props.handleParamChange}
      />

      <div className="canvas-render">
        <CanvasRenderer
          metadataRef={props.metadataRef}
          legacyFramesData={props.legacyFramesData}
          binaryFramesData={props.binaryFramesData}
          overlaysRef={props.overlaysRef}
          wavesurfer={props.wavesurfer}
          setDrift={props.setDrift}
        />
      </div>
    </div>
  );
}
