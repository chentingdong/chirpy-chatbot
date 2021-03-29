<template>
  <div class="container-fluid agent-manager">
    <div>
      <h1>{{title}}</h1>
      <loading v-if="loading" :loadingImage="loadingImage"></loading>
      <div class="filters container-fluid">
        <div class="row">
          <div class="col">
            <button v-b-toggle="'create-agent'" class='btn btn-success ag-button-2'>New</button>
          </div>
          <div class="col filter">
            <label>App ID &nbsp;</label>
            <input :value="filterByAppId" />
          </div>
        </div>
      </div>
      <div class="create-agent create">
        <b-collapse id="create-agent">
          <div class="container-fluid">
            <div class="row">
              <div class="col-5">
                <v-text-field v-model="newAgent.name" label="Name"></v-text-field>
                <v-text-field v-model="newAgent.app_id" label="App Id"></v-text-field>
                <v-text-field v-model="newAgent.description" label="Description"></v-text-field>
              </div>
              <div class="col-7">
                <label>Params Json</label>
                <codemirror v-model='newAgent.params'></codemirror>
              </div>
            </div>
          </div>
          <button class='btn btn-success ag-button-1' v-on:click="createAgentConfig">Create</button>
        </b-collapse>
      </div>
      <admin-table :headers='headers' :items='agents' :item-keys="itemKeys"
                   component-name="agents" default-sort="changed_on:desc" expand loading>
        <template slot="edit-template" slot-scope="data">
          <div class="container-fluid">
            <div class="row">
              <div class="col-5">
                <v-text-field v-model="data.props.item.id" label="Agent ID" disabled></v-text-field>
                <v-text-field v-model="data.props.item.name" label="Name"></v-text-field>
                <v-text-field v-model="data.props.item.description" label="Description"></v-text-field>
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
                  </button>&nbsp;
                  <button @click="showCloneDialog(data.props)"
                          class="btn btn-warning">
                    <v-icon name="clone"></v-icon>
                    <span>Clone</span>
                  </button>
                  <loading v-if="data.props.loading" class="inline"></loading>
                  <div v-if="data.props.item.locked">
                    {{data.props.item.editing_by}} is editing, read only mode. You can clone (coming at 4/30/2019).
                  </div>
                </div>
              </div>
              <div class="col-7">
                <label>Params</label>
                <codemirror v-model='data.props.item.params'></codemirror>
              </div>
            </div>
          </div>
        </template>
        <template slot='pageText' slot-scope='{ pageStart, pageStop }'>
          From {{ pageStart }} to {{ pageStop }}
        </template>
      </admin-table>
    </div>
    <modal name="clone-agent" height="auto" :scrollable="true" class="container">
      <header><h5>Clone agent {{theCloneAgent.id}}: {{theCloneAgent.name}}</h5></header>
      <main>
        <label>Check the bots to clone:</label>
        <ul>
          <li>
            <input id="selectAllBotsForClone" type="checkbox" v-model="isCloneAllBots" @click="toggleCloneAllBots()" />&nbsp;
            <label for="selectAllBotsForClone">check all</label>
          </li>
          <li v-for="(bot, index) in theCloneAgent.bots" :key="index">
            <input type="checkbox" :value="bot" v-model="theCloneBots" :id="'clone-bot-' + bot.id" @change="updateIsCloneAllBots"/>&nbsp;
            <label :for="'clone-bot-' + bot.id">{{bot.id}} - {{bot.name}}</label>
          </li>
        </ul>
      </main>
      <footer class="text-right">
        <button class="col-3 btn btn-secondary" @click="hideCloneDialog('clone-agent')">Cancel</button>&nbsp;
        <button class="col-3 btn btn-warning" @click="cloneAgent">Clone</button>
      </footer>
    </modal>
    <modal name="clone-agent-success" height="auto" :scrollable="true" class="container">
      <header>
        <h5>
          Cloned successfully
        </h5>
      </header>
      <main>
        <div>
          <label>Agent {{cloneResult.agent.id}} - {{cloneResult.agent.name}}</label>
        </div>
        <div>
          <label>Bots:</label>
          <ul>
            <li v-for="(bot, index) in cloneResult.bots" :key="'bot-' + index">
              {{bot.id}} - {{bot.name}}
            </li>
          </ul>
        </div>
        <div>
          <label>Services:</label>
          <ul>
            <li v-for="(service, index) in cloneResult.services" :key="'service-' + index">
              {{service.id}} - {{service.name}}
            </li>
          </ul>
        </div>
      </main>
      <footer class="text-right">
        <button class="col-3 btn btn-success" @click="hideCloneDialog('clone-agent-success')">Ok</button>
      </footer>
    </modal>
  </div>
</template>


<script>
import moment from 'moment'
import 'codemirror/mode/javascript/javascript.js'
import CollapsibleTable from './CollapsibleTable'
import { illusionistAPI } from '@/utils/rest-config'

const apiPath = '/api/agent'
const dateFormat = 'YYYY-MM-DD hh:mm:ss'
const newAgent = {
  'id': '',
  'name': '',
  'app_id': '',
  'description': '',
  'state': 'draft',
  'params': ''
}

export default {
  components: {
    'admin-table': CollapsibleTable
  },
  data () {
    return {
      title: 'Agents',
      headers: [
        { text: 'Agent id', value: 'id' },
        { text: 'Agent name', value: 'name' },
        { text: 'App id', value: 'app_id' },
        { text: 'State', value: 'state' },
        { text: 'Created on', value: 'created_on' },
        { text: 'Changed on', value: 'changed_on' }
      ],
      sorting: [ 'id' ],
      agents: [],
      itemKeys: [ 'id', 'name', 'app_id', 'state', 'created_on', 'changed_on' ],
      newAgent: newAgent,
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      filterByAppId: this.$route.query.app_id || '',
      theCloneAgent: {},
      theCloneBots: [],
      isCloneAllBots: false,
      cloneResult: {'agent': {}, 'bots': [], 'services': []}
    }
  },
  computed: {
    filters () {
      var vm = this
      var filters = []
      if (vm.filterByAppId !== '') {
        filters.push({
          name: 'app_id',
          op: 'eq',
          val: this.filterByAppId
        })
      }
      var filtersQuery = JSON.stringify({
        filters: filters
      })
      return filtersQuery
    }
  },
  mounted: function () {
    this.loadAgents()
  },
  methods: {
    updateAppId (event) {
      this.filterByAppId = event.target.value
      this.$router.replace({ query: { app_id: event.target.value } })
      this.loadAgents()
    },
    loadAgents: function () {
      const vm = this
      vm.loading = true

      illusionistAPI
        .get(apiPath, { params: { q: vm.filters } })
        .then((response) => {
          vm.agents = response.data.objects
          vm.agents.forEach((agent) => {
            agent[ 'params' ] = JSON.stringify(agent[ 'params' ], null, 4)
          })
          vm.newAgent[ 'params' ] = vm.agents[ 0 ][ 'params' ]
        })
        .catch((e) => {
          console.error(e)
        })
        .then(() => {
          vm.loading = false
        })
    },
    showCloneDialog: function (props) {
      const vm = this
      const agent = props.item

      vm.$modal.show('clone-agent')
      vm.theCloneAgent = agent

      vm.theCloneBots = agent.bots
      vm.isCloneAllBots = true

    },
    hideCloneDialog: function (modelName) {
      this.$modal.hide(modelName)
    },
    createAgentConfig: function () {
      const vm = this

      if (!this.isJSON(vm.newAgent.params)) {
        this.$dialog.alert('Invalid Params JSON')
        return
      }
      const newItem = Object.assign({}, vm.newAgent)
      newItem.params = JSON.parse(newItem.params)
      vm.loading = true
      illusionistAPI
        .post(apiPath, newItem)
        .then((response) => {
          vm.loading = false
          vm.newAgent = newAgent
          response.data[ 'params' ] = JSON.stringify(response.data[ 'params' ], null, 4)
          vm.agents.push(response.data)
          vm.$dialog.alert(`Successfully created agent config for : ${response.data.id}`)
        })
        .catch((e) => {
          vm.loading = false
          vm.$dialog.alert(`Failed creating agent config, error: ${e}`)
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
    },
    toggleCloneAllBots () {
      this.isCloneAllBots = !this.isCloneAllBots
      this.theCloneBots = []
      if (this.isCloneAllBots) {
        for (var key in this.theCloneAgent.bots) {
          this.theCloneBots.push(this.theCloneAgent.bots[ key ])
        }
      }
    },
    updateIsCloneAllBots () {
      this.isCloneAllBots = this.theCloneBots.length === this.theCloneAgent.bots.length
    },
    cloneAgent () {
      const vm = this
      const apiPath = '/api/1/clone_agent'
      const payload = {
        'agent_id': this.theCloneAgent.id,
        'bots': this.theCloneBots
      }

      vm.loading = true
      illusionistAPI
        .post(apiPath, payload)
        .then((response) => {
          vm.loading = false
          vm.$modal.hide('clone-agent')
          vm.cloneResult = response.data
          vm.$modal.show('clone-agent-success')
          console.log(vm.cloneResult)
        })
        .catch((e) => {
          console.warn(e)
        })
    }
  }
}
</script>

<style lang='sass'>
@import "@/assets/action.sass";

$bg-overlay: radial-gradient(farthest-corner at 90% 40%, $color-white 0, rgba(255,255,255, 0.5) 50%, $color-g4 100%);
$bg-image: url('../../assets/sunflowers.jpg');

.admin.agents
  background-image: $bg-image;

  .v--modal
    padding: 20px;
</style>
