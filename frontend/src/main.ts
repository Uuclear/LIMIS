import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { vPermission, vPermissionDisabled } from './utils/permission'
import './assets/styles/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 注册权限指令
app.directive('permission', vPermission)
app.directive('permission-disabled', vPermissionDisabled)

app.mount('#app')
