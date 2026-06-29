import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import { queryRecent, clearAll, type DetectionRow } from '../../src/storage/db';

const COLOR_DOT: Record<string, string> = {
  red: '#ff3b30',
  green: '#30d158',
  white: '#e5e5ea',
};

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString();
}

export default function LogScreen() {
  const [rows, setRows] = useState<DetectionRow[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const data = await queryRecent(200);
    setRows(data);
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  const onClear = useCallback(() => {
    Alert.alert('Clear log', 'Delete all detection records?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Clear',
        style: 'destructive',
        onPress: async () => {
          await clearAll();
          setRows([]);
        },
      },
    ]);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Detection Log</Text>
        {rows.length > 0 && (
          <TouchableOpacity onPress={onClear}>
            <Text style={styles.clearBtn}>Clear</Text>
          </TouchableOpacity>
        )}
      </View>
      <FlatList
        data={rows}
        keyExtractor={r => String(r.id)}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#555" />}
        ListEmptyComponent={
          <Text style={styles.empty}>No detections yet. Start watching to log lights.</Text>
        }
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={[styles.dot, { backgroundColor: COLOR_DOT[item.color] ?? '#888' }]} />
            <View style={styles.rowBody}>
              <Text style={styles.rowColor}>{item.color}</Text>
              <Text style={styles.rowBearing}>{item.bearing.toFixed(1)}°</Text>
            </View>
            <Text style={styles.rowTime}>{formatTime(item.timestamp)}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  clearBtn: { color: '#ff3b30', fontSize: 16 },
  empty: { color: '#555', textAlign: 'center', marginTop: 80, paddingHorizontal: 32 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#1a1a1a',
    gap: 12,
  },
  dot: { width: 10, height: 10, borderRadius: 5 },
  rowBody: { flex: 1, flexDirection: 'row', gap: 8 },
  rowColor: { color: '#fff', fontSize: 15, fontWeight: '600', textTransform: 'capitalize' },
  rowBearing: { color: '#888', fontSize: 15 },
  rowTime: { color: '#555', fontSize: 13 },
});
