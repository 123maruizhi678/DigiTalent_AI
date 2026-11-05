import { afterEach, expect, it } from 'vitest'
import type { AxiosAdapter } from 'axios'
import { authApi } from '../src/api/auth'
import { request, authTransport, clearAuthentication } from '../src/api/request'

const originalRequest = request.defaults.adapter
const originalAuth = authTransport.defaults.adapter
afterEach(() => {
  request.defaults.adapter = originalRequest
  authTransport.defaults.adapter = originalAuth
  clearAuthentication()
})

it('认证模块最终 URL 和 Cookie 请求配置符合 R09', async () => {
  const urls: string[] = []
  const adapter: AxiosAdapter = async (config) => {
    urls.push(request.getUri(config))
    expect(config.withCredentials).toBe(true)
    return {
      data: { data: { access_token: 'synthetic' } },
      status: 200,
      statusText: 'OK',
      headers: {},
      config,
    }
  }
  request.defaults.adapter = adapter
  authTransport.defaults.adapter = adapter
  await authApi.login({ account: 'test', password: 'synthetic' })
  await authApi.refresh()
  await authApi.session()
  await authApi.logout()
  expect(urls).toEqual([
    '/api/v1/auth/login',
    '/api/v1/auth/refresh',
    '/api/v1/auth/me',
    '/api/v1/auth/logout',
  ])
})

// 尚无真实业务模块，仅验证业务路径在传输层的组合。
it.each(['/files', '/agents/example/executions', '/workflows/example/executions'])(
  '业务路径 %s 通过 Axios 拼接正确',
  async (path) => {
    request.defaults.adapter = async (config) => {
      expect(request.getUri(config)).toBe(`/api/v1${path}`)
      expect(config.withCredentials).toBe(true)
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }
    await request.post(path)
  },
)
