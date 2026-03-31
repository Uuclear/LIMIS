import { reactive } from 'vue'

type AsyncFn<TArgs extends unknown[] = unknown[], TResult = unknown> = (...args: TArgs) => Promise<TResult>

export function useActionLock() {
  const lockMap = reactive<Record<string, boolean>>({})

  function isLocked(key: string): boolean {
    return !!lockMap[key]
  }

  async function runLocked<TArgs extends unknown[], TResult>(
    key: string,
    fn: AsyncFn<TArgs, TResult>,
    ...args: TArgs
  ): Promise<TResult | undefined> {
    if (lockMap[key]) return undefined
    lockMap[key] = true
    try {
      return await fn(...args)
    } finally {
      lockMap[key] = false
    }
  }

  return {
    lockMap,
    isLocked,
    runLocked,
  }
}
