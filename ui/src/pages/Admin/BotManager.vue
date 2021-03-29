<template>
  <div class="bot-manager admin">
    <div class="container-fluid">
      <h1>{{title}}</h1>
      <loading v-if="loading" :loadingImage="loadingImage"></loading>
      <div class="filters container-fluid">
        <div class="row">
          <div class="col">
            <a class='btn btn-success ag-button-2' href="/bot/new" target="_blank">New</a>
          </div>
          <div class="col filter">
            <label>Agent ID &nbsp;</label>
            <input :value="filterByAgentId" @change="updateAgentId" />
          </div>
          <div class="col filter">
            <label>Bot Name &nbsp;</label>
            <input v-model="filterByBotName" v-on:change="loadBots">
          </div>
        </div>
      </div>
      <v-data-table class="v-table-wrapper elevation-1 table-responsive"
                    :headers="headers" :items="bots" :pagination.sync="pagination"
                    :rows-per-page-items="rowsPerPageItems" expand>
        <template slot="items" slot-scope="props">
          <tr :class="{expanded: props.expanded}" @click="expandCollapsedRow(props)" >
            <td>
              {{props.item.id}}
              <loading v-if="props.loading" class="inline"></loading>
            </td>
            <td>
              <input type="checkbox" v-model="props.item.enabled" disabled>
            </td>
            <td>
              <input type="checkbox" v-model="props.item.searchable" disabled>
            </td>
            <td>
              <router-link v-bind:to="'/bot/' + props.item.id" target="_blank">{{props.item.name}}</router-link>
            </td>
            <td>
              <div>{{props.item.description}}</div>
            </td>
            <td>
              <ul class="list-inline">
                <li class="list-inline-item" v-for="(agent, index) in props.item.agents" :key="index">{{agent}}</li>
              </ul>
            </td>
            <td>
              <ul class="list-inline">
                <li class="list-inline-item" v-for="(domain, index) in props.item.intent.domains" :key="index">
                  {{domain}}
                </li>
              </ul>
            </td>
            <td>
              <span class="test-result" :class="testResultClassName(props)">
                <v-icon name="circle"></v-icon>
              </span>
            </td>
            <td v-if="display_type==='complex'">
              <ul class="list-inline">
                <li class="list-inline-item" v-for="(positiveIntent, index) in props.item.intent.positives"
                    :key="index">{{positiveIntent}}</li>
              </ul>
            </td>
          </tr>
        </template>
        <template slot="expand" slot-scope="props">
          <div class="container ml-0 mr-0" style="max-width: 100%;">
            <div class="row edit-form">
              <div class="col">
                <v-text-field v-model="props.item.name" label="Bot Name"></v-text-field>
                <v-text-field v-model="props.item.description" label="Description"></v-text-field>
                <div class="row checkbox-holder">
                  <v-checkbox class="col-6" label="Enabled" v-model="props.item.enabled"></v-checkbox>
                  <v-checkbox class="col-6" label="Searchable" v-model="props.item.searchable"></v-checkbox>
                </div>
                <div class="action-buttons">
                  <button :disabled="props.item.locked" v-on:click="saveBot(props, $event)" class="btn btn-success">
                    <v-icon name="save"></v-icon>
                    <span>Save</span>
                  </button>
                  <button :disabled="props.item.locked" v-on:click="deleteBot(props.item, $event, props.index)" class="btn btn-danger">
                    <v-icon name="trash"></v-icon>
                    <span>Delete</span>
                  </button>
                  <button v-on:click="cloneBot(props.item, $event, props.index)" class="btn btn-warning">
                    <v-icon name="clone"></v-icon>
                    <span>Clone</span>
                  </button>
                  <div v-if="props.item.locked">{{props.item.editing_by}} is editing this bot, read-only mode. You can only clone it.</div>
                </div>
              </div>
              <div class="col">
                <div>
                  <label>Agents</label>
                  <v-select v-model="props.item.agents" :options="allAgents" label="id" multiple></v-select>
                </div>
                <div>
                  <label class="mb-0" >Domains</label>
                  <v-select v-model="props.item.intent.domains" :options="domains" multiple></v-select>
                </div>
                <div class="tags-field">
                  <label class="mb-0">Tags</label>
                  <tags-input v-model="props.item.intent.tags"></tags-input>
                </div>
              </div>
              <div class="col">
                <h3 class>
                  <span>Intents:</span>
                  <span class="col-1 clickable" v-on:click="addIntentCase('positive', props.item)">
                    <v-icon name="plus-circle"></v-icon>
                  </span>
                </h3>
                <ul class="intents">
                  <li class="row intent" v-for="(intent, index) in props.item.intent.positives" v-bind:key="index">
                    <input type="text" class="col-10" v-model="props.item.intent.positives[index]">
                    <span class="col-2 clickable" v-on:click="deleteIntentCase('positive', props.item, index)">
                      <v-icon name="times-circle"></v-icon>
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script>
import debounce from 'debounce'
import VoerroTagsInput from '@voerro/vue-tagsinput'
import { illusionistAPI } from '@/utils/rest-config'
import { lockMixins, agentMixins } from '@/utils/vue-mixin'

const botPath = '/api/bot'
const agentPath = '/api/agent'

export default {
  components: {
    'tags-input': VoerroTagsInput
  },
  props: {
    display_type: {
      type: String,
      default: 'complex',
    },
    filterByAgentId: '',
    updateAgentIdFilter: {}
  },
  data: function () {
    return {
      title: 'Bots',
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      bots: [],
      allAgents: [],
      domains: [ '', 'IT', 'HR', 'FINANCE' ],
      pagination: {
        rowsPerPage: 50
      },
      rowsPerPageItems: [ 10, 20, 50, 100, 200, 500 ],
      currentUser: window.localStorage.getItem('username'),
      filterByBotName: this.$route.query.bot_name || ''
    }
  },
  computed: {
    headers: function () {
      var headers = [
        { text: 'Bot Id', value: 'id' },
        { text: 'Enabled', value: 'enabled' },
        { text: 'Searchable', value: 'searchable' },
        { text: 'Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Agents', value: 'agents' },
        { text: 'Domains', value: 'domains' },
        { text: 'Test Passed', value: 'test_passed' }
      ]

      if (this.display_type === 'complex') {
        headers.push({ text: 'Intents', value: 'intents' })
      }

      return headers
    },
    filters: function () {
      var vm = this
      var filters = []
      if (vm.filterByAgentId !== '') {
        filters.push({
          name: 'agents',
          op: 'any',
          val: {
            name: 'id',
            op: 'eq',
            val: vm.filterByAgentId
          }
        })
      }
      if (vm.filterByBotName !== '') {
        filters.push({
          name: 'name',
          op: 'like',
          val: '%' + vm.filterByBotName + '%'
        })
      }
      var filtersQuery = JSON.stringify({
        filters: filters
      })
      return filtersQuery
    }
  },
  mounted: function () {
    const vm = this
    this.loadBots()
    this.fetchAllAgents()
  },
  watch: {
    filterByAgentId (val) {
      this.loadBots()
    }
  },
  mixins: [ lockMixins, agentMixins ],
  methods: {
    updateAgentId (event) {
      this.$router.replace({ query: { org_id: this.filterByAgentId } })
      this.$emit('updateAgentIdFilter', event.target.value)
      // this.loadBots()
    },
    expandCollapsedRow (props) {
      this.loading = true
      this.checkLocked(props, botPath).then(() => {
        this.loading = false
        if (!props.expanded) {
          props.expanded = true
          // following line does not work, why?
          // this.bots[ props.index ] = props.item
          this.bots[ props.index ].editing_by = props.item.editing_by
          this.bots[ props.index ].locked = props.item.locked
          this.lockItem(props.item, botPath)
        } else {
          props.expanded = false
          this.unlockItem(props.item, botPath)
        }
      })
    },
    loadBots () {
      const vm = this
      vm.loading = true
      illusionistAPI
        .get(botPath, { params: { q: vm.filters } })
        .then((response) => {
          var bots = response.data.objects
          vm.bots = bots
        })
        .catch(e => {
          console.warn(e)
        })
        .then(() => {
          vm.loading = false
        })
    },
    saveBot (props, $event) {
      $event.preventDefault()
      $event.stopPropagation()
      const url = botPath + '/' + props.item.id
      delete props.item.locked
      delete props.item.workflow
      delete props.item.test_passed
      this.loading = true
      illusionistAPI
        .put(url, props.item)
        .then(response => {
          const bot = response.data
          this.bots[ props.index ] = bot
          this.unlockItem(bot, botPath)
          props.expanded = false
          this.$dialog.alert('Bot ' + response.data.name + ' updated !')
        })
        .catch((e) => {
          this.$dialog.alert('Failed saving bot!')
        })
        .then(() => {
          this.loading = false
        })
    },
    deleteBot (item, event, index) {
      event.preventDefault()
      event.stopPropagation()
      const url = botPath + '/' + item.id
      this.$dialog
        .confirm('Are you sure you want to delete this bot?')
        .then(() => {
          illusionistAPI
            .delete(url)
            .then((response) => {
              this.bots.splice(index, 1)
              this.$dialog.alert('Bot deleted !')
            })
            .catch((e) => {
              this.$dialog.salert('Delete Failed !' + e)
            })
        })
    },
    cloneBot (item) {
      const vm = this
      const apiPath = '/api/1/clone_bot/' + item.id
      this.$dialog
        .confirm('Please confirm bot clone.')
        .then(() => {
          vm.loading = true
          illusionistAPI
            .post(apiPath)
            .then(response => {
              vm.loading = false
              vm.$dialog.alert(response.data.msg)
            })
        })

    },
    addIntentCase (caseType, item) {
      if (caseType === 'positive') {
        if (item.intent.positives === undefined) {
          item.intent.positives = [ '' ]
        } else {
          item.intent.positives.push('')
        }
      } else if (caseType === 'negative') {
        if (item.intent.negatives === undefined) {
          item.intent.negatives = [ '' ]
        } else {
          item.intent.negatives.push('')
        }
      } else {
        console.log('Adding new intent failed.')
      }
    },
    deleteIntentCase (caseType, item, index) {
      if (caseType === 'positive') {
        item.intent.positives.splice(index, 1)
      } else if (caseType === 'negative') {
        item.intent.negatives.splice(index, 1)
      } else {
        console.log('Adding new intent failed.')
      }
    },
    testResultClassName: function (props) {
      var test_passed = 'text-secondary'
      if (props.item.test_passed === true) {
        test_passed = 'text-success'
      }
      else if (props.item.test_passed === false) {
        test_passed = 'text-danger'
      }
      return test_passed
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/variables.scss';
$bg-overlay: radial-gradient(farthest-corner at 90% 40%, $color-white 0, rgba(255,255,255, 0.5) 50%, $color-g4 100%);
$bg-image: url('../../assets/neurons.jpg');
.admin.bots
  background-image: $bg-image;

.bot-manager
  label
    display: block;

  ul.inline
    width: 100%;
    li
      padding: 0 10px 0 0;
      margin: 0 30px 0 0;
      list-style: circle;
      box-sizing: content-box;
  .list-inline
    margin: 0;
    .list-inline-item
      list-style: circle;

  .filters
    .row label
      display: inline-block;
    .filter input
      border: $border;

  .edit-form
    input
      border: none;
      margin-bottom: 0;
    .intents
      padding: 0;
      .intent
        margin: 10px 0
      input
        border: $border;
        padding-left: 4px;
    .tags-field
      margin-top: 0 3em;
    .checkbox-holder
      padding-left: 4%;
    .btn
      margin-right: 1em;
</style>
