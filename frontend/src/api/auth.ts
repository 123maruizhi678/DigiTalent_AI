// 后端契约扩展点：当前原型不调用这些接口，也不将演示状态视为真实身份。
import { request } from './request'
export interface AuthSession {
  userId: string
  name: string
  roles: string[]
  permissions: string[]
}
export const authApi = {
  login: (credentials: { account: string; password: string }) =>
    request.post<AuthSession>('/auth/login', credentials),
  session: () => request.get<AuthSession>('/auth/session'),
  authorize: (permission: string) =>
    request.post<{ allowed: boolean }>('/auth/authorize', { permission }),
  logout: () => request.post('/auth/logout'),
  invite: (data: { account: string; organizationId: string; roleIds: string[] }) =>
    request.post('/users/invitations', data),
}
// 服务端必须逐请求校验身份、角色、数据范围并记录操作审计；前端菜单和守卫仅改善导航。
