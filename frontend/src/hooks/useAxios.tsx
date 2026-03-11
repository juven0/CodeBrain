import type { AxiosRequestConfig } from "axios";
import axios from "axios";
import { useEffect, useState, useCallback } from "react";

interface UseAxiosResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  status?: number | null;
  refetch: (conf: AxiosRequestConfig) => Promise<unknown>;
}

export function UseAxios<T>(
  config: AxiosRequestConfig,
  immediate: boolean = true,
): UseAxiosResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(immediate);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<number | null>(null);

  const fetch = useCallback(async (conf: AxiosRequestConfig) => {
    setLoading(true);
    setError(null);

    try {
      const res = await axios(conf);
      setData(res.data);
      setStatus(res.status);
      return res.data;
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setStatus(err.status ?? null);
        setError(err.response?.data?.message ?? err.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (immediate) {
      fetch(config);
    }
  }, [config, fetch, immediate]);

  return { data, loading, error, refetch: fetch, status };
}
