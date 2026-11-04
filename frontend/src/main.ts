import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { registerElementPlus } from '@/plugins/element-plus'
import './assets/styles/prototype.css'
import './styles/index.css'
import App from './App.vue'
import router from './router'
const app = createApp(App)
app.use(createPinia()).use(router)
registerElementPlus(app)
app.mount('#app')
