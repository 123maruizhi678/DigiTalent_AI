import axios, { type InternalAxiosRequestConfig } from 'axios'

export interface Envelope<T> {
  code: string
  message: string
  data: T
  request_id: string
}
export interface CurrentUser {
  user_id: string
  name: string
  roles: string[]
  permissions: string[]
}
export interface TokenData {
  access_token: string
  token_type: 'Bearer'
  expires_in: number
  user: CurrentUser
}

// 访问令牌仅存内存；刷新 Cookie 由浏览器管理。
// 两个传输实例共用路径配置；认证实例不安装资源请求的自动刷新拦截器。
const transportOptions = {
  baseURL: '/api/v1',
  timeout: 15000,
  withCredentials: true,
}
export const request = axios.create(transportOptions)
export const authTransport = axios.create(transportOptions)
let accessToken: string | null = null
let generation = 0
let refreshing: Promise<void> | null = null
export function clearAuthentication() {
  generation++
  accessToken = null
}
export function getAccessToken() {
  return accessToken
}
export async function login(credentials: { account: string; password: string }) {
  clearAuthentication()
  const epoch = generation
  const response = await authTransport.post<Envelope<TokenData>>('/auth/login', credentials, {
    headers: { 'X-CSRF-Protection': '1' },
  })
  if (epoch !== generation) throw new Error('认证状态已变更')
  accessToken = response.data.data.access_token
  return response
}
export function refreshAuthentication() {
  if (refreshing) return refreshing
  const epoch = generation
  const task = authTransport
    .post<Envelope<TokenData>>('/auth/refresh', undefined, {
      headers: { 'X-CSRF-Protection': '1' },
    })
    .then((response) => {
      if (epoch !== generation) throw new Error('认证状态已变更')
      accessToken = response.data.data.access_token
    })
    .catch((error: unknown) => {
      if (epoch === generation) clearAuthentication()
      throw error
    })
    .finally(() => {
      if (refreshing === task) refreshing = null
    })
  refreshing = task
  return task
}
export async function logout() {
  clearAuthentication()
  // 等待在途刷新落地，再撤销其 Cookie，避免退出后被迟到响应重新设置。
  try {
    await refreshing
  } catch {
    /* 已清理本地认证 */
  }
  return authTransport.post<Envelope<null>>('/auth/logout', undefined, {
    headers: { 'X-CSRF-Protection': '1' },
  })
}
type Retriable = InternalAxiosRequestConfig & { retried?: boolean; epoch?: number }
request.interceptors.request.use((config: Retriable) => {
  config.epoch ??= generation
  if (config.epoch !== generation) throw new Error('认证状态已变更')
  if (accessToken) config.headers.set('Authorization', `Bearer ${accessToken}`)
  else config.headers.delete('Authorization')
  return config
})
request.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config as Retriable | undefined
    if (
      error.response?.status !== 401 ||
      !config ||
      config.retried ||
      config.url?.startsWith('/auth/') ||
      config.epoch !== generation
    )
      throw error
    config.retried = true
    // 迟到的401可以复用已刷新令牌，无须再次轮换。
    if (!accessToken || config.headers.get('Authorization') === `Bearer ${accessToken}`) {
      await refreshAuthentication()
    }
    return request(config)
  },
)
