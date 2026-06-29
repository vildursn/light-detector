import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { DEFAULT_CONFIG, type Config } from '../analysis/types';

const KEY = 'light_detector_config';

export function useSettings(): [Config, (patch: Partial<Config>) => Promise<void>, boolean] {
  const [config, setConfig] = useState<Config>(DEFAULT_CONFIG);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(KEY).then(raw => {
      if (raw) {
        try {
          setConfig({ ...DEFAULT_CONFIG, ...JSON.parse(raw) });
        } catch {
          // corrupt storage — fall back to defaults
        }
      }
      setLoaded(true);
    });
  }, []);

  const update = useCallback(async (patch: Partial<Config>) => {
    setConfig(prev => {
      const next = { ...prev, ...patch };
      AsyncStorage.setItem(KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  return [config, update, loaded];
}
