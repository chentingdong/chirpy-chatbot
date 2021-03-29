<template>
  <div id="bot-editor">
    <b-navbar toggleable="lg" class="container-fluid" type="dark">
      <b-navbar-brand href="#">
        <img class="site-logo" src="@/assets/logo-2.png" />
        <a class="navbar-brand" href="#">&nbsp;{{title}}</a>
      </b-navbar-brand>
      <b-navbar-toggle type="button" target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </b-navbar-toggle>
      <b-collapse id="navbarNav" is-nav>
        <b-navbar-nav>
          <b-nav-item v-on:click="readBot">
              <v-icon name="sync"></v-icon>
              <span> reload </span>
          </b-nav-item>
          <b-nav-item v-on:click="newBot">
            <v-icon name="plus"></v-icon>
            <span>new</span>
          </b-nav-item>
          <b-nav-item v-on:click="cloneBot">
            <v-icon name="copy"></v-icon>
            <span>clone</span>
          </b-nav-item>
          <b-nav-item v-on:click="saveBot" :disabled="bot.locked">
            <v-icon name="save"></v-icon>
            <span>save</span>
          </b-nav-item>
          <b-nav-item v-on:click="deleteBot">
            <v-icon name="trash"></v-icon>
            <span>delete</span>
          </b-nav-item>
          <b-nav-item v-on:click="showBotJson">
            <v-icon name="code"></v-icon>
            <span>json</span>
          </b-nav-item>
          <b-nav-item>
            <span>|</span>
          </b-nav-item>
          <b-nav-dropdown variant="default">
            <template slot="button-content" class="nav-link">
              <v-icon name="code-branch" class="rotate-90"></v-icon>
              <span class="nav-item">states</span>
            </template>
            <b-dropdown-item v-on:click="addNode('start')">start</b-dropdown-item>
            <b-dropdown-item v-on:click="addNode('end')">end</b-dropdown-item>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-item v-on:click="addNode('dialogue')">dialogue</b-dropdown-item>
            <b-dropdown-item v-on:click="addNode('action')">action</b-dropdown-item>
            <b-dropdown-item v-on:click="addNode('converse')">converse</b-dropdown-item>
          </b-nav-dropdown>
          <b-nav-item>
            <span>|</span>
          </b-nav-item>
          <b-nav-item v-on:click="fitToScreen">
            <v-icon name="expand"></v-icon>
            <span>resize</span>
          </b-nav-item>
          <b-nav-item v-bind:class="{active: showGuides}" v-on:click="guidesToggle" >
            <v-icon v-if="showGuides" name="ruler-combined"></v-icon>
            <v-icon v-else name="ruler-horizontal"></v-icon>
            <span>guides</span>
          </b-nav-item>
          <b-nav-item v-bind:class="{active: allNodesExpand}" v-on:click="nodeOpenCloseAll" >
            <v-icon v-if="allNodesExpand" name="eye-slash"></v-icon>
            <v-icon v-else name="eye"></v-icon>
            <span>expand</span>
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
    <split class="split-wrapper" @onDrag="fitToScreen">
      <splitArea :size="70" class="node-editor-wrapper">
        <div class="title" text-center>
          <h1>{{bot.name}}</h1>
          <div class="warning" v-if="bot.locked">
            {{bot.editing_by}} is editing. You are in read-only mode.
          </div>
        </div>
        <div v-if="showGuides" class="guides"></div>
        <loading v-if="loading" :loadingImage="loadingImage"></loading>
        <div id="node-editor" class="node-editor"></div>
      </splitArea>
      <splitArea :size="30">
        <b-tabs class="sidebar">
          <b-tab title="Intent" class="container-fluid">
            <intent-editor v-bind:bot="bot"></intent-editor>
          </b-tab>
          <b-tab title="Debugger" class="container-fluid">
            <bot-debugger v-bind:bot="bot" v-bind:editor="editor"></bot-debugger>
          </b-tab>
        </b-tabs>
      </splitArea>
    </split>
  </div>
</template>

<script>
import axios from 'axios'
import Rete from 'rete'
import ConnectionPlugin from 'rete-connection-plugin'
import VueRenderPlugin from 'rete-vue-render-plugin'
import ContextMenuPlugin from 'rete-context-menu-plugin'
import AreaPlugin from 'rete-area-plugin'
import ReteStart from './rete/components/start'
import ReteEnd from './rete/components/end'
import ReteDialogue from './rete/components/dialogue'
import ReteAction from './rete/components/action'
import ReteConverse from './rete/components/converse'
import ShowCodes from '@/components/ShowCodes'
import { lockMixins } from '@/utils/vue-mixin'
import { illusionistAPI } from '@/utils/rest-config'

import BotIntentEditor from '@/pages/Bot/BotIntentEditor'
import BotDebugger from '@/pages/Bot/BotDebugger'

const reteStart = new ReteStart()
const reteEnd = new ReteEnd()
const reteDialogue = new ReteDialogue()
const reteAction = new ReteAction()
const reteConverse = new ReteConverse()

export default {
  name: 'BotEditor',
  components: {
    'intent-editor': BotIntentEditor,
    'bot-debugger': BotDebugger
  },
  data () {
    return {
      title: 'Answer Designer',
      bot: this.initBot(),
      editor: {},
      allActions: [],
      messages: [],
      reteComponents: [ reteStart, reteEnd, reteDialogue, reteAction, reteConverse ],
      cmOptions: {
        tabSize: 4,
        mode: 'text/javascript',
        json: true,
        theme: 'default',
        lineNumbers: true,
        lineWrapping: true
      },
      loading: false,
      loadingImage: require('@/assets/loading-spinner-green.gif'),
      showGuides: false,
      allNodesExpand: false,
      tabActiveLifetime: 10
    }
  },
  computed: {
    botActionsWarning: function () {
      var vm = this
      var count = 0
      var actions = '<p>Make sure all these actions exist:</p>' +
        '<ul class="container-fluid">'
      Object.keys(vm.bot.workflow.nodes).forEach((id) => {
        var node = vm.bot.workflow.nodes[ id ]
        if (node.title === 'Action') {
          count++
          var actionExists = vm.allActions.indexOf(node.data.action) > 0 ? 'exists' : 'missing'
          actions += `<li class="row"><span class="col-9">${node.data.action}: </span>` +
            `<span class="col-3">${actionExists}</span></li>`
        }
      })
      actions += '</ul>'
      var ret = (count === 0) ? '' : actions
      return ret
    }
  },
  mounted () {
    this.container = document.getElementById('node-editor')
    this.editor = new Rete.NodeEditor('bot@1.0.0', this.container)
    this.editor.use(ConnectionPlugin, { curvature: 0.4 })
    this.editor.use(VueRenderPlugin)
    this.editor.use(ContextMenuPlugin)
    this.editor.use(AreaPlugin)
    this.engine = new Rete.Engine('bot@1.0.0')
    this.reteComponents.map(c => {
      this.editor.register(c)
      this.engine.register(c)
    })
    this.readBot()
    this.readBotActions()
    this.fitToScreen()
    this.preventPageReload()

    if (this.$route.fullPath === '/bot/new') {
      this.newBotNodes()
    }
  },
  watch: {
    $route (to, from) {
      if (to.path != '/bot/new' && to.params.botId !== from.params.botId) {
        this.readBot()
      }
    }
  },
  mixins: [ lockMixins ],
  methods: {
    // bot editor
    async addNode (nodeType) {
      var node = {}

      switch (nodeType) {
        case 'start':
          node = await reteStart.createNode()
          node.position = [ -300, 0 ]
          break
        case 'end':
          node = await reteEnd.createNode()
          node.position = [ 300, 0 ]
          break
        case 'dialogue':
          node = await reteDialogue.createNode()
          node.position = [ 0, 0 ]
          break
        case 'action':
          node = await reteAction.createNode()
          node.position = [ 0, 100 ]
          break
        case 'converse':
          node = await reteConverse.createNode()
          node.position = [ 0, 200 ]
          break
        default:
          console.error('node type not supported: ' + nodeType)
          break
      }
      this.editor.addNode(node)
    },
    // bot CRUD
    initBot () {
      return {
        id: null,
        name: '',
        enabled: true,
        searchable: true,
        intent: {
          domains: [ 'IT' ],
          positives: [ '' ],
          negatives: [ '' ]
        },
        workflow: {
          'groups': {},
          'id': 'bot@1.0.0',
          'nodes': {}
        },
        params: {
          engine: 'semantic_match',
          answer_not_related: 'Sorry, I do not understand, please re-phrase the question according to the context. Thank you.',
          answer_error: 'Sorry, I am not able to answer this question right now, please try again later.'
        },
        created_on: '',
        changed_on: ''
      }
    },
    newBot () {
      this.bot = this.initBot()
      this.editor.fromJSON(this.bot.workflow)
      this.newBotNodes()
    },
    newBotNodes () {
      this.addNode('start')
      this.addNode('end')
      this.addNode('dialogue')
    },
    cloneBot () {
      this.bot.id = null
      var redirect = { path: '/bot/new' }
      this.$router.push(redirect)
      this.bot.name = 'cloned.' + this.bot.name
      this.bot.agents = []
      this.bot.created_on = ''
      this.bot.changed_on = ''
    },
    readBot () {
      const vm = this
      vm.bot.id = vm.$route.params.botId
      var apiPath = '/api/bot/' + vm.bot.id
      vm.loading = true
      illusionistAPI
        .get(apiPath, {
          headers: this.requestHeaders
        })
        .then((response) => {
          vm.bot = response.data
          const currentUser = window.localStorage.getItem('username')
          vm.bot.locked = vm.bot.editing_by !== null && vm.bot.editing_by !== currentUser
          vm.editor.fromJSON(vm.bot.workflow)
        }).catch((e) => {
          console.error('failed to load bot, ' + e)
        }).then(function () {
          vm.loading = false
          vm.fitToScreen()
          vm.readBotActions()
        })
    },
    readBotActions () {
      var vm = this
      const apiPath = '/api/action?results_per_page=9999'
      illusionistAPI
        .get(apiPath)
        .then((response) => {
          if (response.status === 200) {
            response.data.objects.forEach((obj) => {
              vm.allActions.push(obj.name)
            })
          } else {
            console.warning('Failed loading actions')
          }
        })
    },
    saveBot () {
      var vm = this
      var data = vm.bot
      data.workflow = vm.editor
      data.editing_by = null
      if (vm.bot.id === null || vm.bot.id === 'new') {
        vm.createBot(data)
      } else {
        vm.updateBot(data)
      }
      delete vm.bot.locked
    },
    createBot (data) {
      const vm = this
      const apiPath = '/api/bot'
      vm.loading = true
      illusionistAPI
        .post(apiPath, data)
        .then((response) => {
          vm.handleSaveSuccess(response, 'post')
        })
        .catch((error) => {
          vm.handleSaveError(error, 'post')
        })
        .then(() => {
          vm.loading = false
        })
    },
    updateBot (data) {
      const vm = this
      const apiPath = '/api/bot/' + vm.bot.id
      vm.loading = true
      illusionistAPI
        .put(apiPath, data)
        .then((response) => {
          vm.handleSaveSuccess(response, 'put')
        })
        .catch((error) => {
          vm.handleSaveError(error, 'put')
        })
        .then(() => {
          vm.loading = false
        })
    },
    handleSaveSuccess (response, method) {
      const vm = this
      if (response.data.response === false) {
        vm.$dialog.alert(response.data.payloads.error)
      } else {
        vm.bot = response.data
        var template = `<h2 class="success">Successfully saved bot ${vm.bot.id} - ${vm.bot.name}</h2>${vm.botActionsWarning}`
        vm.$dialog.alert(template)
        if (method === 'post') {
          var redirect = { path: '/bot/' + vm.bot.id }
          vm.$router.push(redirect)
        }
      }
    },
    handleSaveError (error, method) {
      var vm = this
      if (error.code === 'ECONNABORTED') {
        return
      }
      var template
      if (method === 'post') {
        template = '<h2 class="error">Error creating new bot</h2>'
      } else {
        template = `<h2 class="error">Error saving bot ${vm.bot.id} - ${vm.bot.name}</h2>`
      }
      if (error.response.data.validation_errors) {
        var errors = error.response.data.validation_errors
        template += '<ul>'
        Object.keys(errors).forEach((key) => {
          template += `<li>${key}: ${errors[ key ]}</li>`
        })
        template += '</ul>'
        vm.$dialog.alert(template)
      }
    },
    deleteBot () {
      var vm = this
      var id = vm.bot.id
      var name = vm.bot.name
      const template = '<h2>Confirm deleting bot</h2>'
      const apiPath = '/api/bot/' + id

      vm.$dialog
        .confirm(template)
        .then(function () {
          vm.loading = true
          illusionistAPI
            .delete(apiPath)
            .then((response) => {
              if (response.status === 204) {
                vm.$dialog.alert(`Successfully deleted ${id}, ${name}`)
                var redirect = { path: '/bot/2' }
                vm.$router.push(redirect)
              } else {
                vm.$dialog.alert(`Failed delete bot ${id}, ${name}`)
              }
              vm.loading = false
            })
        })
    },
    showBotJson () {
      var vm = this
      this.$dialog.registerComponent('show-codes', ShowCodes)
      this.$dialog.alert('', {
        view: 'show-codes',
        data: vm.bot,
        readOnly: true,
        title: 'Current Bot Json',
        customClass: 'large',
        lang: 'json'
      })
    },
    // DOM controls
    fitToScreen () {
      const vm = this
      setTimeout(() => {
        AreaPlugin.zoomAt(vm.editor)
        vm.editor.view.resize()
      }, 10)
    },
    onbeforeunload (e) {
      e.returnValue = ''
    },
    preventPageReload () {
      window.addEventListener('beforeunload', this.onbeforeunload)
    },
    guidesToggle () {
      this.showGuides = !this.showGuides
    },
    nodeOpenCloseAll () {
      const vm = this
      vm.editor.nodes.forEach((node) => {
        if (this.allNodesExpand) {
          node.vueContext.$el.classList.remove('expand')
        } else {
          node.vueContext.$el.classList.add('expand')
        }
      })
      vm.allNodesExpand = !vm.allNodesExpand
    },
    isDescendant (parent, child) {
      var node = child.parentNode
      while (node !== null) {
        if (node === parent) {
          return true
        }
        node = node.parentNode
      }
      return false
    }
  }
}
</script>

<style lang="sass">
@import '@/assets/action.sass';

.title
  position: absolute;
  top: 20px;
  left: 0;
  width: 100%;
  text-align: center;
  text-transform: capitalize;
  font-size: 1rem;
  h1
    font-size: 1em;
  .warning
    font-size: 0.7em;
    margin: 10px;
    font-weight: 500;
    color: $color-warning;

.split-wrapper
  height: calc(100vh - 40px);

#BotIntentEditor,
#debugger
  min-width: 200px;

#node-editor
  height: 100%;

/* wrapper */
$bg-overlay: radial-gradient(farthest-corner at 90% 40%, $color-white 0, rgba(230, 255, 255, 0.7) 50%, $color-g4 250%);
$bg-image:  url('../../assets/neurons.jpg');
#bot-editor
  position: relative;
  background-image: $bg-overlay;
  background-size: cover;
/* nav */
.navbar
  background-color: $color-body;
  color: $color-body-bg;
  input
    background-color: $color-body;
    color: $color-body-bg;
  .nav-item:hover
    color: $color-c5;
    cursor: pointer;
  .fa-icon
    margin: 0 0.75em;

.gutter.gutter-horizontal
  background: linear-gradient(to right, $color-g4 0%, $color-g2 50%, $color-g4 100%);

/* editor */
.node-editor-wrapper
  position: relative;
  cursor: move
  .guides
    background-image: url('../../assets/grid.svg');
    background-repeat: repeat;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0.1;
    z-index: -1;

  .loading
    position: absolute;
    top: 50%;
    left: 50%;

  .node-editor
    position: relative;
    >div>div
      z-index: 1;
      &:hover
        z-index: 10;

    &::after
      content: "";
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      background-repeat: no-repeat;
      background-size: cover;
      opacity: 1;
      z-index: -1;
      width: 100%;
      height: 100%;

    .selected-node
      z-index: 10;

    .node
      border-radius: $border-radius-l;
      color: $color-body;
      overflow-y: hidden;
      z-index: 0;
      width: 250px;
      height: 41px;
      transition: height 200ms ease;
      position: relative;
      padding: 0;
      margin: -10px 0 0 -10px;

      &.expand
        width: 800px;
        height: auto;
        border-radius: $border-radius-s;
        box-shadow: 2px -2px 50px -10px rgba(0,0,0,0.2);
        opacity: 0.97;
        overflow: visible;

      &.selected
        z-index: 9;

      &.highlight
        box-shadow: 0 0 40px -2px $color-c2;

      .title,
      .input-title,
      .output-title
        display: none;

      input[name='name']
        border-color: transparent !important;
        width: 100%;

      &.start,
      &.end
        background: $color-start;
        border: 2px solid $color-start-b;
        &.expand
          width: 250px;

      &.action
        background: $color-action;
        border: 1px solid $color-action-b;
        input, textarea, .vue-codemirror, .v-select
          border: 1px solid $color-action-b;
        &.selected
          box-shadow: 0 0 50px -2px $color-c5;

      &.dialogue
        background: $color-dialogue;
        border: 2px solid $color-dialogue-b;
        input, textarea, .vue-codemirror, .v-select
          border: 1px solid $color-dialogue-b;
        &.selected
          box-shadow: 0 0 50px -2px $color-c6;

      &.converse
        background: $color-converse-b;
        border: 2px solid $color-converse-b;
        input, textarea, .vue-codemirror, .v-select
          border: 1px solid $color-converse-b;

      .control
        overflow: hidden;
        margin: 1px 15px;
      >.input,
      >.output
        position: absolute;
        z-index: 2;
        margin: 0;
        height: 0;
        width: 0;
        top: 8px;

      >.input
        width: 30px;

      >.output
        width: 100%;

      .socket
        width: 15px;
        height: 15px;
        border: 2px solid;
        margin: 0;
        &.input
          color: $color-c4;
          background-color: $color-white;

        &.output
          color: $color-c7;
          background-color: $color-white;

        &:hover
          color: $color-white;

      .node-title
        border: 0;
        background: none;
        margin: 4px 0;
        -webkit-box-shadow: none;
        text-shadow: 0 0 50px #fff;
        text-align: center;
        font-weight: bold;
        word-break: break-all;
        text-transform: capitalize;
        overflow-wrap: break-word;
        outline: none;
        resize: none;
        padding: 0;
        width: 100%;
        line-height: 1em;

      label
        display: block;
        clear: right;
        width: 100%;
        text-transform: capitalize;

      input,
      textarea,
      .vue-codemirror
        border: $color-border;
        border-radius: $border-radius-s;
        background: $color-white;

      .vue-codemirror,
      textarea
        min-height: 100px;

    .connection
      width: auto;
      height: auto;
      .main-path
        stroke: $color-start-b;
        z-index: 100;
        stroke-width: 3px;

.show-codes
  height: 100%;
  .vue-codemirror
    height: calc(100% - 120px);
    .CodeMirror
      width: 100%;
      text-align: left !important;
      line-height: 0.8rm;
      height: 100%;

/* alert style */
.dg-main-content
  max-width: 500px;

.large .dg-content-cont--floating
  -webkit-transform: none;
  transform: none;
  top: 0;
  .dg-main-content
    max-width: 90%;
    height: calc(100vh - 50px);
    overflow: scroll;
    .dg-content-body
      height: calc(100% - 70px);
      overflow: scroll;

    .dg-content-footer
      height: 70px;

</style>
