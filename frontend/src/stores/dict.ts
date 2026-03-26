import { defineStore } from 'pinia'
import { reactive } from 'vue'
import request from '@/utils/request'

export interface DictOption {
  label: string
  value: string | number
  color?: string
}

export const useDictStore = defineStore('dict', () => {
  const dictMap = reactive<Map<string, DictOption[]>>(new Map())

  async function loadDict(dictType: string): Promise<DictOption[]> {
    if (dictMap.has(dictType)) {
      return dictMap.get(dictType)!
    }
    const data = await request.get<unknown, DictOption[]>(`/v1/system/dict/${dictType}/`)
    dictMap.set(dictType, data)
    return data
  }

  function getDict(dictType: string): DictOption[] {
    return dictMap.get(dictType) || []
  }

  function getDictLabel(dictType: string, value: string | number): string {
    const options = dictMap.get(dictType) || []
    return options.find((o) => o.value === value)?.label || String(value)
  }

  function clearDict(dictType?: string) {
    if (dictType) {
      dictMap.delete(dictType)
    } else {
      dictMap.clear()
    }
  }

  return { dictMap, loadDict, getDict, getDictLabel, clearDict }
})
