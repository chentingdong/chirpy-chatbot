<template>
  <div class="container-fluid app-manager admin">
    <div>
      <h1>{{title}}</h1>
      <loading v-if="loading" :loadingImage="loadingImage"></loading>
      <div class="filters container-fluid">
        <div class="row">
          <div class="col">
            <button v-b-toggle="'create-app'" class='btn btn-success ag-button-2'>New</button>
          </div>
          <div class="col filter">
            <label>App type &nbsp;</label>
            <input :value="filterByAppType" @change="updateAppType($event)"/>
          </div>
          <div class="col filter">
            <label>Org ID &nbsp;</label>
            <input :value="filterByOrgId" @change="updateOrgId($event)"/>
          </div>
        </div>
      </div>
      <div class="create-app create">
        <b-collapse id="create-app">
          <div class="container-fluid">
            <div class="row">
              <div class="col-6">
                <v-text-field v-model="newApp.name" label="Name"></v-text-field>
                <v-text-field v-model="newApp.org_id" label="Org Id"></v-text-field>
                <v-text-field v-model="newApp.description" label="Description"></v-text-field>
                <v-text-field v-model="newApp.type" label="Type"></v-text-field>
                <v-text-field v-model="newApp.tag" label="Tag"></v-text-field>
              </div>
              <div class="col-6">
                <label>Settings Json</label>
                <codemirror v-model='newApp.settings'></codemirror>
              </div>
            </div>
          </div>
          <button class='btn btn-success ag-button-1' v-on:click="createApp">Create</button>
        </b-collapse>
      </div>
      <admin-table :headers='headers' :items='apps' :item-keys="itemKeys"
                   component-name="apps" default-sort="changed_on:desc" expand>
        <template slot="edit-template" slot-scope="data">
          <div class="container-fluid">
            <div class="row">
              <div class="col-4">
                <v-text-field v-model="data.props.item.id" label="App ID" disabled></v-text-field>
                <v-text-field v-model="data.props.item.org_id" label="Org ID"></v-text-field>
                <v-text-field v-model="data.props.item.name" label="Name"></v-text-field>
                <v-text-field v-model="data.props.item.type" label="Type"></v-text-field>
                <v-text-field v-model="data.props.item.description" label="Description"></v-text-field>
                <v-text-field v-model="data.props.item.tag" label="Tag"></v-text-field>
                <div class="action-buttons">
                  <button :disabled="data.props.item.locked"
                          @click="data.saveItem(data.props)"
                          class="btn btn-success">
                    <v-icon name="save"></v-icon>
                    <span>Save</span>
                  </button>&nbsp;
                  <button :disabled="data.props.item.locked"
                          @click="data.deleteItem(data.props, items)"
                          class="btn btn-danger">
                    <v-icon name="trash"></v-icon>
                    <span>Delete</span>
                  </button>
                  <div v-if="data.props.item.locked">
                    {{data.props.item.editing_by}} is editing, you are in read-only mode.
                  </div>
                </div>
              </div>
              <div class="col-4">
                <label>Params</label>
                <codemirror v-model='data.props.item.params'></codemirror>
              </div>
              <div class="col-4">
                <label>Settings</label>
                <codemirror v-model='data.props.item.settings'></codemirror>
              </div>
            </div>
          </div>
        </template>
        <!-- <template slot='pageText' slot-scope='{ pageStart, pageStop }'>
          From {{ pageStart }} to {{ pageStop }}
        </template> -->
      </admin-table>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import 'codemirror/mode/javascript/javascript.js'

import CollapsibleTable from './CollapsibleTable'
import { illusionistAPI } from '@/utils/rest-config'

const apiPath = '/api/app'
const dateFormat = 'YYYY-MM-DD hh:mm:ss'
const newApp = {
  'id': '',
  'name': '',
  'description': '',
  'type': 'answers',
  'tag': 'dev',
  'uid': '',
  'editing_by': null,
  'params': {},
  'settings': ''
}
export default {
  'name': 'app-manager',
  components: {
    'admin-table': CollapsibleTable
  },
  data () {
    return {
      title: 'Apps',
      headers: [
        { text: 'App id', value: 'id' },
        { text: 'Org id', value: 'org_id' },
        { text: 'App name', value: 'name' },
        { text: 'Type', value: 'type' },
        { text: 'UID', value: 'uid' },
        { text: 'Tag', value: 'tag' },
        { text: 'Created on', value: 'created_on' },
        { text: 'Changed on', value: 'changed_on' }
      ],
      sorting: [ 'id' ],
      apps: [],
      itemKeys: [ 'id', 'org_id', 'name', 'type', 'uid', 'tag', 'created_on', 'changed_on' ],
      newApp: newApp,
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      filterByOrgId: this.$route.query.org_id || '',
      filterByAppType: this.$route.query.app_type || 'answers'
    }
  },
  computed: {
    filters: function () {
      var vm = this
      var filters = []
      if (vm.filterByOrgId !== '') {
        filters.push({
          name: 'org_id',
          op: 'eq',
          val: vm.filterByOrgId
        })
      }
      if (vm.filterByAppType !== '') {
        filters.push({
          name: 'type',
          op: 'eq',
          val: vm.filterByAppType
        })
      }

      var filtersQuery = JSON.stringify({
        filters: filters
      })
      return filtersQuery
    }
  },
  mounted: function () {
    this.loadApps()
  },
  methods: {
    updateOrgId (event) {
      this.filterByOrgId = event.target.value
      this.$router.replace({ query: { org_id: event.target.value } })
      this.loadApps()
    },
    updateAppType (event) {
      this.filterByAppType = event.target.value
      this.$router.replace({ query: { app_type: event.target.value } })
      this.loadApps()
    },
    loadApps: function () {
      const vm = this
      vm.loading = true

      illusionistAPI
        .get(apiPath, { params: { q: vm.filters } })
        .then((response) => {
          vm.apps = response.data.objects
          vm.apps.forEach((app) => {
            app[ 'params' ] = JSON.stringify(app[ 'params' ], null, 4)
            app[ 'settings' ] = app.settings ? JSON.stringify(app[ 'settings' ], null, 4) : '{}'
          })
          // Preload new app default values with first app (41) contents.
          vm.newApp[ 'params' ] = vm.apps[ 0 ][ 'params' ]
          vm.newApp[ 'settings' ] = vm.apps[ 0 ][ 'settings' ]
        })
        .catch((e) => {
          console.error(e)
        })
        .then(() => {
          vm.loading = false
        })
    },
    createApp: function () {
      const vm = this

      if (!this.isJSON(vm.newApp.params)) {
        this.$dialog.alert('Invalid Params JSON')
        return
      }
      if (vm.newApp.settings && !this.isJSON(vm.newApp.settings)) {
        this.$dialog.alert('Invalid Settings JSON')
        return
      }
      const newItem = Object.assign({}, vm.newApp)
      newItem.params = JSON.parse(newItem.params)
      newItem.settings = newItem.settings ? JSON.parse(newItem.settings) : null
      console.log(newItem)
      vm.loading = true
      illusionistAPI
        .post(apiPath, newItem)
        .then((response) => {
          vm.loading = false
          vm.newApp = newApp
          response.data[ 'params' ] = JSON.stringify(response.data[ 'params' ], null, 4)
          response.data[ 'settings' ] = response.data.settings ? JSON.stringify(response.data[ 'settings' ], null, 4) : null
          vm.apps.push(response.data)
          vm.$dialog.alert(`Successfully created app config for : ${response.data.id}`)
        })
        .catch((e) => {
          vm.loading = false
          vm.$dialog.alert(`Failed creating app config, error: ${e}`)
        })
    },
    isJSON (str) {
      try {
        return (JSON.parse(str) && !!str)
      } catch (e) {
        return false
      }
    },
    dateFormatter (date) {
      return moment(date).format(dateFormat)
    }
  }
}
</script>

<style lang='sass'>
@import "@/assets/action.sass";

$bg-overlay: radial-gradient(farthest-corner at 90% 40%, $color-white 0, rgba(255,255,255, 0.5) 50%, $color-g4 100%);
$bg-image: url('../../assets/sunflowers.jpg');
.admin.apps
  background-image: $bg-image;
  background-size: cover;

</style>
