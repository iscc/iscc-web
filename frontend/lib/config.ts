/** Runtime configuration the backend injects into the served HTML as `window.__ISCC_WEB__`. */

export interface RuntimeConfig {
  /** Initial state of the Semantic Code generation toggle in the intake card. */
  semanticDefault: boolean;
  /** Seconds after which uploaded files are deleted (backend `ISCC_WEB_STORAGE_EXPIRY`). */
  storageExpiry: number;
}

/** Built-in fallbacks used when no backend config is present (e.g. unit tests). */
const FALLBACK: RuntimeConfig = { semanticDefault: true, storageExpiry: 3600 };

/** Backend-injected runtime config merged over the built-in fallbacks. */
export function runtimeConfig(): RuntimeConfig {
  const injected = (globalThis as typeof globalThis & { __ISCC_WEB__?: Partial<RuntimeConfig> }).__ISCC_WEB__;
  return { ...FALLBACK, ...injected };
}

/** Human-readable duration in whole units: 3600 -> "one hour", 1800 -> "30 minutes". */
export function formatDuration(seconds: number): string {
  const units: [number, string][] = [
    [3600, "hour"],
    [60, "minute"],
    [1, "second"],
  ];
  for (const [size, name] of units) {
    if (seconds >= size && seconds % size === 0) {
      const value = seconds / size;
      return value === 1 ? `one ${name}` : `${value} ${name}s`;
    }
  }
  return `${seconds} seconds`;
}

/** Label for the storage-expiry copy, derived from the injected runtime config. */
export function expiryLabel(): string {
  return formatDuration(runtimeConfig().storageExpiry);
}
