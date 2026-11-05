import { afterEach, describe, expect, it } from 'vitest'
import { AxiosError, type AxiosAdapter, type InternalAxiosRequestConfig } from 'axios'
import {
  request,
  authTransport,
  clearAuthentication,
  getAccessToken,
  login,
  logout,
  refreshAuthentication,
} from '../src/api/request'

const original = authTransport.defaults.adapter
function response(config: InternalAxiosRequestConfig, token = 'synthetic') {
  return {
    data: { code: '0', data: { access_token: token } },
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  }
}
afterEach(() => {
  authTransport.defaults.adapter = original
  clearAuthentication()
})
describe('认证请求契约', () => {
  it('同一时间只刷新一次，并携带CSRF头和Cookie', async () => {
    let count = 0
    const adapter: AxiosAdapter = async (config) => {
      count++
      expect(config.baseURL).toBe('/api/v1')
      expect(config.withCredentials).toBe(true)
      expect(config.headers.get('X-CSRF-Protection')).toBe('1')
      return response(config)
    }
    authTransport.defaults.adapter = adapter
    // 每个实例显式使用测试适配器。
    const pending = refreshAuthentication()
    expect(refreshAuthentication()).toBe(pending)
    await pending
    expect(count).toBe(1)
    expect(getAccessToken()).toBe('synthetic')
  })
  it('退出期间迟到刷新不能恢复内存身份', async () => {
    let release!: () => void
    authTransport.defaults.adapter = async (config) => {
      if (config.url === '/auth/refresh')
        await new Promise<void>((resolve) => {
          release = resolve
        })
      return response(config)
    }
    const refresh = refreshAuthentication()
    const rejected = expect(refresh).rejects.toThrow('认证状态已变更')
    await Promise.resolve()
    const exit = logout()
    release()
    await rejected
    await exit
    expect(getAccessToken()).toBeNull()
  })
  it('登录失败不保留旧访问令牌', async () => {
    authTransport.defaults.adapter = async (config) => response(config)
    await login({ account: 'test', password: 'synthetic-password' })
    authTransport.defaults.adapter = async () => {
      throw new Error('rejected')
    }
    await expect(login({ account: 'test', password: 'wrong' })).rejects.toThrow()
    expect(getAccessToken()).toBeNull()
  })
})

it('资源401最多重试一次', async () => {
  let refreshes = 0
  let attempts = 0
  authTransport.defaults.adapter = async (config) => {
    refreshes++
    return response(config)
  }
  const originalRequest = request.defaults.adapter
  request.defaults.adapter = async (config) => {
    attempts++
    throw new AxiosError('unauthorized', 'ERR_BAD_REQUEST', config, undefined, {
      ...response(config),
      status: 401,
    })
  }
  try {
    await expect(request.get('/protected')).rejects.toThrow('unauthorized')
    expect(attempts).toBe(2)
    expect(refreshes).toBe(1)
  } finally {
    request.defaults.adapter = originalRequest
  }
})
