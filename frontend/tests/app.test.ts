import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import App from '@/App.vue'

describe('application shell', () => {
  it('renders the current route through the root component', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<main>工程基线验证</main>' } }],
    })
    await router.push('/')
    await router.isReady()

    const wrapper = mount(App, { global: { plugins: [router] } })
    try {
      expect(wrapper.find('main').text()).toBe('工程基线验证')
    } finally {
      wrapper.unmount()
    }
  })
})
