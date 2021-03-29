<template>
  <div class="container-fluid service-manager admin">
    <div>
      <h1>{{title}}</h1>
      <loading v-if="loading" :loadingImage="loadingImage"></loading>
      <div class="filters container-fluid">
        <div class="row">
          <div class="col">
            <button v-b-toggle="'create-service'" class='btn btn-success ag-button-2'>New</button>
          </div>
          <div class="col filter">
            <label>Agent ID &nbsp;</label>
            <input :value="filterByAgentId" @change="updateAgentId" />
          </div>
          <div class="col filter">
            <label>Bot Name &nbsp;</label>
            <input v-model="filterByServiceName" v-on:change="loadServices()">
          </div>
        </div>
      </div>
      <div class="create-service create">
        <b-collapse id="create-service">
          <div class="container-fluid">
            <div class="row">
              <div class="col-5">
                <v-text-field v-model="newService.name" label="Service Name"></v-text-field>
                <v-text-field v-model="newService.description" label="Description"></v-text-field>
                <v-text-field v-model="newService.agent_id" label="Agent ID"></v-text-field>
                <v-text-field v-model="newService.version" type="number" label="Version"></v-text-field>
              </div>
              <div class="col-7">
                <label>Params in JSON format</label>
                <codemirror v-model='newService.params'></codemirror>
              </div>
            </div>
          </div>
          <button class='btn btn-success ag-button-1' v-on:click="createService">Create</button>
        </b-collapse>
      </div>
      <admin-table :headers="headers" :items="services" :item-keys="itemKeys" component-name="services">
          <template slot="edit-template" slot-scope="data">
            <div class="container-fluid">
              <div class="row">
                <div class="col-5">
                  <v-text-field v-model="data.props.item.name" label="Service Name"></v-text-field>
                  <v-text-field v-model="data.props.item.description" label="Description"></v-text-field>
                  <v-text-field v-model="data.props.item.agent_id" label="Agent ID"></v-text-field>
                  <v-text-field v-model="data.props.item.version" type="number" label="Version"></v-text-field>
                  <div>
                    <button :disabled="data.props.item.locked" v-on:click="data.saveItem(data.props)" class="btn btn-success">
                      <v-icon name="save"></v-icon>
                      <span>Save</span>
                    </button>&nbsp;
                    <button :disabled="data.props.item.locked" v-on:click="data.deleteItem(data.props)" class="btn btn-danger">
                      <v-icon name="trash"></v-icon>
                      <span>Delete</span>
                    </button>
                    <div v-if="data.props.item.locked">Locked by {{data.props.item.editing_by}}, read-only mode</div>
                  </div>
                </div>
                <div class="col-7">
                  <label>Params in JSON format</label>
                  <codemirror v-model='data.props.item.params'></codemirror>
                </div>
              </div>
            </div>
          </template>
      </admin-table>
    </div>
  </div>
</template>

<script>
import 'codemirror/mode/javascript/javascript.js'
import CollapsibleTable from './CollapsibleTable'
import { illusionistAPI } from '@/utils/rest-config'

const apiPath = '/api/service'

export default {
  components: {
    'admin-table': CollapsibleTable
  },
  props: {
    filterByAgentId: '',
    updateAgentIdFilter: {}
  },
  data: function () {
    return {
      title: 'Services',
      dialog: false,
      formTitle () {
        return this.editedIndex === -1 ? 'New Service' : 'Edit Service'
      },
      headers: [
        { text: 'Service ID', value: 'id' },
        { text: 'Service Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Agent ID', value: 'agent_id' },
        { text: 'Version', value: 'version' }
      ],
      itemKeys: [ 'id', 'name', 'description', 'agent_id', 'version' ],
      newService: {
        'name': '',
        'description': '',
        'agent_id': '',
        'version': null,
        'params': ''
      },
      services: [],
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      filterByServiceName: this.$route.query.service_id || ''
    }
  },
  computed: {
    filters: function () {
      var vm = this
      var filters = []
      if (vm.filterByAgentId !== '') {
        filters.push({
          name: 'agent_id',
          op: 'eq',
          val: vm.filterByAgentId
        })
      }
      if (vm.filterByServiceName !== '') {
        filters.push({
          name: 'name',
          op: 'like',
          val: '%' + vm.filterByServiceName + '%'
        })
      }
      var filtersQuery = JSON.stringify({
        filters: filters
      })
      return filtersQuery
    }
  },
  mounted: function () {
    this.loadServices()
  },
  watch: {
    filterByAgentId (val) {
      this.loadServices()
    }
  },
  methods: {
    updateAgentId (event) {
      this.$router.replace({ query: { agent_id: this.filterByAgentId } })
      this.$emit('updateAgentIdFilter', event.target.value)
      // this.loadServices()
    },
    loadServices () {
      const vm = this
      this.loading = true
      illusionistAPI
        .get(apiPath, { params: { q: vm.filters } })
        .then((response) => {
          vm.services = response.data.objects
          vm.services.forEach((service) => {
            service[ 'params' ] = JSON.stringify(service[ 'params' ], null, 4)
          })
        })
        .catch((e) => {
          console.warn(e)
        })
        .then(() => {
          this.loading = false
        })
    },
    createService: function () {
      const vm = this
      if (!this.isJSON(vm.newService.params)) {
        this.$dialog.alert('Invalid JSON')
        return
      }
      const newItem = Object.assign({}, vm.newService)
      newItem.params = JSON.parse(newItem.params)
      newItem.version = Number.isInteger(newItem.version) ? Number.parseInt(newItem.version) : 1
      vm.loading = true
      illusionistAPI
        .post(apiPath, newItem)
        .then((response) => {
          vm.newService = {
            'name': '',
            'description': '',
            'agent_id': '',
            'version': null,
            'params': ''
          }
          vm.loading = false
          response.data[ 'params' ] = JSON.stringify(response.data[ 'params' ], null, 4)
          vm.services.push(response.data)
          vm.$dialog.alert(`Successfully created service for id: ${response.data.id}`)
        })
        .catch((e) => {
          vm.loading = false
          vm.$dialog.alert(`Failed creating service, error: ${e.data.message}`)
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

<style lang="sass">
@import "@/assets/variables.scss";

$bg-image: url('../../assets/hero-demo.png');

.admin.services
  background-image: $bg-image;

.v-dialog__content
  height: auto;
  background: green;

.v-table
  border: $border;
.input-fields input
  width: auto;
.service-manager .v-table td
  vertical-align: middle;
</style>
