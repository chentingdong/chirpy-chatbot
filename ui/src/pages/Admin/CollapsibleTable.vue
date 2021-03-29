<template>
  <v-data-table class="elevation-1"
                :headers="headers"
                :items="items"
                :default-sort="sortValue"
                :rows-per-page-items="rowsPerPageItems"
                :pagination.sync="pagination" expand>
    <loading v-if="loading"></loading>
    <template slot="items" slot-scope="props">
      <tr @click="expandCollapsedRow(props)" :class="{expanded: props.expanded}">
        <td v-for="(itemKey, index) in itemKeys" :key="index">
          {{ props.item[itemKey] }}
        </td>
      </tr>
    </template>
    <template slot="expand" slot-scope="props">
      <slot name="edit-template" :saveItem="saveItem" :deleteItem="deleteItem" :props="props"></slot>
    </template>
  </v-data-table>
</template>

<script>
import { illusionistAPI } from '@/utils/rest-config'
import { lockMixins } from '@/utils/vue-mixin'
import { clearTimeout } from 'timers';
import idleTimeout from 'idle-timeout'

export default {
  props: [ 'componentName', 'headers', 'items', 'itemKeys', 'sortValue' ],
  data: function () {
    return {
      apiPaths: {
        actions: '/api/action',
        services: '/api/service',
        apps: '/api/app',
        agents: '/api/agent'
      },
      pagination: {
        rowsPerPage: 50
      },
      rowsPerPageItems: [ 10, 20, 50, 100, 200, 500 ],
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      lockingTimeout: 30000
    }
  },
  mixins: [ lockMixins ],
  methods: {
    expandCollapsedRow (props) {
      const vm = this
      const apiPath = this.apiPaths[ this.componentName ]
      this.$parent.loading = true
      this.checkLocked(props, apiPath).then(() => {
        this.$parent.loading = false
        if (!props.expanded) {
          props.expanded = true
          // following line does not work, why?
          // this.bots[ props.index ] = props.item
          this.items[ props.index ].editing_by = props.item.editing_by
          this.items[ props.index ].locked = props.item.locked
          this.lockItem(props.item, apiPath)

          idleTimeout(
            () => {
              vm.unlockItem(props.item, apiPath)
              props.expanded = false
            },
            {
              element: document,
              timeout: vm.lockingTimeout,
              loop: false
            }
          )
        } else {
          props.expanded = false
          this.unlockItem(props.item, apiPath)
        }
      })
    },
    prepareSave (props) {
      delete props.item.locked
      const editedItem = Object.assign({}, props.item)

      if ((this.componentName === 'agents' || this.componentName === 'apps')) {
        if (editedItem.settings && !this.isJSON(editedItem.settings)) {
          this.$dialog.alert('Invalid Settings JSON')
          return
        }
        if (editedItem.params && !this.isJSON(editedItem.params)) {
          this.$dialog.alert('Invalid Params JSON')
          return
        }
      }

      editedItem.params = JSON.parse(editedItem.params)

      if (this.componentName === 'agents' || this.componentName === 'apps') {
        editedItem.settings = editedItem.settings ? JSON.parse(editedItem.settings) : null
      }

      if (editedItem.version) {
        editedItem.version = Number.isInteger(editedItem.version) ? Number.parseInt(editedItem.version) : 1
      }
      return editedItem
    },
    saveItem (props) {
      const vm = this
      const editedItem = vm.prepareSave(props)
      const apiPath = vm.apiPaths[ vm.componentName ]
      const url = apiPath + '/' + props.item.id
      vm.loading = true
      illusionistAPI
        .put(url, editedItem)
        .then(response => {
          vm.items[ props.index ] = response.data
          vm.$dialog.alert('Successfully updated ' + editedItem.name)
          props.expanded = false
        })
        .catch(e => {
          vm.$dialog.alert('Failed to update ' + editedItem.name)
        })
        .then(() => {
          vm.loading = false
          const item = vm.prepareSave(props)
          item.editing_by = null
          vm.unlockItem(item, vm.apiPaths[ vm.componentName ])
        })
    },
    deleteItem (props) {
      const vm = this
      vm.loading = true
      vm.$dialog
        .confirm('Are you sure you want to delete this item?')
        .then(() => {
          const url = vm.apiPaths[ vm.componentName ] + '/' + props.item.id
          illusionistAPI
            .delete(url)
            .then(response => {
              vm.$dialog.alert('Successfully deleted ' + props.item.name)
              vm.items.splice(props.index, 1)
            })
            .catch(e => {
              vm.$dialog.alert('Failed deleting' + props.item.name)
            })
            .then(() => {
              vm.loading = false
            })
        })
    },
    isJSON (str) {
      try {
        return (JSON.parse(str) && !!str)
      } catch (e) {
        return false
      }
    }
  }
}
</script>
