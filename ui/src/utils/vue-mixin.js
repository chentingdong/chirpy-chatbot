import { illusionistAPI } from '@/utils/rest-config'

const lockMixins = {
  methods: {
    checkLocked (props, apiPath) {
      apiPath = apiPath + '/' + props.item.id
      const currentUser = window.localStorage.getItem('username')
      return illusionistAPI
        .get(apiPath)
        .then((response) => {
          props.item = response.data
          const locked = props.item.editing_by !== null && props.item.editing_by !== currentUser
          props.item.locked = locked
        })
    },
    lockItem: function (item, apiPath) {
      apiPath = apiPath + '/' + item.id
      item.editing_by = window.localStorage.getItem('username')
      if (item.locked) {
        return
      }
      delete item.locked
      delete item.loading
      illusionistAPI
        .put(apiPath, item)
        .catch((e) => {
          console.error('Failed locking item. ' + e)
        })
    },
    unlockItem: function (item, apiPath) {
      apiPath = apiPath + '/' + item.id
      if (item.locked) {
        return
      }
      delete item.locked
      delete item.loading
      item.editing_by = null
      illusionistAPI
        .put(apiPath, item)
        .catch((e) => {
          console.error('Failed unlocking item. ' + e)
        })
    }
  }
}

const agentMixins = {
  data: function () {
    return {
      allAgents: []
    }
  },
  methods: {
    fetchAllAgents: function () {
      const vm = this
      return illusionistAPI
        .get('/api/app', {
          headers: this.requestHeaders
        })
        .then(response => {
          const apps = response.data.objects
          apps.forEach((app) => {
            vm.allAgents.push(app.id)
          })
        })
    }
  }
}

export { lockMixins, agentMixins }
