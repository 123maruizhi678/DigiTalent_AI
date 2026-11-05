// @vitest-environment node
import { createServer } from 'node:http'
import { expect, it } from 'vitest'
import { createServer as createViteServer } from 'vite'
import config from '../vite.config'

it('Vite 实际转发保留完整 URL 和 Cookie 路径', async () => {
  const upstream = createServer((req, res) => {
    res.setHeader('Set-Cookie', 'dt_refresh=synthetic; Path=/api/v1/auth; HttpOnly')
    res.end(req.url)
  })
  await new Promise((resolve) => upstream.listen(0, '127.0.0.1', resolve))
  const proxy = config.server.proxy['/api']
  expect(proxy).toEqual({ target: 'http://127.0.0.1:8080', changeOrigin: true })
  const vite = await createViteServer({
    ...config,
    configFile: false,
    server: {
      ...config.server,
      port: 0,
      proxy: { '/api': { ...proxy, target: `http://127.0.0.1:${upstream.address().port}` } },
    },
  })
  try {
    await vite.listen()
    for (const path of [
      '/auth/login',
      '/auth/refresh',
      '/auth/logout',
      '/auth/me',
      '/files',
      '/agents/example/executions',
      '/workflows/example/executions',
    ]) {
      const response = await globalThis.fetch(
        `http://127.0.0.1:${vite.httpServer.address().port}/api/v1${path}`,
      )
      expect(await response.text()).toBe(`/api/v1${path}`)
      expect(response.headers.get('set-cookie')).toContain('Path=/api/v1/auth')
    }
  } finally {
    await vite.close()
    await new Promise((resolve) => upstream.close(resolve))
  }
}, 20000)
