<template>
  <div class="container-fluid action-manager admin">
    <div>
      <h1>{{title}}</h1>
      <loading v-if="loading" :loadingImage="loadingImage"></loading>
      <div class="filters container-fluid">
        <div class="row">
          <div class="col">
            <button v-b-toggle="'create-action'" class='btn btn-success ag-button-2'>New</button>
          </div>
          <div class="col filter">
            <label>Action Type &nbsp;</label>
            <input v-model="filterByActionType" v-on:change="getActions()">
          </div>
        </div>
      </div>
      <div class="create-action create">
        <b-collapse id="create-action">
          <div class="container-fluid">
            <div class="row">
              <div class="col-3">
                <v-text-field v-model="newAction.name" label="Action Name"></v-text-field>
                <v-text-field v-model="newAction.action_type" label="Action Type"></v-text-field>
              </div>
              <div class="col-3">
                <v-text-field v-model="newAction.description" label="Description"></v-text-field>
                <v-text-field v-model="newAction.version" type="number" label="Version"></v-text-field>
              </div>
              <div class="col-6">
                <label>Params in JSON format</label>
                <codemirror v-model='newAction.params'></codemirror>
              </div>
            </div>
          </div>
          <button class='btn btn-success ag-button-1' v-on:click="createAction">Create</button>
        </b-collapse>
      </div>
      <admin-table :headers="headers" :items="actions" :item-keys="itemKeys" component-name="actions">
        <template slot="edit-template" slot-scope="data">
          <div class="container-fluid">
            <div class="row">
              <div class="col-6">
                <div class="row">
                  <div class="col-6">
                    <v-text-field v-model="data.props.item.name" label="Action Name"></v-text-field>
                    <v-text-field v-model="data.props.item.action_type" label="Action Type"></v-text-field>
                  </div>
                  <div class="col-6">
                    <v-text-field v-model="data.props.item.description" label="Description"></v-text-field>
                    <v-text-field v-model="data.props.item.version" type="number" label="Version"></v-text-field>
                  </div>
                </div>
                <div class="action-buttons">
                  <button :disabled="!!data.props.item.locked" v-on:click="data.saveItem(data.props)" class="btn btn-success">
                    <v-icon name="save"></v-icon>
                    <span>Save</span>
                  </button>&nbsp;
                  <button :disabled="data.props.item.locked" v-on:click="data.deleteItem(data.props)" class="btn btn-danger">
                    <v-icon name="trash"></v-icon>
                    <span>Delete</span>
                  </button>
                  <div v-if="data.props.item.locked">{{data.props.item.editing_by}} is editing, you are in read-only mode.</div>
                </div>
              </div>
              <div class="col-6">
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

const apiPath = '/api/action'

export default {
  components: {
    'admin-table': CollapsibleTable
  },
  data: function () {
    return {
      title: 'Actions',
      dialog: false,
      formTitle () {
        return this.editedIndex === -1 ? 'New Action' : 'Edit Action'
      },
      headers: [
        { text: 'Action ID', value: 'id' },
        { text: 'Action Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Version', value: 'version' },
        { text: 'Action Type', value: 'action_type' }
      ],
      itemKeys: [ 'id', 'name', 'description', 'version', 'action_type' ],
      newAction: {
        'name': '',
        'description': '',
        'version': null,
        'params': '',
        'action_type': ''
      },
      actions: [],
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      filterByActionType: this.$route.query.action_type || ''
    }
  },
  computed: {
    filters: function () {
      var vm = this
      var filters = []
      if (vm.filterByActionType !== '') {
        filters.push({
          name: 'action_type',
          op: 'like',
          val: '%' + vm.filterByActionType + '%'
        })
      }
      var filtersQuery = JSON.stringify({
        filters: filters
      })
      return filtersQuery
    }
  },
  mounted: function () {
    this.getActions()
  },
  methods: {
    getActions () {
      const vm = this
      this.loading = true
      illusionistAPI
        .get(apiPath, { params: { q: vm.filters } })
        .then((response) => {
          vm.actions = response.data.objects
          vm.actions.forEach((action) => {
            action[ 'params' ] = JSON.stringify(action[ 'params' ], null, 4)
          })
        }).catch((e) => {
          console.warn(e)
        }).then(() => {
          this.loading = false
        })
    },
    createAction: function () {
      const vm = this
      if (!this.isJSON(vm.newAction.params)) {
        this.$dialog.alert('Invalid JSON')
        return
      }
      const newItem = Object.assign({}, vm.newAction)
      newItem.params = JSON.parse(newItem.params)
      newItem.version = Number.isInteger(newItem.version) ? Number.parseInt(newItem.version) : 1
      vm.loading = true
      illusionistAPI
        .post(apiPath, newItem)
        .then((response) => {
          vm.loading = false
          vm.newAction = {
            'name': '',
            'description': '',
            'version': null,
            'params': '',
            'action_type': ''
          }
          response.data[ 'params' ] = JSON.stringify(response.data[ 'params' ], null, 4)
          vm.actions.push(response.data)
          vm.$dialog.alert(`Successfully created action for id: ${response.data.id}`)
        })
        .catch((e) => {
          vm.loading = false
          vm.$dialog.alert(`Failed creating action, error: ${e}`)
        })
    },
    isJSON (str) {
      try {
        return (JSON.parse(str) && !!str)
      } catch (e) {
        return false
      }
    },
    close () {
      this.dialog = false
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      }, 300)
    },
    save () {
      if (this.editedIndex > -1) {
        Object.assign(this.actions[ this.editedIndex ], this.editedItem)
      } else {
        this.actions.push(this.editedItem)
      }
      this.close()
    }
  }
}
</script>

<style lang="sass">
@import "@/assets/variables.scss";

$bg-overlay: radial-gradient(farthest-corner at 90% 40%, $color-white 0, rgba(0,0,0, 0.5) 50%, $color-g4 100%);
$bg-image: url('../../assets/matrix.gif');

.admin.actions
  background-image: $bg-image;

.v-dialog__content
  height: auto;
  background: $color-c4;

.v-table
  border: $border;
  td
    vertical-align: middle;

label
  margin: 10px 0;

textarea
  min-height: 100px;
</style>
