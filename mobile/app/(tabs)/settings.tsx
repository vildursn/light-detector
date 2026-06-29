import React from 'react';
import { View, Text, StyleSheet, ScrollView, Switch } from 'react-native';
import { useSettings } from '../../src/hooks/useSettings';

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

function SwitchRow({
  label,
  value,
  onToggle,
}: {
  label: string;
  value: boolean;
  onToggle: (v: boolean) => void;
}) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ true: '#30d158' }}
        thumbColor="#fff"
      />
    </View>
  );
}

export default function SettingsScreen() {
  const [config, update] = useSettings();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Settings</Text>

      <Text style={styles.section}>Camera</Text>
      <Row label="Field of view" value={`${config.cameraFov}°`} />
      <Row label="Heading offset" value={`${config.headingOffset}°`} />

      <Text style={styles.section}>Detection</Text>
      <SwitchRow
        label="Adaptive threshold"
        value={config.adaptiveThreshold}
        onToggle={v => update({ adaptiveThreshold: v })}
      />
      <Row label="Brightness threshold" value={String(config.brightnessThreshold)} />
      <Row label="Adaptive margin" value={String(config.adaptiveMargin)} />
      <Row label="Min threshold" value={String(config.minThreshold)} />
      <Row label="Max threshold" value={String(config.maxThreshold)} />

      <Text style={styles.section}>Alerts</Text>
      <Row label="Confirm after" value={`${config.confirmAfterSeconds}s`} />
      <Row label="Light gone after" value={`${config.lightGoneAfterSeconds}s`} />
      <Row label="Alert cooldown" value={`${config.alertCooldownSeconds}s`} />
      <Row label="Bearing tolerance" value={`${config.bearingTolerance}°`} />

      <Text style={styles.note}>
        Tap values to edit coming soon. Defaults match the Raspberry Pi configuration.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  content: { paddingBottom: 40 },
  heading: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 20,
  },
  section: {
    color: '#555',
    fontSize: 12,
    fontWeight: '600',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 6,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#1a1a1a',
  },
  label: { color: '#fff', fontSize: 15 },
  value: { color: '#555', fontSize: 15 },
  note: {
    color: '#444',
    fontSize: 13,
    paddingHorizontal: 16,
    paddingTop: 24,
    lineHeight: 20,
  },
});
