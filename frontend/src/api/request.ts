import axios from 'axios'
// 后端接入扩展点；当前页面不调用此实例。
export const request = axios.create({ baseURL: '/api', timeout: 15000 })
