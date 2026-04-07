import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

export const Layout = () => import('@/layout/index.vue')

// constantRoutes
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
          title: '鏂囨湰鏁寸悊',
          icon: 'List',
        },
      },
      {
        path: 'pdf-team-splitter',
        component: () => import('@/views/pdf-team-splitter/index.vue'),
        name: 'PdfTeamSplitter',
        meta: {
          title: 'PDF 行程整理',
          icon: 'Document',
        },
      },
    ],
  },
]

// Create router
const router = createRouter({
  history: createWebHashHistory(),
  routes: constantRoutes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

export default router
