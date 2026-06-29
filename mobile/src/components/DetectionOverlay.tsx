import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { Detection } from '../analysis/types';

const COLORS: Record<string, string> = {
  red: '#ff3b30',
  green: '#30d158',
  white: '#ffffff',
  unknown: '#ffcc00',
};

interface Props {
  detections: Detection[];
  frameWidth: number;
  frameHeight: number;
  viewWidth: number;
  viewHeight: number;
}

export function DetectionOverlay({ detections, frameWidth, frameHeight, viewWidth, viewHeight }: Props) {
  const scaleX = viewWidth / frameWidth;
  const scaleY = viewHeight / frameHeight;

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {detections.map((d, i) => {
        const left = d.bbox.x * scaleX;
        const top = d.bbox.y * scaleY;
        const width = d.bbox.w * scaleX;
        const height = d.bbox.h * scaleY;
        const color = COLORS[d.color] ?? COLORS.unknown;

        return (
          <View
            key={i}
            style={[
              styles.box,
              { left, top, width, height, borderColor: color },
            ]}
          >
            <Text style={[styles.label, { color }]}>
              {d.color} {d.bearing.toFixed(0)}°
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    position: 'absolute',
    borderWidth: 2,
    borderRadius: 3,
  },
  label: {
    position: 'absolute',
    top: -18,
    left: 0,
    fontSize: 11,
    fontWeight: '600',
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 3,
    borderRadius: 2,
  },
});
