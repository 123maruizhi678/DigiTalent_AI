// 真实认证接入点；原型演示状态不代表服务端身份。
import {
  request,
  login,
  logout,
  refreshAuthentication,
  type Envelope,
  type CurrentUser,
} from './request'
export const authApi = {
  login,
  refresh: refreshAuthentication,
  session: () => request.get<Envelope<CurrentUser>>('/auth/me'),
  logout,
  invite: (data: { account: string; organizationId: string; roleIds: string[] }) =>
    request.post('/users/invitations', data),
}
