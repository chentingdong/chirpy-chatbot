<template>
  <div class="admin" :class="activeTab">
    <b-navbar toggleable="lg" type="info" variant="default" class="navbar navbar-expand-lg container-fluid">
      <b-navbar-brand href="/admin">
        <img id="logo" src="@/assets/logo-2.png"/>
      </b-navbar-brand>
      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item href="#">
            <span class="navbar-brand">{{title}}</span>
          </b-nav-item>
          <b-nav-item class="nav-link" v-for="(tab, index) in tabs" :key="index" :to="tab">
            <span :class="{active:tab.isActive}" role="tab" @click.stop.prevent="setActive(tab)">{{ tab }}</span>
          </b-nav-item>
          <b-nav-item class="nav-link">|</b-nav-item>
          <b-nav-item class="nav-link" href="/simulator/5">Simulator</b-nav-item>
          <b-nav-dropdown class="nav-link dropdown b-nav-dropdown" text="Demos">
            <b-nav-item v-for="(demo, agentId) in demos" :key="agentId" class="nav-link" :href="'/demo' + agentId" :v-html="demo"></b-nav-item>
            <b-nav-item class="nav-link" href="/demo/45" target="_blank">Adidas Wogit</b-nav-item>
            <b-nav-item class="nav-link" href="/demo/64" target="_blank">Bank of America</b-nav-item>
            <b-nav-item class="nav-link" href="/demo/76" target="_blank">Bose</b-nav-item>
          </b-nav-dropdown>
          <b-nav-dropdown class="nav-link dropdown b-nav-dropdown" text="Reporting">
            <b-dropdown-item :to="defaultMatrixUrl" target="_blank">Apps Similarity Matrix</b-dropdown-item>
          </b-nav-dropdown>
        </b-navbar-nav>
        <b-navbar-nav class="ml-auto">
          <b-nav-item @click="logout" class="nav-link">
            <span class="user">{{firstname}}&nbsp;</span>
            <v-icon name="sign-out-alt"></v-icon>&nbsp;Sign out
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
    <div class="tab-content">
      <div v-for="(tab, index) in tabs"
          :key="index"
          :class="{active: isActive(tab), show:isActive(tab)}"
          class="tab-pane fade" role="tabpanel">
        <component :is="tab" :filterByAgentId="filterByAgentId" @updateAgentIdFilter="updateAgentIdFilter"></component>
      </div>
    </div>
  </div>
</template>

<script>
import AppManager from '@/pages/Admin/AppManager'
import AgentManager from '@/pages/Admin/AgentManager'
import BotManager from '@/pages/Admin/BotManager'
import ActionManager from '@/pages/Admin/ActionManager'
import ServiceManager from '@/pages/Admin/ServiceManager'
import 'vuetify/dist/vuetify.min.css'

export default {
  components: {
    'apps': AppManager,
    'agents': AgentManager,
    'bots': BotManager,
    'actions': ActionManager,
    'services': ServiceManager
  },
  data: function () {
    return {
      title: 'Answer Designer',
      tabs: [ 'apps', 'agents', 'bots', 'actions', 'services' ],
      activeTab: this.$route.params.activeTab,
      demos: { 45: 'Adidas Wogit', 64: 'Bank of America', 76: 'Bose' },
      defaultMatrixUrl: { name: 'similarity-matrix', params: { agentId: '64' } },
      firstname: window.localStorage.getItem('first_name'),
      filterByAgentId: this.$route.query.agent_id || ''
    }
  },
  methods: {
    isActive (tab) {
      return tab === this.$route.params.activeTab
    },
    setActive (tab) {
      this.activeTab = tab
      if (tab === 'bots' || tab === 'services') {
        this.$router.replace({ params: { activeTab: tab }, query: { agent_id: this.filterByAgentId } })
      } else {
        this.$router.replace({ params: { activeTab: tab } })
      }
    },
    updateAgentIdFilter (newId) {
      console.log(newId)
      this.filterByAgentId = newId
      this.$router.replace({ query: { agent_id: newId } })
    },
    logout () {
      window.localStorage.removeItem('access_token')
      window.localStorage.removeItem('username')
      window.localStorage.removeItem('user_id')
      window.localStorage.removeItem('first_name')
      window.localStorage.removeItem('last_name')
      window.localStorage.removeItem('roles')
      this.$router.push('/login')
    }
  }
}
</script>

<style lang="sass">
@import "@/assets/variables.scss";

.admin
  background-size: cover;
  width: 100%;
  min-height: 100vh;
  height: auto;
  h1
    color: $color-g6;
    font-size: 1.5rem;
  .navbar
    background: rgba(0,0,0,0.8);
    .nav-link
      color: $color-body-bg;
    a:hover,
    .active
      color: $color-c5;
  .create
    background: $color-g6;
    padding: 10px 0;
  .vue-codemirror
    height: calc(100% - 40px);
  .CodeMirror
    height: auto;
    min-height: 100%;
  .filters
    background: $color-g5;
    padding: 10px;
    button
      margin: 0;
    input
      background: $color-g7;
      border: 1px solid $color-g4;
  .v-table-wrapper
    height: 100%;
  table.v-table
    max-height: calc(100vh - 270px);
    background: $color-body-bg;
    tr
      background: $color-g7;
      cursor: pointer;
      &.expanded
        border-bottom: 1px solid $color-g5;
        background: $color-c11;
      &.v-datatable__expand-row
        background: $color-g5;
        padding: 10px 0;
        height: 0;
        opacity: 0.95;
        transition: height 1s linear;
        .v-datatable__expand-content
          margin: 10px 0;
      td
        padding: 0 10px;
        display: table-cell;
  .v-input
    input, textarea
      color: rgba(0,0,0,.87);
      margin: 15px 0 0 0;

  .action-buttons
    cursor: pointer;
    .fa-icon
      margin-right: 1em;
  .action-buttons:hover
      color: blue;
  .ag-code
    min-height: 20em;
    flex: 0.5;
  .ag-button-1
    display: block;
    margin: 1% auto;
  .ag-button-2
    margin: 1%;
  .loading
    position: fixed;
    left: calc(50% - 15px);
    top: calc(50% + 50px);
    &.inline
      display: inline;
      left: 0;
      top: 0;
      position: relative;

</style>
