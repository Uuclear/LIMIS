import request from '@/utils/request'

export const getTestTaskList = (params?: any) => request.get('/v1/test-tasks/', { params })
export const getTestTask = (id: number) => request.get(`/v1/test-tasks/${id}/`)
export const assignTask = (id: number, data: any) => request.post(`/v1/test-tasks/${id}/assign/`, data)
export const startTask = (id: number) => request.post(`/v1/test-tasks/${id}/start/`)
export const completeTask = (id: number) => request.post(`/v1/test-tasks/${id}/complete/`)
export const getTodayTasks = () => request.get('/v1/test-tasks/today_list/')
export const getOverdueTasks = () => request.get('/v1/test-tasks/overdue_list/')
export const getAgeCalendar = (params: any) => request.get('/v1/test-tasks/age_calendar/', { params })

export const getRecordTemplates = (params?: any) => request.get('/v1/record-templates/', { params })
export const getRecordTemplate = (id: number) => request.get(`/v1/record-templates/${id}/`)
export const getOriginalRecordList = (params?: any) => request.get('/v1/original-records/', { params })
export const getOriginalRecord = (id: number) => request.get(`/v1/original-records/${id}/`)
export const createOriginalRecord = (data: any) => request.post('/v1/original-records/', data)
export const updateOriginalRecord = (id: number, data: any) => request.put(`/v1/original-records/${id}/`, data)
export const submitRecord = (id: number) => request.post(`/v1/original-records/${id}/submit/`)
export const reviewRecord = (id: number, data: any) => request.post(`/v1/original-records/${id}/review/`, data)

export const getTestResults = (params?: any) => request.get('/v1/test-results/', { params })
export const createTestResult = (data: any) => request.post('/v1/test-results/', data)
export const calculateResult = (data: any) => request.post('/v1/test-results/calculate/', data)

export const getTestCategories = () => request.get('/v1/test-categories/')
export const getTestMethods = (params?: any) => request.get('/v1/test-methods/', { params })
