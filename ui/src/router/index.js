import Vue from 'vue'
import Router from 'vue-router'
import Simulator from '@/pages/Simulator'
import Demo from '@/pages/Demo/Index'
import BotEditor from '@/pages/Bot/BotEditor'
import AdminIndex from '@/pages/Admin/AdminIndex'
import Login from '@/pages/Login'
import AppsSimilarityMatrix from '@/pages/Report/AppsSimilarityMatrix'

Vue.use(Router)

function checkLogin(to, from, next) {
  try {
    const roles = JSON.parse(window.localStorage.getItem('roles'))
    // TODO: need privilage column in role table,
    // attach route to privilages,
    // then remove the hardcoded logic below
    // const canAccess = roles.includes('admin') || roles.includes('designer')
    const canAccess = true
    if (canAccess) {
      next()
    } else {
      next({ name: 'Login', params: { redirectPath: to } })
    }
  } catch (e) {
    next({ name: 'Login' })
  }
}

export default new Router({
  // TODO redesign the route after user login system.
  mode: 'history',
  routes: [
    {
      path: '/simulator/:appId',
      name: 'simulator',
      component: Simulator,
      props: (route) => ({
        workflow: route.params.workflow,
        version: route.params.version,
        app: route.params.app
      })
    },
    {
      path: '/demo/:agentId',
      name: 'demo',
      component: Demo,
      props: (route) => ({
        agentId: route.params.agentId
      })
    },
    {
      path: '/bot/:botId',
      name: 'bot',
      component: BotEditor,
      props: (route) => ({
        botId: route.params.botId
      })
    },
    {
      path: '/admin/:activeTab',
      name: 'admin-index',
      component: AdminIndex,
      beforeEnter: (to, from, next) => {
        checkLogin(to, from, next)
      },
      props: (route) => ({
        activeTab: route.params.activeTab
      })
    },
    {
      path: '/admin',
      redirect: '/admin/bots'
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/reporting/agents/:agentId/similarity_matrix',
      name: 'similarity-matrix',
      component: AppsSimilarityMatrix,
      beforeEnter: (to, from, next) => {
        checkLogin(to, from, next)
      },
      props: (route) => ({
        agentId: route.params.agentId
      })
    }
  ]
})
