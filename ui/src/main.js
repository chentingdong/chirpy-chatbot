/* eslint-disable */

import '@babel/polyfill'

import Vue from 'vue'
Vue.config.productionTip = false

import App from './App.vue'

import VueResource from 'vue-resource'
Vue.use(VueResource)

import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue)

import VueHead from 'vue-head'
Vue.use(VueHead)

import VueMoment from 'vue-moment'
Vue.use(VueMoment)

import filter from './helper.js'
Vue.filter('truncate', filter)

import VueSplit from 'vue-split-panel'
Vue.use(VueSplit)

import VueCodemirror from 'vue-codemirror'
import 'codemirror/addon/display/autorefresh.js'
import 'codemirror/lib/codemirror.css'
import 'codemirror/theme/duotone-light.css'
Vue.use(VueCodemirror, {
  options: {
    styleActiveLine: true,
    lineNumbers: true,
    line: true,
    mode: 'text/javascript',
    json: true,
    lineWrapping: true,
    theme: 'duotone-light',
    indentWithTabs: true,
    smartIndent: true,
    matchBrackets : true,
    autofocus: false,
    autoRefresh:true,
    tabSize: 4
  }
})

import Loading from '@/components/Loading'
Vue.component('loading', Loading)

import Icon from 'vue-awesome/components/Icon'
import 'vue-awesome/icons'
Vue.component('v-icon', Icon)

import vSelect from 'vue-select'
Vue.component('v-select', vSelect)

import VuejsDialog from 'vuejs-dialog'
import 'vuejs-dialog/dist/vuejs-dialog.min.css';
Vue.use(VuejsDialog, {
  html: true,
  okText: 'Ok',
  cancelText: 'Cancel',
  backdropClose: true
})

import VModal from 'vue-js-modal'
Vue.use(VModal, {
  dialog: true,
  dynamic: true,
  injectModalsContainer: true,
  dynamicDefaults: {
    clickToClose: false
  }
})

import Vuetify from 'vuetify'
Vue.use(Vuetify)

// mobile support.
import VueViewports from 'vue-viewports'
const viewportOptions = [
  {
    rule: '320px',
    label: 'mobile'
  },
  {
    rule: '768px',
    label: 'tablet'
  },
  {
    rule: '1024px',
    label: 'desktop'
  },
  {
    rule: '1920px',
    label: 'hd-desktop'
  },
  {
    rule: '2560px',
    label: 'qhd-desktop'
  },
  {
    rule: '3840px',
    label: 'uhd-desktop'
  }
]

Vue.use(VueViewports, viewportOptions)

// Http request headers
Vue.http.headers.common['Content-Type'] = 'application/json'
Vue.http.headers.common['Access-Control-Allow-Origin'] = '*'
Vue.http.headers.common['Accept'] = 'application/json, text/plain, */*'
Vue.http.headers.common['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, Authorization, Access-Control-Allow-Origin'

// app
import router from './router'
const app = new Vue({
  el: '#app',
  router: router,
  template: '<app/>',
  components: { App }
})

export default app