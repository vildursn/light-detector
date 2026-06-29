import React, { useCallback, useRef, useState } from 'react';
import { View, Text, StyleSheet, useWindowDimensions } from 'react-native';
import {
  useCameraDevice,
  useCameraPermission,
  useFrameProcessor,
  Camera,
} from 'react-native-vision-camera';
import { useResizePlugin } from 'vision-camera-resize-plugin';
import { useKeepAwake } from 'expo-keep-awake';
import { runOnJS } from 'react-native-reanimated';

import { detectLights } from '../../src/analysis/colorDetector';
import { DetectionOverlay } from '../../src/components/DetectionOverlay';
import { insertDetection } from '../../src/storage/db';
import { processDetections } from '../../src/alerts/alarm';
import { useSettings } from '../../src/hooks/useSettings';
import type { Detection } from '../../src/analysis/types';

const FRAME_WIDTH = 320;
const FRAME_HEIGHT = 240;

export default function WatchScreen() {
  useKeepAwake();

  const { hasPermission, requestPermission } = useCameraPermission();
  const device = useCameraDevice('back');
  const { resize } = useResizePlugin();
  const { width: viewWidth, height: viewHeight } = useWindowDimensions();
  const [config, , configLoaded] = useSettings();

  const [detections, setDetections] = useState<Detection[]>([]);
  const configRef = useRef(config);
  configRef.current = config;

  const onDetections = useCallback(async (dets: Detection[]) => {
    setDetections(dets);
    const cfg = configRef.current;
    for (const d of dets) {
      await insertDetection(d);
    }
    await processDetections(dets, cfg);
  }, []);

  const frameProcessor = useFrameProcessor(
    frame => {
      'worklet';
      const resized = resize(frame, {
        scale: { width: FRAME_WIDTH, height: FRAME_HEIGHT },
        pixelFormat: 'rgb',
        dataType: 'uint8',
      });
      const dets = detectLights(resized, FRAME_WIDTH, FRAME_HEIGHT, configRef.current);
      runOnJS(onDetections)(dets);
    },
    [onDetections],
  );

  if (!hasPermission) {
    return (
      <View style={styles.center}>
        <Text style={styles.text}>Camera permission required</Text>
        <Text style={[styles.text, styles.link]} onPress={requestPermission}>
          Grant permission
        </Text>
      </View>
    );
  }

  if (!device || !configLoaded) {
    return (
      <View style={styles.center}>
        <Text style={styles.text}>Initialising…</Text>
      </View>
    );
  }

  const cameraHeight = viewHeight - 49; // tab bar

  return (
    <View style={styles.container}>
      <Camera
        style={{ width: viewWidth, height: cameraHeight }}
        device={device}
        isActive
        frameProcessor={frameProcessor}
        pixelFormat="yuv"
      />
      <DetectionOverlay
        detections={detections}
        frameWidth={FRAME_WIDTH}
        frameHeight={FRAME_HEIGHT}
        viewWidth={viewWidth}
        viewHeight={cameraHeight}
      />
      {detections.length > 0 && (
        <View style={styles.banner}>
          {detections.map((d, i) => (
            <Text key={i} style={styles.bannerText}>
              {d.color.toUpperCase()} — {d.bearing.toFixed(1)}°
            </Text>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, backgroundColor: '#000', alignItems: 'center', justifyContent: 'center', gap: 12 },
  text: { color: '#fff', fontSize: 16 },
  link: { color: '#30d158' },
  banner: {
    position: 'absolute',
    bottom: 60,
    left: 0,
    right: 0,
    alignItems: 'center',
    gap: 4,
  },
  bannerText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
});
