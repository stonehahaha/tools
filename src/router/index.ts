import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

export const Layout = () => import('@/layout/index.vue')

// 静态路由
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/text-formatter',
    children: [
      {
        path: 'text-formatter',
        component: () => import('@/views/text-formatter/index.vue'),
        name: 'TextFormatter',
        meta: {
          title: '文本整理',
          icon: 'List',
        },
      },
    ],
  },
]

// 创建路由
const router = createRouter({
  history: createWebHashHistory(),
  routes: constantRoutes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

export default router
