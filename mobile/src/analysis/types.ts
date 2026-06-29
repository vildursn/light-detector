export type LightColor = 'red' | 'green' | 'white' | 'unknown';

export interface Detection {
  bearing: number;
  color: LightColor;
  confidence: number;
  bbox: { x: number; y: number; w: number; h: number };
}

export interface Config {
  cameraFov: number;
  headingOffset: number;
  brightnessThreshold: number;
  adaptiveThreshold: boolean;
  adaptiveMargin: number;
  minThreshold: number;
  maxThreshold: number;
  minBlobArea: number;
  maxBlobArea: number;
  confirmAfterSeconds: number;
  lightGoneAfterSeconds: number;
  alertCooldownSeconds: number;
  bearingTolerance: number;
}

export const DEFAULT_CONFIG: Config = {
  cameraFov: 90,
  headingOffset: 0,
  brightnessThreshold: 200,
  adaptiveThreshold: true,
  adaptiveMargin: 80,
  minThreshold: 120,
  maxThreshold: 245,
  minBlobArea: 5,
  maxBlobArea: 5000,
  confirmAfterSeconds: 2,
  lightGoneAfterSeconds: 5,
  alertCooldownSeconds: 60,
  bearingTolerance: 7,
};
