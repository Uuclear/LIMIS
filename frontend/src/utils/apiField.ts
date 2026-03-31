/**
 * 读取接口对象字段：同时兼容 snake_case 与 camelCase（避免 axios/网关改键名后只有 name 等少数字段能对上）。
 */
export function apiField<T = unknown>(
  obj: Record<string, unknown> | null | undefined,
  snake: string,
): T | undefined {
  if (!obj || typeof obj !== 'object') return undefined
  const camel = snake.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase())
  if (Object.prototype.hasOwnProperty.call(obj, camel)) return obj[camel] as T
  if (Object.prototype.hasOwnProperty.call(obj, snake)) return obj[snake] as T
  return undefined
}

/**
 * 爬取接口返回仍包在 { code, data } 内、或 data 再包一层时，剥到含 standard_no/name 的平面对象。
 * 并转成普通对象，避免 Proxy / 不可枚举键导致 apiField 读不到。
 */
export function unwrapCrawlPayload(raw: unknown): Record<string, unknown> {
  let cur: unknown = raw
  for (let i = 0; i < 5; i++) {
    if (!cur || typeof cur !== 'object') break
    const r = cur as Record<string, unknown>
    const inner = r.data
    if (
      inner != null &&
      typeof inner === 'object' &&
      !Array.isArray(inner) &&
      (Object.prototype.hasOwnProperty.call(inner, 'standard_no') ||
        Object.prototype.hasOwnProperty.call(inner, 'standardNo') ||
        Object.prototype.hasOwnProperty.call(inner, 'name'))
    ) {
      cur = inner
      continue
    }
    break
  }
  try {
    return JSON.parse(JSON.stringify(cur)) as Record<string, unknown>
  } catch {
    return (cur && typeof cur === 'object' ? (cur as Record<string, unknown>) : {}) || {}
  }
}
