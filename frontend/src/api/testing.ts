import request from '@/utils/request'

const T = '/v1/testing'

export const getTestTaskList = (params?: any) => request.get(`${T}/tasks/`, { params })
export const getTestTask = (id: number) => request.get(`${T}/tasks/${id}/`)
export const assignTask = (id: number, data: any) => request.post(`${T}/tasks/${id}/assign/`, data)
export const returnTask = (id: number, data?: any) => request.post(`${T}/tasks/${id}/return/`, data || {})
export const returnTaskToCommission = (id: number, data?: any) => request.post(`${T}/tasks/${id}/return-commission/`, data || {})
export const completeTask = (id: number) => request.post(`${T}/tasks/${id}/complete/`)
export const getTaskTimeline = (id: number) => request.get(`${T}/tasks/${id}/timeline/`)
export const getTodayTasks = () => request.get(`${T}/tasks/today_list/`)
export const getOverdueTasks = () => request.get(`${T}/tasks/overdue_list/`)
export const getAgeCalendar = (params: any) => request.get(`${T}/tasks/age_calendar/`, { params })

export const getRecordTemplates = (params?: any) => request.get(`${T}/templates/`, { params })
export const getRecordTemplate = (id: number) => request.get(`${T}/templates/${id}/`)
export const createRecordTemplate = (data: any) => request.post(`${T}/templates/`, data)
export const updateRecordTemplate = (id: number, data: any) => request.put(`${T}/templates/${id}/`, data)
export const deleteRecordTemplate = (id: number) => request.delete(`${T}/templates/${id}/`)
export const getRecordTemplateWordPreview = (id: number, taskId: number) => request.get(`${T}/templates/${id}/word-preview/`, { params: { task_id: taskId } })
/** 按检测任务合并各检测参数对应的原始记录模板结构 */
export const getMergedRecordSchema = (taskId: number) =>
  request.get(`${T}/tasks/${taskId}/merged-record-schema/`)
export const getOriginalRecordList = (params?: any) => request.get(`${T}/records/`, { params })
export const getOriginalRecord = (id: number) => request.get(`${T}/records/${id}/`)
export const createOriginalRecord = (data: any) => request.post(`${T}/records/`, data)
export const updateOriginalRecord = (id: number, data: any) => request.put(`${T}/records/${id}/`, data)
export const submitRecord = (id: number) => request.post(`${T}/records/${id}/submit/`)
export const reviewRecord = (id: number, data: any) => request.post(`${T}/records/${id}/review/`, data)

export const getTestResults = (params?: any) => request.get(`${T}/results/`, { params })
export const createTestResult = (data: any) => request.post(`${T}/results/`, data)
/** 后端为单条结果的 calculate 动作，此处保留占位；若需批量计算请对接后端接口 */
export const calculateResult = (data: any) => request.post(`${T}/results/calculate/`, data)

export const getTestCategories = () => request.get(`${T}/categories/`)
export const getTestParameters = (params?: any) => request.get(`${T}/parameters/`, { params })
export const createTestParameter = (data: any) => request.post(`${T}/parameters/`, data)
export const updateTestParameter = (id: number, data: any) => request.put(`${T}/parameters/${id}/`, data)
export const deleteTestParameter = (id: number) => request.delete(`${T}/parameters/${id}/`)
